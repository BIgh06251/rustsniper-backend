# fetch_skins.py
import requests
import json
import time

def fetch_all_rust_skins():
    skins = []
    start = 0
    print("🔄 Starter henting av Rust skins fra Steam...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    while True:
        url = f"https://steamcommunity.com/market/search/render/?query=&start={start}&count=100&search_descriptions=0&sort_column=popular&sort_dir=desc&appid=252490"
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if "results" not in data or not data["results"]:
                print("❌ Ingen flere resultater eller feil med 'results'. Avslutter...")
                break

            for item in data["results"]:
                name = item.get("name")
                if name:
                    skins.append(name)

            print(f"✅ Hentet {len(data['results'])} skins fra start={start}")

            if len(data["results"]) < 100:
                break  # Slutt hvis vi er på siste side

            start += 100
            time.sleep(1.5)  # Steam liker ikke spamming

        except Exception as e:
            print(f"⚠️ Feil ved henting (start={start}):", e)
            break

    # Lagre til JSON
    try:
        with open("skins.json", "w", encoding="utf-8") as f:
            json.dump(skins, f, ensure_ascii=False, indent=2)
        print(f"✅ Lagret {len(skins)} skins til skins.json")
    except Exception as e:
        print("❌ Klarte ikke lagre til skins.json:", e)

    return skins

# Railway cron-jobb kjører dette
if __name__ == "__main__":
    all_skins = fetch_all_rust_skins()
    print("📦 Totalt hentet:", len(all_skins))
    if all_skins:
        print("🔹 Første skin:", all_skins[0])
