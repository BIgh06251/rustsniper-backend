# fetch_skins.py
import requests
import json
import time

def fetch_all_rust_skins():
    skins = []
    start = 0
    while True:
        url = f"https://steamcommunity.com/market/search/render/?query=&start={start}&count=100&search_descriptions=0&sort_column=popular&sort_dir=desc&appid=252490"
        r = requests.get(url)
        data = r.json()
        if "results" not in data:
            break

        for item in data["results"]:
            name = item["name"]
            skins.append(name)

        if not data["results"] or len(data["results"]) < 100:
            break

        start += 100
        time.sleep(1)

    # Lagre som JSON
    with open("skins.json", "w", encoding="utf-8") as f:
        json.dump(skins, f, ensure_ascii=False, indent=2)

    print(f"Hentet {len(skins)} Rust skins.")

if __name__ == "__main__":
    fetch_all_rust_skins()
