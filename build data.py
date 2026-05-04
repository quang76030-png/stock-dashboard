import json
from datetime import datetime, timezone, timedelta

# Dữ liệu mẫu – sau này sẽ thay bằng API thật
def fetch_data():
    tickers = ["VNINDEX", "HPG", "SSI", "VIC", "VHM", "VCB"]
    result = []
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    for ticker in tickers:
        result.append({
            "ticker": ticker,
            "price": 1280.50,
            "change": 5.20,
            "changePercent": 0.41,
            "volume": 800000000,
            "lastUpdate": now
        })
    return result

data = fetch_data()
with open("market_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
