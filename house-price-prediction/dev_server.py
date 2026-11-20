"""
Run the whole project locally (pages + API) with one command:

    python dev_server.py

then open http://127.0.0.1:5000
"""
from api.index import app

if __name__ == "__main__":
    print("House Price Prediction running at http://127.0.0.1:5000  (stop with Ctrl + C)")
    app.run(host="127.0.0.1", port=5000, debug=False)
