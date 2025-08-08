import requests, json, time, re, os, base64
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
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"❌ Feil {r.status_code}: {r.text[:200]}")
            break

        data = r.json()
        html = (data.get("results_html") or "").strip()
        total = data.get("total_count", 0)

        if not html:
            print("❌ Tom HTML i results_html – stopper.")
            break

        # Prefer exact names from data-hash-name
        names = re.findall(r'data-hash-name="([^"]+)"', html)

        # Fallback from listing URLs if needed
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

        time.sleep(1.2)

    with open("skins.json", "w", encoding="utf-8") as f:
        json.dump(skins, f, ensure_ascii=False, indent=2)

    print(f"✅ Lagret {len(skins)} skins til skins.json")
    return skins

# ---------- GitHub push ----------
def get_file_sha(owner, repo, path, branch, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    h = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    r = requests.get(url, headers=h, timeout=20)
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def push_to_github(owner, repo, path, branch, token, content_bytes, message):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    sha = get_file_sha(owner, repo, path, branch, token)
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    h = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    r = requests.put(url, headers=h, json=payload, timeout=30)
    if r.status_code in (200, 201):
        print("✅ Pushet skins.json til GitHub")
    else:
        print(f"❌ Klarte ikke pushe til GitHub: {r.status_code} {r.text[:300]}")

if __name__ == "__main__":
    all_skins = fetch_all_rust_skins()
    print("📦 Totalt hentet:", len(all_skins))
    if all_skins:
        print("🔹 Første skin:", all_skins[0])

    # Push back to GitHub so web service redeploys with latest list
    GH_TOKEN  = os.getenv("GH_TOKEN")         # set this in Railway (job service)
    GH_OWNER  = os.getenv("GH_OWNER", "Blgh06251")
    GH_REPO   = os.getenv("GH_REPO", "rustsniper-backend")
    GH_BRANCH = os.getenv("GH_BRANCH", "main")

    if GH_TOKEN:
        with open("skins.json", "rb") as f:
            push_to_github(
                GH_OWNER, GH_REPO, "skins.json", GH_BRANCH, GH_TOKEN,
                f.read(), "chore: update skins.json from cron job"
            )
    else:
        print("ℹ️ GH_TOKEN ikke satt – hopper over GitHub push.")
