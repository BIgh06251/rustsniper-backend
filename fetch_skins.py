import requests
import json
import time
from bs4 import BeautifulSoup

def fetch_all_rust_skins():
    skins = []
    start = 0
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
            html = data.get("results_html", "")
            if not html:
                print("❌ Mangler results_html. Avslutter...")
                break

            soup = BeautifulSoup(html, "html.parser")
            items = soup.select(".market_listing_item_name")

            if not items:
                print("❌ Fant ingen items. Avslutter...")
                break

            for tag in items:
                name = tag.get_text(strip=True)
                skins.append(name)

            print(f"✅ Hentet {len(items)} skins fra start={start}")
            if len(items) < 100:
                break

            start += 100
            time.sleep(1.5)

        except Exception as e:
            print(f"⚠️ Feil ved henting/parsing: {e}")
            break

    try:
        with open("skins.json", "w", encoding="utf-8") as f:
            json.dump(skins, f, ensure_ascii=False, indent=2)
        print(f"✅ Lagret {len(skins)} skins til skins.json")
    except Exception as e:
        print("❌ Klarte ikke lagre:", e)

    return skins

if __name__ == "__main__":
    all_skins = fetch_all_rust_skins()
    print("📦 Totalt hentet:", len(all_skins))
    if all_skins:
        print("🔹 Første skin:", all_skins[0])
