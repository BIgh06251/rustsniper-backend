from flask import Flask, jsonify, request
import requests, json, os, re
from urllib.parse import unquote, quote

app = Flask(__name__, static_folder="static")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://steamcommunity.com/market/search?appid=252490",
}

# Safe load skins.json
try:
    with open("skins.json", "r", encoding="utf-8") as f:
        all_items = json.load(f)
    if not isinstance(all_items, list):
        all_items = []
    print(f"[boot] loaded {len(all_items)} skins")
except Exception as e:
    print("[boot] failed to load skins.json:", e)
    all_items = []

@app.route("/")
def root():
    return app.send_static_file("index.html")

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "index_exists": os.path.isfile(os.path.join(app.static_folder, "index.html")),
        "static_exists": os.path.isdir(app.static_folder),
        "skins_exists": os.path.isfile("skins.json"),
        "skins_count": len(all_items),
        "cwd": os.getcwd(),
    })

def priceoverview(name: str):
    url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={quote(name)}"
    r = requests.get(url, headers=HEADERS, timeout=8)
    return r.json()

def search_candidates(query: str, limit: int = 3):
    """Search Steam and extract market_hash_name candidates from results_html."""
    url = (
        "https://steamcommunity.com/market/search/render/"
        f"?query={quote(query)}&start=0&count=10&search_descriptions=0"
        "&sort_column=popular&sort_dir=desc&appid=252490"
    )
    r = requests.get(url, headers=HEADERS, timeout=8)
    data = r.json()
    html = data.get("results_html", "") or ""
    # 1) Best: explicit data-hash-name
    names = re.findall(r'data-hash-name="([^"]+)"', html)
    # 2) Fallback from listing URL path
    if not names:
        names = [unquote(m) for m in re.findall(r'/market/listings/252490/([^"?]+)', html)]
    # dedup while preserving order
    seen, out = set(), []
    for n in names:
        if n not in seen:
            out.append(n); seen.add(n)
        if len(out) >= limit:
            break
    return out

@app.route("/skins")
def get_skins():
    return jsonify(all_items)

@app.route("/top10")
def top10():
    deals = []
    for item in all_items[:50]:
        try:
            data = priceoverview(item)
            if data.get("lowest_price") and data.get("median_price"):
                def to_float(s):
                    return float(
                        s.replace("$","").replace("kr","").replace("€","").replace("£","")
                         .replace(" ", "").replace(",", "")
                    )
                lowest = to_float(data["lowest_price"])
                median = to_float(data["median_price"])
                deviation = round((lowest - median) / median * 100, 2) if median else 0.0
                deals.append({
                    "item": item,
                    "lowest_price": data["lowest_price"],
                    "median_price": data["median_price"],
                    "percent_below": deviation,
                    "volume": data.get("volume", "N/A")
                })
        except Exception as e:
            print(f"[top10] skip {item}: {e}")
            continue
    sorted_deals = sorted(deals, key=lambda x: x["percent_below"])
    return jsonify({"count": len(sorted_deals[:10]), "deals": sorted_deals[:10]})

@app.route("/search")
def search():
    q = request.args.get("item")
    if not q:
        return jsonify({"error": "No item provided"}), 400

    # 1) Try direct
    try:
        d = priceoverview(q)
        if d.get("lowest_price") and d.get("median_price"):
            def to_float(s):
                return float(
                    s.replace("$","").replace("kr","").replace("€","").replace("£","")
                     .replace(" ", "").replace(",", "")
                )
            lowest = to_float(d["lowest_price"])
            median = to_float(d["median_price"])
            deviation = round((lowest - median) / median * 100, 2) if median else 0.0
            return jsonify({
                "item": q,
                "canonical_name": q,
                "lowest_price": d["lowest_price"],
                "median_price": d["median_price"],
                "percent_below": deviation,
                "volume": d.get("volume", "N/A")
            })
    except Exception as e:
        print("[search] direct failed:", e)

    # 2) Fallback: search for correct hash names
    candidates = search_candidates(q, limit=5)
    for name in candidates:
        try:
            d = priceoverview(name)
            if d.get("lowest_price") and d.get("median_price"):
                def to_float(s):
                    return float(
                        s.replace("$","").replace("kr","").replace("€","").replace("£","")
                         .replace(" ", "").replace(",", "")
                )
                lowest = to_float(d["lowest_price"])
                median = to_float(d["median_price"])
                deviation = round((lowest - median) / median * 100, 2) if median else 0.0
                return jsonify({
                    "item": q,
                    "canonical_name": name,  # the exact Steam name we used
                    "lowest_price": d["lowest_price"],
                    "median_price": d["median_price"],
                    "percent_below": deviation,
                    "volume": d.get("volume", "N/A")
                })
        except Exception as e:
            print(f"[search] candidate {name} failed: {e}")
            continue

    return jsonify({"error": f'Skin not found for query "{q}"'}), 404

if __name__ == "__main__":
    app.run(debug=True)
