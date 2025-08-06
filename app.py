from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/snipes')
def get_snipes():
    url = "https://api.skinport.com/v1/items?app_id=730&currency=EUR"
    response = requests.get(url)
    data = response.json()
    snipes = []

    for item in data:
        if item.get('min_price') and item.get('suggested_price'):
            if item['min_price'] < 0.8 * item['suggested_price']:
                snipes.append({
                    "name": item['market_hash_name'],
                    "min_price": item['min_price'],
                    "suggested_price": item['suggested_price'],
                    "link": f"https://skinport.com/item/{item['market_hash_name'].replace(' ', '%20')}"
                })

    return jsonify(snipes)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
