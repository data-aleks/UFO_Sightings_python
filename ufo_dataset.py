import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from tqdm import tqdm

# This python script is to allow me to test the reverse geolocation on a local machine

# --- Initialize Nominatim geolocator ---
# IMPORTANT: Replace "ufo_dataset_project_your_name_or_email" with a unique identifier
geolocator = Nominatim(user_agent="ufo_dataset_project_your_name_or_email")

# --- Geocoding Function (MODIFIED) ---
def get_location_details_smart(row):
    """
    Attempts to reverse geocode missing city, state, or country values using latitude/longitude.
    Only proceeds if latitude and longitude are available and at least one of city, state, or country is missing.
    Prioritizes country_code for country and searches for common administrative divisions for state.
    """
    current_city = row['city'] if pd.notna(row['city']) else None
    current_country = row['country'] if pd.notna(row['country']) else None
    current_state = row['state'] if pd.notna(row['state']) else None
    current_latitude = row['latitude'] if pd.notna(row['latitude']) else None
    current_longitude = row['longitude'] if pd.notna(row['longitude']) else None

    result_city = current_city
    result_state = current_state
    result_country = current_country # This will hold the abbreviation if found

    if (current_latitude is not None and current_longitude is not None and
        (current_city is None or current_state is None or current_country is None)):

        try:
            time.sleep(1) # Add a delay to comply with Nominatim's fair usage policy.
            location = geolocator.reverse(f"{current_latitude}, {current_longitude}", language='en')

            if location and location.raw and 'address' in location.raw:
                address = location.raw['address']

                # --- Handle City ---
                if result_city is None:
                    # Prioritize common city-like keys
                    result_city = address.get('city') or \
                                  address.get('town') or \
                                  address.get('village') or \
                                  address.get('hamlet')

                # --- Handle State (or equivalent) ---
                if result_state is None:
                    # Prioritize common administrative divisions for 'state'
                    result_state = address.get('state') or \
                                   address.get('province') or \
                                   address.get('region') or \
                                   address.get('county') # county might be too granular for 'state', but can be a fallback

                # --- Handle Country (with Abbreviation) ---
                if result_country is None:
                    # Prefer country_code (e.g., 'US', 'GB') if available, otherwise use full 'country' name.
                    # Convert to uppercase for consistency.
                    country_info = address.get('country_code', address.get('country'))
                    if country_info:
                        result_country = country_info.upper()

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            # print(f"Error reverse geocoding {current_latitude}, {current_longitude}: {e}")
            pass
        except Exception as e:
            # print(f"An unexpected error occurred during reverse geocoding {current_latitude}, {current_longitude}: {e}")
            pass

    return {'city': result_city, 'state': result_state, 'country': result_country}

# --- Rest of your existing code (no changes needed here for the logic) ---

# Load your dataset
df = pd.read_csv('./dataset/ufo_dataset.csv')
df_processing = df.copy()

# Rename columns
df_processing.rename(columns={
    'duration (seconds)': 'duration_seconds',
    'duration (hours/min)': 'duration_hours_min',
    'date posted': 'date_posted',
    'longitude ': 'longitude'
}, inplace=True)

# Identify records for geocoding
rows_to_process_mask = (df_processing['latitude'].notna()) & \
                       (df_processing['longitude'].notna()) & \
                       ((df_processing['city'].isna()) | \
                        (df_processing['state'].isna()) | \
                        (df_processing['country'].isna()))

df_needs_geocoding = df_processing[rows_to_process_mask].copy()

# Create the TEST SAMPLE and store its original indices
df_test_sample = df_needs_geocoding.sample(n=500, random_state=42)
test_sample_indices = df_test_sample.index.tolist()

# --- Perform Geocoding on the Test Sample ---
total_records_to_process = len(df_test_sample)
successfully_geocoded_count = 0

print(f"**Identified {total_records_to_process} records for potential reverse geocoding in test sample.**\n")

if total_records_to_process > 0:
    pbar = tqdm(df_test_sample.iterrows(), total=total_records_to_process,
                desc=f"Geocoding (Filled: 0/{total_records_to_process}, Remaining: {total_records_to_process})")

    for index, row in pbar:
        original_city = df_processing.loc[index, 'city']
        original_state = df_processing.loc[index, 'state']
        original_country = df_processing.loc[index, 'country']

        geocoded_values = get_location_details_smart(row)

        # Update df_processing directly
        df_processing.loc[index, 'city'] = geocoded_values['city']
        df_processing.loc[index, 'state'] = geocoded_values['state']
        df_processing.loc[index, 'country'] = geocoded_values['country']

        if (pd.isna(original_city) and pd.notna(df_processing.loc[index, 'city'])) or \
           (pd.isna(original_state) and pd.notna(df_processing.loc[index, 'state'])) or \
           (pd.isna(original_country) and pd.notna(df_processing.loc[index, 'country'])):
            successfully_geocoded_count += 1

        pbar.set_description(f"Geocoding (Filled: {successfully_geocoded_count}/{total_records_to_process}, Remaining: {total_records_to_process - successfully_geocoded_count})")
else:
    print("No records found that meet the criteria for reverse geocoding (i.e., having lat/lon but missing city/state/country).")

print("\n" + "="*50 + "\n")
print("--- Updated DataFrame (Full df_processing) ---")
print(df_processing.head()) # Just showing head for brevity
print(f"\n**Summary:** Successfully filled at least one missing field (city/state/country) for **{successfully_geocoded_count}** records out of **{total_records_to_process}** that met the geocoding criteria in the test sample.")

# --- Save the UPDATED test records from df_processing ---
df_updated_test_records = df_processing.loc[test_sample_indices].copy()

# For comparison, get the original records from the *initial* df
df_test_sample_original = df.loc[test_sample_indices].copy()

# Combine them for easy comparison (optional but good for testing)
df_comparison = pd.concat([
    df_test_sample_original.add_suffix('_original'),
    df_updated_test_records.add_suffix('_updated')
], axis=1)


# Save the updated test records to a CSV
df_updated_test_records.to_csv('./dataset/geocoded_test_sample_updated.csv', index=True)
print(f"\nSaved updated test records to: ./dataset/geocoded_test_sample_updated.csv")

# Optionally save the comparison DataFrame for detailed review
df_comparison.to_csv('./dataset/geocoded_test_sample_comparison.csv', index=True)
print(f"Saved comparison of original vs. updated test records to: ./dataset/geocoded_test_sample_comparison.csv")