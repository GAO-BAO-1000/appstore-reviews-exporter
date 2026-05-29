import streamlit as st
import requests
import pandas as pd
import time
from io import StringIO

st.title("🍎 App Store Reviews Exporter (DUOLINGO)")
st.write("Collect and export App Store reviews to CSV")
st.caption("Built by @GAO-BAO-1000 | Data Tool for App Analytics")

# -------------------------
# Helpers
# -------------------------

def fetch_reviews(app_id, page=1, country="us"):
    url = f"https://itunes.apple.com/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
    if country:
        url += f"?cc={country}"

    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"Request error: {e}")
        return None


def safe_get(entry, path, default=None):
    try:
        for p in path:
            entry = entry[p]
        return entry
    except:
        return default


def parse_review(entry, app_id, country, source_url, app_name):
    return {
        "review_id": safe_get(entry, ["id", "label"]),
        "app_id": app_id,
        "app_name": app_name,
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


def collect_all_reviews(app_id, country="us", progress_bar=None, status=None):
    results = []
    seen = set()
    page = 1

    while True:
        data = fetch_reviews(app_id, page, country)
        if not data:
            break

        feed = data.get("feed", {})
        entries = feed.get("entry", [])

        if not isinstance(entries, list) or len(entries) == 0:
            break

        app_name = safe_get(feed, ["title", "label"], None)

        new_data = 0

        for e in entries:
            r = parse_review(
                e,
                app_id,
                country,
                f"https://itunes.apple.com/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json",
                app_name
            )

            rid = r["review_id"]
            if not rid or rid in seen:
                continue

            seen.add(rid)
            results.append(r)
            new_data += 1

        if status:
            status.write(f"Page {page} → +{new_data} reviews (total {len(results)})")

        if progress_bar:
            progress_bar.progress(min(page / 10, 1.0))  # приблизительный прогресс

        if new_data == 0:
            break

        page += 1
        time.sleep(0.5)

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.drop_duplicates(subset=["review_id"])

    return df


# -------------------------
# STREAMLIT UI
# -------------------------

st.title("🍎 Apple App Store Reviews Collector (All Time)")

app_id = st.text_input("Enter App ID", "")
country = st.text_input("Country code", "us")

start = st.button("Start scraping")

if start:
    if not app_id.isdigit():
        st.error("App ID must be numeric")
    else:
        app_id = int(app_id)

        progress = st.progress(0)
        status = st.empty()

        df = collect_all_reviews(app_id, country, progress, status)

        st.success(f"Done! Total reviews: {len(df)}")

        st.dataframe(df)

        # -------------------------
        # CSV download
        # -------------------------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"app_{app_id}_reviews.csv",
            mime="text/csv"
        )
