from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/snipes")
def get_kilt_price():
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "country": "NO",
        "currency": 1,  # USD: 1, Euro: 3, NOK: 9
        "appid": 252490,
        "market_hash_name": "Whiteout Kilt"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            return jsonify({
                "item": "Whiteout Kilt",
                "lowest_price": data.get("lowest_price", "N/A"),
                "median_price": data.get("median_price", "N/A"),
                "volume": data.get("volume", "N/A")
            })
        else:
            return jsonify({"error": "Steam API response was not successful"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to fetch price", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

