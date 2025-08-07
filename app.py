from flask import Flask, jsonify, request, send_from_directory
import requests
import json
import os

app = Flask(__name__, static_folder="static")

# Last inn skins fra fil
with open("skins.json", "r", encoding="utf-8") as f:
    all_items = json.load(f)

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/skins")
def get_skins():
    return jsonify(all_items)

@app.route("/top10")
def top10():
    deals = []
    for item in all_items[:50]:
        try:
            url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={item}"
            r = requests.get(url)
            data = r.json()

            if data.get("lowest_price") and data.get("median_price"):
                lowest = float(data["lowest_price"].replace("$", "").replace(",", ""))
                median = float(data["median_price"].replace("$", "").replace(",", ""))
                deviation = round((lowest - median) / median * 100, 2)

                deals.append({
                    "item": item,
                    "lowest_price": data["lowest_price"],
                    "median_price": data["median_price"],
                    "percent_below": deviation,
                    "volume": data.get("volume", "N/A")
                })
        except Exception:
            continue

    sorted_deals = sorted(deals, key=lambda x: x["percent_below"])
    return jsonify({"count": len(sorted_deals[:10]), "deals": sorted_deals[:10]})

@app.route("/search")
def search():
    query = request.args.get("item")
    if not query:
        return jsonify({"error": "No item provided"}), 400

    url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={query}"
    r = requests.get(url)
    data = r.json()

    if "lowest_price" in data and "median_price" in data:
        lowest = float(data["lowest_price"].replace("$", "").replace(",", ""))
        median = float(data["median_price"].replace("$", "").replace(",", ""))
        deviation = round((lowest - median) / median * 100, 2)
        return jsonify({
            "item": query,
            "lowest_price": data["lowest_price"],
            "median_price": data["median_price"],
            "percent_below": deviation,
            "volume": data.get("volume", "N/A")
        })
    else:
        return jsonify({"error": "Skin not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
