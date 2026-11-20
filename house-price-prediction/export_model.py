"""
Check (and optionally re-save) the trained model files in models/.

    python export_model.py             loads the three files, runs one test prediction, prints versions and sizes
    python export_model.py --resave    also writes the files again (Random Forest compressed)

The files themselves are created by notebooks/house_price_prediction.ipynb (last cells).
Saved scikit-learn files load reliably only with the version that created them, so this script
prints the versions installed here; compare them with requirements.txt before deploying.
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
import sklearn

MODELS = Path(__file__).resolve().parent / "models"
FILES = ["preprocessor.pkl", "linear_regression.pkl", "random_forest.pkl"]

preprocessor = joblib.load(MODELS / "preprocessor.pkl")
lr = joblib.load(MODELS / "linear_regression.pkl")
rf = joblib.load(MODELS / "random_forest.pkl")

example = pd.DataFrame([{"location": "Whitefield", "area_type": "Super built-up Area",
                         "total_sqft": 1500, "bhk": 3, "bath": 2, "balcony": 2}])
X = preprocessor.transform(example)
print(f"scikit-learn {sklearn.__version__}, pandas {pd.__version__}")
print(f"Example (Whitefield, 1500 sqft, 3 bed, 2 bath, 2 balcony): "
      f"Linear Regression {lr.predict(X)[0]:.2f} lakhs, Random Forest {rf.predict(X)[0]:.2f} lakhs")

if "--resave" in sys.argv:
    joblib.dump(preprocessor, MODELS / "preprocessor.pkl")
    joblib.dump(lr, MODELS / "linear_regression.pkl")
    joblib.dump(rf, MODELS / "random_forest.pkl", compress=3)
    print("Files saved again.")

for name in FILES:
    print(f"  {name}: {(MODELS / name).stat().st_size / 1024:.0f} KB")
