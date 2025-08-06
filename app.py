from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/snipes')
def get_snipes():
    url = "https://api.skinport.com/v1/items?app_id=730&currency=EUR"
    response = requests.get(url)
    data = response.json()
    snipes = []

    for item in data:
        if item['min_price'] and item['suggested_price']:
            if item['min_price'] < 0.8 * item['suggested_price']:
                snipes.append({
                    "name": item['market_hash_name'],
                    "min_price": item['min_price'],
                    "suggested_price": item['suggested_price'],
                    "link": f"https://skinport.com/item/{item['market_hash_name'].replace(' ', '%20')}"
                })

    return jsonify(snipes)

if __name__ == "__main__":
    app.run(debug=True)
