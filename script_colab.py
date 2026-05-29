# =========================
# Google Colab: Apple Reviews Collector (ALL TIME)
# =========================

!pip -q install requests pandas

import requests
import pandas as pd
import time

# -------------------------
# Helpers
# -------------------------

def fetch_reviews(app_id, page=1, country="us"):
    url = f"https://itunes.apple.com/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
    if country:
        url += f"?cc={country}"

    print(f"[INFO] Fetching page {page}")

    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def safe_get(entry, path, default=None):
    try:
        for p in path:
            entry = entry[p]
        return entry
    except:
        return default


def parse_review(entry, app_id, country, source_url):
    return {
        "review_id": safe_get(entry, ["id", "label"]),
        "app_id": app_id,
        "app_name": None,
        "country": country,
        "author_name": safe_get(entry, ["author", "name", "label"]),
        "rating": safe_get(entry, ["im:rating", "label"]),
        "review_title": safe_get(entry, ["title", "label"]),
        "review_text": safe_get(entry, ["content", "label"]),
        "app_version": safe_get(entry, ["im:version", "label"]),
        "review_date": safe_get(entry, ["updated", "label"]),
        "helpful_count": None,
        "source_url": source_url
    }


def collect_all_reviews(app_id, country="us"):
    results = []
    seen = set()

    page = 1

    while True:
        data = fetch_reviews(app_id, page, country)
        if not data:
            break

        feed = data.get("feed", {})
        entries = feed.get("entry", [])

        # first item is usually app metadata, skip non-list pages
        if not isinstance(entries, list) or len(entries) == 0:
            print("[INFO] No more data, stopping.")
            break

        app_name = safe_get(feed, ["title", "label"], None)

        new_data = 0

        for e in entries:
            r = parse_review(
                e,
                app_id,
                country,
                f"https://itunes.apple.com/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
            )

            r["app_name"] = app_name

            rid = r["review_id"]
            if not rid or rid in seen:
                continue

            seen.add(rid)
            results.append(r)
            new_data += 1

        print(f"[INFO] Page {page} -> +{new_data} reviews (total {len(results)})")

        if new_data == 0:
            print("[INFO] No new reviews found, stopping.")
            break

        page += 1
        time.sleep(0.5)

    df = pd.DataFrame(results)

    if not df.empty:
        df = df.drop_duplicates(subset=["review_id"])

    return df


# -------------------------
# USER INPUT
# -------------------------

app_id = int(input("Enter App ID: "))
country = input("Country code (default us): ") or "us"

# -------------------------
# RUN
# -------------------------

df = collect_all_reviews(app_id, country)

file_name = f"app_{app_id}_ALL_reviews.csv"
df.to_csv(file_name, index=False)

print("\n=========================")
print(f"[DONE] CSV saved: {file_name}")
print(f"[DONE] Total reviews: {len(df)}")
print("=========================\n")

display(df.head())

# -------------------------
# Download (Colab)
# -------------------------
from google.colab import files
files.download(file_name)
