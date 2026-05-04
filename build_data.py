import json
import requests
from datetime import datetime, timezone, timedelta

def fetch_all_stocks():
    print("Bắt đầu lấy dữ liệu toàn thị trường...")
    
    # 1. Lấy danh sách tất cả mã
    url_list = "https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url_list, headers=headers, timeout=30)
        data = resp.json()
        all_tickers = [item["ticker"] for item in data if "ticker" in item]
        print(f"Tổng số mã tìm thấy: {len(all_tickers)}")
    except Exception as e:
        print(f"Lỗi lấy danh sách: {e}")
        return []
    
    # 2. Lấy batch dữ liệu giá (mỗi lần 100 mã)
    batch_size = 100
    result = []
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    
    for i in range(0, len(all_tickers), batch_size):
        batch = all_tickers[i:i+batch_size]
        tickers_param = ",".join(batch)
        url_batch = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/stock/batch?ticker={tickers_param}"
        try:
            resp_batch = requests.get(url_batch, headers=headers, timeout=30)
            batch_data = resp_batch.json()
            for stock in batch_data:
                ticker = stock.get("ticker")
                price = stock.get("close", 0)
                if price == 0:
                    continue
                change = stock.get("change", 0)
                change_percent = stock.get("changePercent", 0)
                volume = stock.get("volume", 0)
                result.append({
                    "ticker": ticker,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2),
                    "volume": volume,
                    "lastUpdate": now
                })
            print(f"Batch {i//batch_size + 1}/{(len(all_tickers)-1)//batch_size + 1} thành công, tổng: {len(result)}")
        except Exception as e:
            print(f"Lỗi batch {i//batch_size + 1}: {e}")
            continue
    
    print(f"Hoàn tất. Lấy thành công {len(result)}/{len(all_tickers)} mã.")
    return result

if __name__ == "__main__":
    data = fetch_all_stocks()
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Đã lưu market_data.json")
