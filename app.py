from flask import Flask, jsonify, request, send_file
import requests
import json
import os

app = Flask(__name__)

# Last inn alle skins fra fil
with open("skins.json", "r", encoding="utf-8") as f:
    all_items = json.load(f)

# ✅ Forside
@app.route("/")
def home():
    return send_file("index.html")

# 🔎 Returner alle skins til søkefelt
@app.route("/skins")
def get_skins():
    return jsonify(all_items)

# 🔥 Returner top 10 underprisede skins
@app.route("/top10")
def top10():
    deals = []
    for item in all_items[:50]:  # Du kan øke dette om du har mange skins
        try:
            url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={item}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
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
        except Exception as e:
            print(f"❌ Feil med {item}: {e}")
            continue

    sorted_deals = sorted(deals, key=lambda x: x["percent_below"])
    return jsonify({"count": len(sorted_deals[:10]), "deals": sorted_deals[:10]})

# 🔍 Søk etter ett skin
@app.route("/search")
def search():
    query = request.args.get("item")
    if not query:
        return jsonify({"error": "No item provided"}), 400

    try:
        url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 For lokal testing
if __name__ == "__main__":
    app.run(debug=True)
