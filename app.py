from flask import Flask, jsonify
import requests
import os
import time
import json

app = Flask(__name__)

SKINS_CACHE = "skins.json"
STEAM_API_URL = "https://steamcommunity.com/market/priceoverview/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

@app.route("/")
def home():
    return "✅ RustSniper API is live and scanning!"

@app.route("/snipes/all")
def get_all_snipes():
    skins = get_all_skins()
    deals = []

    for name in skins:
        price_data = fetch_price_data(name)
        if not price_data or "lowest_price" not in price_data or "median_price" not in price_data:
            continue
        try:
            lowest = float(price_data["lowest_price"].replace("$", "").replace(" USD", ""))
            median = float(price_data["median_price"].replace("$", "").replace(" USD", ""))
            if lowest < 1.1 * median:
                deals.append({
                    "item": name,
                    "lowest_price": price_data["lowest_price"],
                    "median_price": price_data["median_price"],
                    "volume": price_data["volume"]
                })
        except:
            continue
        time.sleep(1)  # For å være snill med Steam

    return jsonify({
        "count": len(deals),
        "deals": deals
    })

def get_all_skins():
    # Bruk cache hvis den finnes
    if os.path.exists(SKINS_CACHE):
        with open(SKINS_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    skins = []
    start = 0
    while True:
        print(f"Henter Rust skins... offset={start}")
        params = {
            "country": "NO",
            "currency": 1,
            "appid": 252490,
            "norender": 1,
            "start": start,
            "count": 100
        }
        try:
            res = requests.get("https://steamcommunity.com/market/search/render/", params=params, headers=HEADERS)
            data = res.json()
            results = data.get("results", [])
            if not results:
                break
            for item in results:
                skins.append(item["hash_name"])
            if not data.get("more", False):
                break
            start += 100
            time.sleep(1)
        except:
            break

    # Lagre cache
    with open(SKINS_CACHE, "w", encoding="utf-8") as f:
        json.dump(skins, f, indent=2, ensure_ascii=False)

    return skins

def fetch_price_data(item):
    try:
        params = {
            "country": "NO",
            "currency": 1,
            "appid": 252490,
            "market_hash_name": item
        }
        res = requests.get(STEAM_API_URL, params=params, headers=HEADERS)
        res.raise_for_status()
        return res.json()
    except:
        return None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
