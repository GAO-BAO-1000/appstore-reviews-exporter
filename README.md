# 🍎 App Store Reviews Exporter DUOLINGO

A Streamlit-based tool for collecting and exporting Apple App Store reviews into a structured CSV format for analysis.

---

## 🚀 Features

- Collects reviews from Apple App Store RSS API
- Supports all available pages (historical data scraping)
- Exports data to CSV
- Simple Streamlit interface
- No API key required

---

## 📊 Output Data

Each review includes:

- Review ID
- App ID
- App name
- Country / storefront
- Author name
- Rating
- Review title
- Review text
- App version
- Review date
- Source URL

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
