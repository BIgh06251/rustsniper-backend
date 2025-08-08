import requests, json, time, re
from urllib.parse import unquote

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://steamcommunity.com/market/search?appid=252490",
}

def fetch_all_rust_skins():
    skins, start = [], 0
    print("🔄 Starter henting av Rust skins fra Steam...")

    while True:
        url = (
            "https://steamcommunity.com/market/search/render/"
            f"?query=&start={start}&count=100&search_descriptions=0"
            "&sort_column=popular&sort_dir=desc&appid=252490"
        )
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"❌ Feil {r.status_code}: {r.text[:200]}")
            break

        data = r.json()
        html = (data.get("results_html") or "").strip()
        total = data.get("total_count", 0)

        if not html:
            print("❌ Tom HTML i results_html – stopper.")
            break

        # Prefer exact data-hash-name (present in modern Steam markup)
        names = re.findall(r'data-hash-name="([^"]+)"', html)

        # Fallback from listing URLs
        if not names:
            names = [unquote(m) for m in re.findall(r'/market/listings/252490/([^"?]+)', html)]

        if not names:
            print("❌ Fant ingen navn på denne siden – stopper.")
            break

        added = 0
        for n in names:
            if n not in skins:
                skins.append(n)
                added += 1

        print(f"✅ start={start}: fant {len(names)} (nye: {added}) | totalt unike: {len(skins)}")

        start += 100
        # Stop if we've paged past total_count or reached a sane cap
        if total and start >= total:
            break
        if start >= 5000:
            break

        time.sleep(1.5)

    with open("skins.json", "w", encoding="utf-8") as f:
        json.dump(skins, f, ensure_ascii=False, indent=2)

    print(f"✅ Lagret {len(skins)} skins til skins.json")
    return skins

if __name__ == "__main__":
    all_skins = fetch_all_rust_skins()
    print("📦 Totalt hentet:", len(all_skins))
    if all_skins:
        print("🔹 Første skin:", all_skins[0])
