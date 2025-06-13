# **PT1: Data Cleaning of UFO Sightings Dataset**  

### **Project Goal**
The goal of this project is to **explore, clean, and analyze** UFO sightings from the [Kaggle](https://www.kaggle.com/datasets/NUFORC/ufo-sightings) Dataset using Python. This is **Part 1**, focusing entirely on **data cleaning**—an essential step in preparing data for meaningful insights. The objective is to become comfortable with Python's data analytics workflow and master various data cleaning techniques.  

### **Dataset Overview (`ufo_dataset.csv`)**
The dataset contains information about UFO sightings, including:  
- `datetime` – Timestamp of sighting  
- `city` – Location where sighting occurred  
- `state` – State where sighting occurred  
- `country` – Country where sighting occurred  
- `shape` – UFO shape reported  
- `duration_seconds` – Duration of sighting in seconds  
- `duration_hours_min` – Duration formatted in hours/minutes  
- `comments` – Description of the sighting  
- `date_posted` – Date the sighting was publicly reported  
- `latitude` / `longitude` – Geographic coordinates of sighting  

---

## **Data Cleaning Steps**
1. **Loading the Dataset**  
2. **Cleaning & Preprocessing**  
   - Handling column names and duplicates  
   - Resolving **missing city/state values** using **GeoPy** & **Nominatim API**  
   - Removing **parentheses in state values**  
   - Standardizing **date formats**  
   - Processing **duration columns (seconds → hours/minutes)**  
   - Cleaning **HTML entities** and **non-ASCII characters** in comments  
   - **Attempting state abbreviation standardization (but required a global dictionary due to international data)**  

3. **Saving the cleaned dataset for analysis**  

---

## **Key Learnings**
Data cleaning is **not a straightforward process**—it requires multiple tools, methods, and approaches to refine raw data into a usable format. Through this project, I learned to:  
✔ **Use GeoPy & Nominatim API** to enrich location data via reverse geocoding  
✔ **Handle text anomalies** by removing HTML entities (`&#44;` → `,`)  
✔ **Normalize Unicode characters** to clean non-standard text  
✔ **Standardize duration columns**, converting seconds to readable formats  
✔ **Validate cleaned data**, ensuring minimal record loss while improving quality  

---

## **Challenges & Limitations**
While significant improvements were made, some challenges remained unresolved due to dataset constraints lack of expirience or technical knowledge:  
- **State abbreviations couldn't be standardized** because Nominatim & GeoPy returned full state names (e.g., "Wales"), requiring a dictionary for global abbreviations (not just U.S. states, but entire world.).  
- Some **records were lost due to incomplete or incorrectly entered dates** that could not be recovered.  
- **Maritime sightings were removed**, as they lacked consistent geographic identifiers and will not be required.  

---

## **Dataset Comparison Before & After Cleaning**
| Metric  | Count |
|---------|-------|
| Original row count | **80,332** |
| Cleaned row count  | **79,561** |
| Records lost | **771** |
| **Percentage lost** | **0.96%** |

This careful validation ensures that **removals were intentional**, improving dataset reliability while preserving valuable insights.  

---

## **Next Steps**
This is **only Part 1**—the next phase will focus on **exploratory data analysis (EDA)** and **visualization** using Python.  