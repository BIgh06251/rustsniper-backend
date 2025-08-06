from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)  # 👈 Gjør at frontend får hente data uten CORS-feil

@app.route("/")
def home():
    return "✅ RustSniper API is running!"

@app.route("/snipes")
def get_item_price():
    item = request.args.get("item", "Whiteout Kilt")
    return fetch_price(item)

@app.route("/snipes/all")
def get_deals():
    items = [
        "Whiteout Kilt",
        "Tempered Mask",
        "Azul Hoodie",
        "Plate Carrier",
        "Blackout Gloves",
        "No Mercy Hoodie",
        "Arctic Wolf Pants"
    ]

    deals = []

    for item in items:
        data = fetch_price_data(item)
        if not data or "lowest_price" not in data or "median_price" not in data:
            continue

        try:
            lowest = float(data["lowest_price"].replace("$", "").replace(" USD", ""))
            median = float(data["median_price"].replace("$", "").replace(" USD", ""))
            if lowest < 0.7 * median:
                deals.append({
                    "item": item,
                    "lowest_price": data["lowest_price"],
                    "median_price": data["median_price"],
                    "volume": data["volume"]
                })
        except:
            continue

        time.sleep(1)

    return jsonify({
        "count": len(deals),
        "deals": deals
    })

def fetch_price(item):
    data = fetch_price_data(item)
    if data and data.get("success"):
        return jsonify({
            "item": item,
            "lowest_price": data.get("lowest_price", "N/A"),
            "median_price": data.get("median_price", "N/A"),
            "volume": data.get("volume", "N/A")
        })
    else:
        return jsonify({"error": "Steam API response failed"}), 500

def fetch_price_data(item):
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "country": "NO",
        "currency": 1,
        "appid": 252490,
        "market_hash_name": item
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except:
        return None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
