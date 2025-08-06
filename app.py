from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ RustSniper backend is running. Use /snipes to get discounted Rust skin deals."

@app.route("/snipes")
def get_snipes():
    url = "https://api.skinport.com/v1/items?app_id=730&currency=EUR"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return jsonify({
            "error": "Failed to fetch data from Skinport API",
            "details": str(e)
        }), 500

    snipes = []
    for item in data:
        if item.get('min_price') and item.get('suggested_price'):
            if item['min_price'] < 0.8 * item['suggested_price']:
                snipes.append({
                    "name": item['market_hash_name'],
                    "min_price": round(item['min_price'], 2),
                    "suggested_price": round(item['suggested_price'], 2),
                    "link": f"https://skinport.com/item/{item['market_hash_name'].replace(' ', '%20')}"
                })

    return jsonify(snipes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
