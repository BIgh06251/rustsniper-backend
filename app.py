from flask import Flask, jsonify, request
import requests, json, os

app = Flask(__name__, static_folder="static")

# ---- Boot diagnostics ----
CWD = os.getcwd()
STATIC_DIR = os.path.abspath(app.static_folder)
INDEX_PATH = os.path.join(STATIC_DIR, "index.html")
SKINS_PATH = os.path.join(CWD, "skins.json")

print(f"[boot] cwd={CWD}")
print(f"[boot] static_dir={STATIC_DIR} exists={os.path.isdir(STATIC_DIR)}")
print(f"[boot] index_path={INDEX_PATH} exists={os.path.isfile(INDEX_PATH)}")
print(f"[boot] skins_path={SKINS_PATH} exists={os.path.isfile(SKINS_PATH)}")

# Safe load skins.json
try:
    with open(SKINS_PATH, "r", encoding="utf-8") as f:
        all_items = json.load(f)
    if not isinstance(all_items, list):
        print("[boot] skins.json is not a list; resetting to empty list.")
        all_items = []
    print(f"[boot] loaded {len(all_items)} skins")
except Exception as e:
    print("[boot] failed to load skins.json:", repr(e))
    all_items = []

# ---- Routes ----
@app.route("/")
def root():
    try:
        return app.send_static_file("index.html")
    except Exception as e:
        print("[/] failed to serve index.html:", repr(e))
        return jsonify({"error": "failed to serve index.html", "detail": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "cwd": CWD,
        "static_exists": os.path.isdir(STATIC_DIR),
        "index_exists": os.path.isfile(INDEX_PATH),
        "skins_exists": os.path.isfile(SKINS_PATH),
        "skins_count": len(all_items),
    })

@app.route("/debug")
def debug():
    try:
        cwd_files = sorted(os.listdir(CWD))[:50]
    except Exception as e:
        cwd_files = [f"err: {e}"]
    try:
        static_files = sorted(os.listdir(STATIC_DIR))[:50] if os.path.isdir(STATIC_DIR) else []
    except Exception as e:
        static_files = [f"err: {e}"]
    return jsonify({
        "cwd": CWD,
        "cwd_files": cwd_files,
        "static_dir": STATIC_DIR,
        "static_files": static_files,
        "index_exists": os.path.isfile(INDEX_PATH),
        "skins_exists": os.path.isfile(SKINS_PATH),
        "skins_count": len(all_items),
    })

@app.route("/skins")
def get_skins():
    return jsonify(all_items)

@app.route("/top10")
def top10():
    deals = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for item in all_items[:50]:
        try:
            url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={item}"
            r = requests.get(url, headers=headers, timeout=8)
            data = r.json()
            if data.get("lowest_price") and data.get("median_price"):
                def to_float(s):
                    return float(s.replace("$","").replace("kr","").replace(" ","").replace(",", ""))
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
    try:
        url = f"https://steamcommunity.com/market/priceoverview/?country=NO&currency=1&appid=252490&market_hash_name={q}"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        data = r.json()
        if "lowest_price" in data and "median_price" in data:
            def to_float(s):
                return float(s.replace("$","").replace("kr","").replace(" ","").replace(",", ""))
            lowest = to_float(data["lowest_price"])
            median = to_float(data["median_price"])
            deviation = round((lowest - median) / median * 100, 2) if median else 0.0
            return jsonify({
                "item": q,
                "lowest_price": data["lowest_price"],
                "median_price": data["median_price"],
                "percent_below": deviation,
                "volume": data.get("volume", "N/A")
            })
        return jsonify({"error":"Skin not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Request failed: {e}"}), 500

if __name__ == "__main__":
    # Local dev; gunicorn runs this on Railway
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
