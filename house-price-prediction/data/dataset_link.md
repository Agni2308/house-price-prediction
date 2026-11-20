# Dataset: Bengaluru House Price Data

All statistics below were computed directly from the file `Bengaluru_House_Data.csv` (938,020 bytes) used in this project.

## Source
- Name: Bengaluru House Price Data
- Platform: Kaggle
- URL: https://www.kaggle.com/datasets/amitabhajoy/bengaluru-house-price-data
- Licence: **TO BE FILLED** from the Kaggle dataset page (not verified)
- Price unit: lakhs of INR, per secondary descriptions of this dataset. The CSV itself carries no unit, so confirm on the Kaggle page.

## Shape
- Rows: 13,320
- Columns: 9

## Columns
| Column | Type (as loaded) | Role | Unique values | Missing |
|---|---|---|---|---|
| area_type | text | categorical feature | 4 | 0 |
| availability | text | categorical (81 values, mostly "Ready To Move" or a month) | 81 | 0 |
| location | text | categorical feature | 1,305 raw (1,294 after trimming spaces) | 1 |
| size | text (e.g. "2 BHK", "4 Bedroom") | needs parsing into a number | 31 | 16 |
| society | text | categorical, mostly missing | 2,688 | 5,502 (41.31%) |
| total_sqft | text | numeric, needs cleaning | 2,117 | 0 |
| bath | float | numerical feature | 19 | 73 |
| balcony | float | numerical feature | 4 | 609 (4.57%) |
| price | float | **target** | 1,994 | 0 |

## Target variable
`price`: min 8, 25% 50, median 72, mean 112.57, 75% 120, max 3,600 (right-skewed).

## Data quality findings
- Full-row duplicates: **529**. Duplicates on the modelling columns (area_type, location, size, total_sqft, bath, balcony, price): 691. To be decided in preprocessing.
- Rows with a missing location, size, bath or balcony: 610.
- `total_sqft` is not purely numeric: 247 values fail numeric conversion. 201 are ranges such as "2100 - 2850". The rest use other units (SqMeter 17, SqYards 15, Acres 8, Cents 2, Guntha 2, Perch 1, Grounds 1).
- Numeric `total_sqft` range: 1 to 52,272 (median 1,275).
- `size` mixes "BHK" and "Bedroom" labels. Parsed bedroom count ranges from 1 to 43. 26 rows have 10 or more bedrooms.
- `bath` ranges up to 40; 16 rows have bath greater than bedrooms + 2.
- 744 rows have under 300 sqft per bedroom (suspicious).
- `location` is high-cardinality: 1,053 of 1,294 locations have 10 or fewer rows (2,885 rows in total), and 473 appear only once.
- `availability`: 10,581 rows are "Ready To Move", 2,739 hold a date-like label.

## Limitations
- Single city (Bengaluru), so results do not generalise to other cities.
- No parking, property age or number of floors.
- Listing prices, not necessarily final sale prices.
- No listing date, so price levels cannot be tied to a time period.
- Heavy missingness in `society`, inconsistent units in `total_sqft`, and clear outliers.

## How to get the data for this project
1. Download `Bengaluru_House_Data.csv` from the Kaggle link above (a free Kaggle login is needed).
2. Put the file in this `data/` folder, so the path is `data/Bengaluru_House_Data.csv`.
3. Run the notebook in `notebooks/`.

The CSV is not stored in this repository (see `.gitignore`) because the dataset licence has not been confirmed.
