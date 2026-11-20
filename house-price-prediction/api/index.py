"""
Prediction API for the House Price Prediction project (Flask).

Endpoints
  GET  /api/options   lists the form options (locations, area types, limits, models, offline test results)
  POST /api/predict   validates the input, applies the SAVED preprocessing pipeline and the SAVED model

The app only LOADS the saved files from ../models. It never trains anything.
The same app also serves the pages in ../public when run locally (python dev_server.py);
on Vercel those files are served from the CDN.
"""
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
PUBLIC_DIR = ROOT / "public"

app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")

# ---------------------------------------------------------------- saved files
preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")
SAVED_MODELS = {
    "linear_regression": joblib.load(MODELS_DIR / "linear_regression.pkl"),
    "random_forest": joblib.load(MODELS_DIR / "random_forest.pkl"),
}
MODEL_INFO = {
    "linear_regression": {
        "label": "Linear Regression",
        "summary": "Ordinary least squares on the preprocessed inputs. A simple, interpretable baseline.",
        "caution": "It extrapolates in a straight line, so unusual inputs can give very high or even negative prices.",
    },
    "random_forest": {
        "label": "Random Forest",
        "summary": "An average of 100 decision trees (at least 3 samples per leaf, random_state 42). It can capture non-linear effects.",
        "caution": "It fitted the training data more closely than the test data, so treat the price as an estimate.",
    },
}

# The model input features, exactly as used in training (same order as the notebook)
FEATURES = ["location", "area_type", "total_sqft", "bhk", "bath", "balcony"]

_encoder = preprocessor.named_transformers_["cat"]
_infrequent = set(_encoder.infrequent_categories_[0]) if _encoder.infrequent_categories_[0] is not None else set()
LOCATIONS = sorted(c for c in _encoder.categories_[0] if c not in _infrequent)   # locations with > 10 training houses
AREA_TYPES = list(_encoder.categories_[1])
OTHER_LOCATION = "Other"          # any place not in the list goes to the model's "rare location" group
_location_lookup = {name.lower(): name for name in LOCATIONS}

# Allowed ranges = the ranges seen in the training data
LIMITS = {"total_sqft": (300, 52272), "bhk": (1, 16), "bath": (1, 16), "balcony": (0, 3)}
TYPICAL_MAX_SQFT = 5100           # about the 99th percentile of training houses (5,097.6 sqft)
MIN_SQFT_PER_BHK = 300            # rows below this were removed during cleaning

FIELD_LABELS = {"location": "Location", "area_type": "Area type", "total_sqft": "Total area (sqft)",
                "bhk": "Bedrooms", "bath": "Bathrooms", "balcony": "Balconies"}


def load_test_results():
    """Offline test-set results written by the notebook (empty if the file is missing)."""
    path = RESULTS_DIR / "comparison.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path).set_index("Model")
    return {name: {"MAE": float(r["MAE"]), "RMSE": float(r["RMSE"]), "R2": float(r["R2"])} for name, r in df.iterrows()}


TEST_RESULTS = load_test_results()


def test_metrics(model_key):
    return TEST_RESULTS.get(MODEL_INFO[model_key]["label"])


# ---------------------------------------------------------------- helpers
def text(value):
    return "" if value is None else str(value).strip()


def format_inr(lakhs):
    """85.4 lakhs -> '85,40,000' (Indian digit grouping)."""
    rupees = int(round(lakhs * 100000))
    s = str(abs(rupees))
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if rupees < 0 else "") + s


def parse_number(raw, label, lo, hi, integer=False, required=True):
    raw = text(raw)
    if raw == "":
        return (None, f"Enter the {label.lower()}.") if required else (None, None)
    try:
        value = float(raw)
    except ValueError:
        return None, f"{label} must be a number, for example {lo}."
    if not math.isfinite(value):
        return None, f"{label} must be a real number."
    if integer and value != int(value):
        return None, f"{label} must be a whole number."
    if value < lo or value > hi:
        return None, f"{label} must be between {lo:,} and {hi:,}."
    return (int(value) if integer else value), None


def validate(data):
    """Check the raw values. Returns (clean_values, errors, warnings)."""
    errors, warnings, clean = {}, [], {}

    raw_loc = text(data.get("location"))
    if not raw_loc:
        errors["location"] = "Choose a location, or type Other if yours is not listed."
    elif raw_loc.lower() == OTHER_LOCATION.lower():
        clean["location"] = OTHER_LOCATION
    elif raw_loc.lower() in _location_lookup:
        clean["location"] = _location_lookup[raw_loc.lower()]
    else:
        errors["location"] = f"\u201c{raw_loc}\u201d is not in the location list. Pick one from the suggestions, or type Other."

    raw_area = text(data.get("area_type"))
    if not raw_area:
        errors["area_type"] = "Choose an area type."
    elif raw_area not in AREA_TYPES:
        errors["area_type"] = "Choose one of the listed area types."
    else:
        clean["area_type"] = raw_area

    for name, integer, required in [("total_sqft", False, True), ("bhk", True, True), ("bath", True, True), ("balcony", True, False)]:
        value, err = parse_number(data.get(name), FIELD_LABELS[name], *LIMITS[name], integer=integer, required=required)
        if err:
            errors[name] = err
        else:
            clean[name] = value

    model_key = text(data.get("model"))
    if model_key not in SAVED_MODELS:
        errors["model"] = "Choose Linear Regression or Random Forest."
    else:
        clean["model"] = model_key

    if not errors:   # valid input, but outside what the models mostly saw in training
        if clean["total_sqft"] > TYPICAL_MAX_SQFT:
            warnings.append(f"A total area above {TYPICAL_MAX_SQFT:,} sqft is larger than about 99% of the training houses, "
                            "so the prediction is less reliable.")
        if clean["total_sqft"] / clean["bhk"] < MIN_SQFT_PER_BHK:
            warnings.append(f"Under {MIN_SQFT_PER_BHK} sqft per bedroom is outside the data the models were trained on "
                            "(such rows were removed during cleaning).")
        if clean["bath"] > clean["bhk"] + 2:
            warnings.append("More than two extra bathrooms compared with bedrooms is outside the data the models were trained on.")
    return clean, errors, warnings


def predict_price(clean):
    """Apply the SAVED preprocessing pipeline, then the SAVED model. Returns the price in lakhs."""
    row = {f: clean.get(f) for f in FEATURES}
    if row["balcony"] is None:
        row["balcony"] = np.nan                       # the pipeline fills it with the training median
    X = preprocessor.transform(pd.DataFrame([row], columns=FEATURES))
    return float(SAVED_MODELS[clean["model"]].predict(X)[0])


def input_summary(clean):
    area = clean["total_sqft"]
    area_text = f"{area:,.0f}" if float(area).is_integer() else f"{area:,}"
    return [
        {"label": FIELD_LABELS["location"], "value": clean["location"] if clean["location"] != OTHER_LOCATION else "Other (not in the list)"},
        {"label": FIELD_LABELS["area_type"], "value": clean["area_type"]},
        {"label": FIELD_LABELS["total_sqft"], "value": area_text},
        {"label": FIELD_LABELS["bhk"], "value": str(clean["bhk"])},
        {"label": FIELD_LABELS["bath"], "value": str(clean["bath"])},
        {"label": FIELD_LABELS["balcony"],
         "value": str(clean["balcony"]) if clean.get("balcony") is not None else "Not given (the model uses the typical value, 2)"},
    ]


# ---------------------------------------------------------------- API
@app.get("/api/options")
def api_options():
    return jsonify(
        locations=LOCATIONS, area_types=AREA_TYPES, other=OTHER_LOCATION,
        limits={k: list(v) for k, v in LIMITS.items()}, min_sqft_per_bhk=MIN_SQFT_PER_BHK,
        models=[{"key": k, "label": v["label"], "summary": v["summary"], "caution": v["caution"], "test": test_metrics(k)}
                for k, v in MODEL_INFO.items()])


@app.post("/api/predict")
def api_predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = request.form.to_dict()
    clean, errors, warnings = validate(data)
    if errors:
        return jsonify(ok=False, errors=errors), 400
    lakhs = predict_price(clean)
    info = MODEL_INFO[clean["model"]]
    if lakhs <= 0:
        return jsonify(ok=False, errors={"model": f"{info['label']} returned a price below zero for these inputs, which is not a valid price. "
                                                   "Try the other model or different values."}), 422
    return jsonify(ok=True, model_key=clean["model"], model=info["label"],
                   predicted_price_lakhs=round(lakhs, 2), predicted_price_inr=int(round(lakhs * 100000)),
                   predicted_price_text=f"\u20b9{format_inr(lakhs)}", warnings=warnings, summary=input_summary(clean),
                   model_info={"summary": info["summary"], "caution": info["caution"]}, test_metrics=test_metrics(clean["model"]))


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify(ok=False, errors={"request": "Unknown API endpoint."}), 404
    return send_from_directory(PUBLIC_DIR, "index.html"), 404


# ---------------------------------------------------------------- pages (local run only; Vercel serves public/ from the CDN)
@app.get("/")
def page_home():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.get("/predict")
def page_predict():
    return send_from_directory(PUBLIC_DIR, "predict.html")


@app.get("/result")
def page_result():
    return send_from_directory(PUBLIC_DIR, "result.html")
