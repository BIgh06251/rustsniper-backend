from flask import Flask, jsonify, request
import requests, json, os

app = Flask(__name__, static_folder="static")

# Safe load of skins.json
try:
    with open("skins.json", "r", encoding="utf-8") as f:
        all_items = json.load(f)
    print(f"✅ Laster inn {len(all_items)} skins fra skins.json")
except Exception as e:
    print("❌ Klarte ikke laste skins.json:", e)
    all_items = []

@app.route("/")
def home():
    # Serve static/index.html
    return app.send_static_file("index.html")

@app.route("/health")
def health():
    return jsonify({"ok": True, "skins": len(all_items)})

@app.route("/skins")
def get_skins():
    return jsonify(all_items)

@app.route("/top10")
def top10():
    deals = []
    for item in all_items[:50]:
        try:
            url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={item}"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
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
            print(f"❌ Feil for {item}: {e}")
            continue

    sorted_deals = sorted(deals, key=lambda x: x["percent_below"])
    return jsonify({"count": len(sorted_deals[:10]), "deals": sorted_deals[:10]})

@app.route("/search")
def search():
    q = request.args.get("item")
    if not q:
        return jsonify({"error": "No item provided"}), 400
    try:
        url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={q}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        if "lowest_price" in data and "median_price" in data:
            lowest = float(data["lowest_price"].replace("$", "").replace(",", ""))
            median = float(data["median_price"].replace("$", "").replace(",", ""))
            deviation = round((lowest - median) / median * 100, 2)
            return jsonify({
                "item": q,
                "lowest_price": data["lowest_price"],
                "median_price": data["median_price"],
                "percent_below": deviation,
                "volume": data.get("volume", "N/A")
            })
        return jsonify({"error": "Skin not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Request failed: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
