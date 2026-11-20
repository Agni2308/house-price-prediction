"""
Sends test inputs to the RUNNING app and records the real responses.
Start the app first (python dev_server.py), then from the project root:   python tests/run_tests.py
Writes results/web_app_tests.md
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:5000"
OUT = Path(__file__).resolve().parent.parent / "results" / "web_app_tests.md"


def request(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


base = {"location": "Whitefield", "area_type": "Super built-up Area", "total_sqft": "1500", "bhk": "3", "bath": "2", "balcony": "2"}
def case(**kw): d = dict(base); d.update(kw); return d

# (group, description, input, expected)  expected: "ok" = a price, "error" = friendly validation error (HTTP 400/422)
tests = [
 ("Valid", "Valid property A", case(model="linear_regression"), "ok"),
 ("Valid", "Valid property A", case(model="random_forest"), "ok"),
 ("Valid", "Different property B (Malleshwaram, Plot Area)", case(location="Malleshwaram", area_type="Plot Area", total_sqft="1800", bhk="3", bath="3", balcony="1", model="linear_regression"), "ok"),
 ("Valid", "Different property B (Malleshwaram, Plot Area)", case(location="Malleshwaram", area_type="Plot Area", total_sqft="1800", bhk="3", bath="3", balcony="1", model="random_forest"), "ok"),
 ("Combination", "Small flat, Carpet Area, 1 bedroom", case(location="Indira Nagar", area_type="Carpet Area", total_sqft="650", bhk="1", bath="1", balcony="0", model="random_forest"), "ok"),
 ("Combination", "Balcony left blank", case(balcony="", model="random_forest"), "ok"),
 ("Combination", "Location typed in lower case", case(location="whitefield", model="random_forest"), "ok"),
 ("Combination", "Location not in list (Other)", case(location="Other", model="random_forest"), "ok"),
 ("Extreme valid", "Very large area: 50,000 sqft, 9 bedrooms", case(total_sqft="50000", bhk="9", bath="8", model="random_forest"), "ok"),
 ("Extreme valid", "Very large area: 50,000 sqft, 9 bedrooms", case(total_sqft="50000", bhk="9", bath="8", model="linear_regression"), "ok"),
 ("Extreme valid", "Smallest area: 300 sqft, 1 bedroom", case(total_sqft="300", bhk="1", bath="1", balcony="0", model="random_forest"), "ok"),
 ("Extreme valid", "Largest counts: 16 bedrooms, 16 bathrooms", case(total_sqft="12000", bhk="16", bath="16", model="random_forest"), "ok"),
 ("Missing input", "Nothing entered", {"model": "random_forest"}, "error"),
 ("Missing input", "Location empty", case(location="", model="random_forest"), "error"),
 ("Missing input", "Total area empty", case(total_sqft="", model="random_forest"), "error"),
 ("Missing input", "Model not chosen", case(), "error"),
 ("Invalid number", "Area is text (abc)", case(total_sqft="abc", model="random_forest"), "error"),
 ("Invalid number", "Area is nan", case(total_sqft="nan", model="random_forest"), "error"),
 ("Invalid number", "Area is negative", case(total_sqft="-500", model="random_forest"), "error"),
 ("Invalid number", "Area below minimum (100 sqft)", case(total_sqft="100", model="random_forest"), "error"),
 ("Invalid number", "Area above maximum (99,999 sqft)", case(total_sqft="99999", model="random_forest"), "error"),
 ("Invalid number", "Bedrooms is 2.5", case(bhk="2.5", model="random_forest"), "error"),
 ("Invalid number", "Bedrooms is 0", case(bhk="0", model="random_forest"), "error"),
 ("Invalid number", "Bathrooms is 20", case(bath="20", model="random_forest"), "error"),
 ("Invalid number", "Balconies is 7", case(balcony="7", model="random_forest"), "error"),
 ("Invalid category", "Unknown location (Atlantis)", case(location="Atlantis", model="random_forest"), "error"),
 ("Invalid category", "Unknown area type", case(area_type="Penthouse Area", model="random_forest"), "error"),
 ("Invalid category", "Unknown model (xgboost)", case(model="xgboost"), "error"),
 ("Warning", "Valid but unusual: 300 sqft with 4 bedrooms", case(total_sqft="300", bhk="4", bath="2", model="random_forest"), "ok"),
 ("Model limit", "Linear Regression would give a negative price (Chikka Tirupathi, 300 sqft)", case(location="Chikka Tirupathi", area_type="Built-up Area", total_sqft="300", bhk="1", bath="1", balcony="0", model="linear_regression"), "error"),
 ("Model limit", "Same property with Random Forest", case(location="Chikka Tirupathi", area_type="Built-up Area", total_sqft="300", bhk="1", bath="1", balcony="0", model="random_forest"), "ok"),
]

rows, passed = [], 0
for group, desc, data, expected in tests:
    status, raw = request("POST", "/api/predict", data)
    try:
        body = json.loads(raw)
    except ValueError:
        body = {}
    if status == 200 and body.get("ok"):
        outcome, got = body["predicted_price_text"], "ok"
        if body.get("warnings"):
            outcome += " [Warning shown]"
    elif status in (400, 422) and body.get("errors"):
        outcome, got = " | ".join(body["errors"].values()), "error"
    else:
        outcome, got = f"unexpected response (HTTP {status})", "crash"
    ok = got == expected
    passed += ok
    shown = {k: v for k, v in data.items() if k != "model"}
    rows.append((group, desc, ", ".join(f"{k}={v!r}" for k, v in shown.items()) or "(empty)", data.get("model") or "-", status, outcome, "Pass" if ok else "FAIL"))

# pages and options
page_checks = []
for path in ["/", "/predict.html", "/result.html", "/style.css", "/app.js", "/api/options"]:
    status, _ = request("GET", path)
    page_checks.append((path, status))
status_404, raw_404 = request("GET", "/api/nothing-here")
pages_ok = all(s == 200 for _, s in page_checks) and status_404 == 404

lines = ["# Web application test results", "",
         "Every output below was returned by the running app (`python dev_server.py`) through `POST /api/predict`. Nothing was typed in by hand.",
         "Price unit: lakhs of INR as given in the dataset description; shown as rupees with Indian digit grouping.", "",
         f"**Result: {passed} of {len(tests)} prediction tests passed.** A pass means the outcome matched what was expected before running the test.", "",
         "| # | Group | Test | Input | Model | HTTP | Actual output | Status |", "|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    lines.append(f"| {i} | " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
lines += ["", "## Pages and options", "", "| Path | HTTP |", "|---|---|"] + [f"| `{p}` | {s} |" for p, s in page_checks]
lines += [f"| `/api/nothing-here` (unknown endpoint) | {status_404} (JSON error) |", "",
          f"**Pages and options: {'all as expected' if pages_ok else 'CHECK FAILED'}.**"]
OUT.write_text("\n".join(lines) + "\n")
print(f"{passed}/{len(tests)} prediction tests passed; pages ok: {pages_ok}")
