import requests
import json
import time

def fetch_all_rust_skins():
    skins = []
    start = 0
    max_pages = 50  # max 100 * 50 = 5000 skins

    print("🔄 Starter henting av Rust skins fra Steam...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Referer': 'https://steamcommunity.com/market/search?appid=252490'
    }

    while True:
        url = f"https://steamcommunity.com/market/search/render/?query=&start={start}&count=100&search_descriptions=0&sort_column=popular&sort_dir=desc&appid=252490"

        try:
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print(f"❌ Feil {r.status_code}: {r.text[:200]}")
                break

            data = r.json()

            # Steam returnerer ikke "results" uten login – da avslutter vi
            if "results" not in data or not data["results"]:
                print("❌ Ingen resultater i JSON. Mulig blokkert av Steam.")
                break

            for item in data["results"]:
                name = item.get("name")
                if name and name not in skins:
                    skins.append(name)

            print(f"✅ Hentet {len(data['results'])} skins (totalt: {len(skins)}) fra start={start}")

            if len(data["results"]) < 100 or start >= max_pages * 100:
                print("🛑 Ferdig med scraping.")
                break

            start += 100
            time.sleep(1.5)

        except Exception as e:
            print(f"⚠️ Feil ved henting: {e}")
            break

    try:
        with open("skins.json", "w", encoding="utf-8") as f:
            json.dump(skins, f, ensure_ascii=False, indent=2)
        print(f"✅ Lagret {len(skins)} skins til skins.json")
    except Exception as e:
        print("❌ Klarte ikke lagre skins.json:", e)

    return skins

if __name__ == "__main__":
    all_skins = fetch_all_rust_skins()
    print("📦 Totalt hentet:", len(all_skins))
    if all_skins:
        print("🔹 Første skin:", all_skins[0])
