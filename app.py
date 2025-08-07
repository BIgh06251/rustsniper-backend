from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

with open("skins.json", encoding="utf-8") as f:
    ALL_SKINS = json.load(f)

@app.route("/")
def home():
    return "✅ RustSniper API is live!"

@app.route("/search")
def search_skin():
    name = request.args.get("item")
    if not name:
        return jsonify({"error": "No item provided"}), 400
    data = fetch_price_data(name)
    if not data or not data.get("success"):
        return jsonify({"error": "Failed to fetch"}), 500
    lowest = parse_price(data.get("lowest_price"))
    median = parse_price(data.get("median_price"))
    percent = round((1 - lowest / median) * 100, 2) if median else 0
    return jsonify({
        "item": name,
        "lowest_price": data.get("lowest_price"),
        "median_price": data.get("median_price"),
        "volume": data.get("volume"),
        "percent_below": percent
    })

@app.route("/top10")
def top_10_deals():
    deals = []
    for item in ALL_SKINS[:200]:  # begrens til 200 for ytelse
        data = fetch_price_data(item)
        if not data or "lowest_price" not in data or "median_price" not in data:
            continue
        try:
            low = parse_price(data["lowest_price"])
            med = parse_price(data["median_price"])
            if low < 0.7 * med:
                deals.append({
                    "item": item,
                    "lowest_price": data["lowest_price"],
                    "median_price": data["median_price"],
                    "volume": data["volume"],
                    "percent_below": round((1 - low / med) * 100, 2)
                })
        except:
            continue
    deals.sort(key=lambda x: x["percent_below"], reverse=True)
    return jsonify({"count": len(deals[:10]), "deals": deals[:10]})

def parse_price(price):
    return float(price.replace("$", "").replace(" USD", "").replace(",", ""))

def fetch_price_data(item):
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {"country": "NO", "currency": 1, "appid": 252490, "market_hash_name": item}
    try:
        response = requests.get(url, params=params, timeout=5)
        return response.json()
    except:
        return None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
