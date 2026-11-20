# Web application test results

Every output below was returned by the running app (`python dev_server.py`) through `POST /api/predict`. Nothing was typed in by hand.
Price unit: lakhs of INR as given in the dataset description; shown as rupees with Indian digit grouping.

**Result: 31 of 31 prediction tests passed.** A pass means the outcome matched what was expected before running the test.

| # | Group | Test | Input | Model | HTTP | Actual output | Status |
|---|---|---|---|---|---|---|---|
| 1 | Valid | Valid property A | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | linear_regression | 200 | ₹77,35,414 | Pass |
| 2 | Valid | Valid property A | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | random_forest | 200 | ₹95,27,493 | Pass |
| 3 | Valid | Different property B (Malleshwaram, Plot Area) | location='Malleshwaram', area_type='Plot Area', total_sqft='1800', bhk='3', bath='3', balcony='1' | linear_regression | 200 | ₹4,14,97,061 | Pass |
| 4 | Valid | Different property B (Malleshwaram, Plot Area) | location='Malleshwaram', area_type='Plot Area', total_sqft='1800', bhk='3', bath='3', balcony='1' | random_forest | 200 | ₹1,43,89,222 | Pass |
| 5 | Combination | Small flat, Carpet Area, 1 bedroom | location='Indira Nagar', area_type='Carpet Area', total_sqft='650', bhk='1', bath='1', balcony='0' | random_forest | 200 | ₹38,07,694 | Pass |
| 6 | Combination | Balcony left blank | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='' | random_forest | 200 | ₹95,27,493 | Pass |
| 7 | Combination | Location typed in lower case | location='whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | random_forest | 200 | ₹95,27,493 | Pass |
| 8 | Combination | Location not in list (Other) | location='Other', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | random_forest | 200 | ₹84,87,744 | Pass |
| 9 | Extreme valid | Very large area: 50,000 sqft, 9 bedrooms | location='Whitefield', area_type='Super built-up Area', total_sqft='50000', bhk='9', bath='8', balcony='2' | random_forest | 200 | ₹10,59,80,972 [Warning shown] | Pass |
| 10 | Extreme valid | Very large area: 50,000 sqft, 9 bedrooms | location='Whitefield', area_type='Super built-up Area', total_sqft='50000', bhk='9', bath='8', balcony='2' | linear_regression | 200 | ₹29,21,22,760 [Warning shown] | Pass |
| 11 | Extreme valid | Smallest area: 300 sqft, 1 bedroom | location='Whitefield', area_type='Super built-up Area', total_sqft='300', bhk='1', bath='1', balcony='0' | random_forest | 200 | ₹28,04,514 | Pass |
| 12 | Extreme valid | Largest counts: 16 bedrooms, 16 bathrooms | location='Whitefield', area_type='Super built-up Area', total_sqft='12000', bhk='16', bath='16', balcony='2' | random_forest | 200 | ₹11,34,99,843 [Warning shown] | Pass |
| 13 | Missing input | Nothing entered | (empty) | random_forest | 400 | Choose an area type. / Enter the bathrooms. / Enter the bedrooms. / Choose a location, or type Other if yours is not listed. / Enter the total area (sqft). | Pass |
| 14 | Missing input | Location empty | location='', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | random_forest | 400 | Choose a location, or type Other if yours is not listed. | Pass |
| 15 | Missing input | Total area empty | location='Whitefield', area_type='Super built-up Area', total_sqft='', bhk='3', bath='2', balcony='2' | random_forest | 400 | Enter the total area (sqft). | Pass |
| 16 | Missing input | Model not chosen | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | - | 400 | Choose Linear Regression or Random Forest. | Pass |
| 17 | Invalid number | Area is text (abc) | location='Whitefield', area_type='Super built-up Area', total_sqft='abc', bhk='3', bath='2', balcony='2' | random_forest | 400 | Total area (sqft) must be a number, for example 300. | Pass |
| 18 | Invalid number | Area is nan | location='Whitefield', area_type='Super built-up Area', total_sqft='nan', bhk='3', bath='2', balcony='2' | random_forest | 400 | Total area (sqft) must be a real number. | Pass |
| 19 | Invalid number | Area is negative | location='Whitefield', area_type='Super built-up Area', total_sqft='-500', bhk='3', bath='2', balcony='2' | random_forest | 400 | Total area (sqft) must be between 300 and 52,272. | Pass |
| 20 | Invalid number | Area below minimum (100 sqft) | location='Whitefield', area_type='Super built-up Area', total_sqft='100', bhk='3', bath='2', balcony='2' | random_forest | 400 | Total area (sqft) must be between 300 and 52,272. | Pass |
| 21 | Invalid number | Area above maximum (99,999 sqft) | location='Whitefield', area_type='Super built-up Area', total_sqft='99999', bhk='3', bath='2', balcony='2' | random_forest | 400 | Total area (sqft) must be between 300 and 52,272. | Pass |
| 22 | Invalid number | Bedrooms is 2.5 | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='2.5', bath='2', balcony='2' | random_forest | 400 | Bedrooms must be a whole number. | Pass |
| 23 | Invalid number | Bedrooms is 0 | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='0', bath='2', balcony='2' | random_forest | 400 | Bedrooms must be between 1 and 16. | Pass |
| 24 | Invalid number | Bathrooms is 20 | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='20', balcony='2' | random_forest | 400 | Bathrooms must be between 1 and 16. | Pass |
| 25 | Invalid number | Balconies is 7 | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='7' | random_forest | 400 | Balconies must be between 0 and 3. | Pass |
| 26 | Invalid category | Unknown location (Atlantis) | location='Atlantis', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | random_forest | 400 | “Atlantis” is not in the location list. Pick one from the suggestions, or type Other. | Pass |
| 27 | Invalid category | Unknown area type | location='Whitefield', area_type='Penthouse Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | random_forest | 400 | Choose one of the listed area types. | Pass |
| 28 | Invalid category | Unknown model (xgboost) | location='Whitefield', area_type='Super built-up Area', total_sqft='1500', bhk='3', bath='2', balcony='2' | xgboost | 400 | Choose Linear Regression or Random Forest. | Pass |
| 29 | Warning | Valid but unusual: 300 sqft with 4 bedrooms | location='Whitefield', area_type='Super built-up Area', total_sqft='300', bhk='4', bath='2', balcony='2' | random_forest | 200 | ₹57,51,912 [Warning shown] | Pass |
| 30 | Model limit | Linear Regression would give a negative price (Chikka Tirupathi, 300 sqft) | location='Chikka Tirupathi', area_type='Built-up Area', total_sqft='300', bhk='1', bath='1', balcony='0' | linear_regression | 422 | Linear Regression returned a price below zero for these inputs, which is not a valid price. Try the other model or different values. | Pass |
| 31 | Model limit | Same property with Random Forest | location='Chikka Tirupathi', area_type='Built-up Area', total_sqft='300', bhk='1', bath='1', balcony='0' | random_forest | 200 | ₹39,75,430 | Pass |

## Pages and options

| Path | HTTP |
|---|---|
| `/` | 200 |
| `/predict.html` | 200 |
| `/result.html` | 200 |
| `/style.css` | 200 |
| `/app.js` | 200 |
| `/api/options` | 200 |
| `/api/nothing-here` (unknown endpoint) | 404 (JSON error) |

**Pages and options: all as expected.**
