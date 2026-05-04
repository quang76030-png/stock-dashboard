import json
import requests
from datetime import datetime, timezone, timedelta

def fetch_all_stocks_tcbs():
    print(f"Bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Lấy danh sách tất cả mã cổ phiếu từ TCBS
    url_list = "https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url_list, headers=headers, timeout=30)
        data = response.json()
        # Dữ liệu trả về là list các object, mỗi object có key "ticker"
        tickers = [item["ticker"] for item in data if "ticker" in item]
        print(f"Tổng số mã lấy được: {len(tickers)}")
    except Exception as e:
        print(f"Lỗi lấy danh sách mã: {e}")
        return []
    
    # 2. Lấy giá hiện tại cho từng mã (giá tham chiếu cuối ngày)
    result = []
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    
    # Giới hạn số lượng để tránh timeout (có thể lấy 50-100 mã đầu, hoặc toàn bộ nhưng chậm)
    # Bạn có thể lấy toàn bộ nhưng sẽ mất vài phút
    # Ở đây mình lấy 100 mã đầu để test. Sau khi chạy ok, bạn sửa thành tickers (toàn bộ)
    tickers_limit = tickers[:100]  # 👈 SỬA LẠI THÀNH tickers NẾU MUỐN LẤY TẤT CẢ
    
    for idx, ticker in enumerate(tickers_limit, 1):
        try:
            url_price = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/stock/{ticker}/yearly"
            res = requests.get(url_price, headers=headers, timeout=10)
            if res.status_code != 200:
                print(f"[{idx}/{len(tickers_limit)}] {ticker}: Không có dữ liệu")
                continue
            data_price = res.json()
            if not data_price or len(data_price) < 2:
                print(f"[{idx}/{len(tickers_limit)}] {ticker}: Không đủ dữ liệu")
                continue
            
            # Lấy giá đóng cửa ngày gần nhất và ngày trước đó
            latest = data_price[-1]
            prev = data_price[-2]
            price = latest.get("close", 0)
            prev_close = prev.get("close", 0)
            if prev_close == 0:
                continue
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            volume = latest.get("volume", 0)
            
            result.append({
                "ticker": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "volume": volume,
                "lastUpdate": now
            })
            print(f"[{idx}/{len(tickers_limit)}] ✓ {ticker}: {price} ({change_percent:+.2f}%)")
        except Exception as e:
            print(f"[{idx}/{len(tickers_limit)}] ✗ {ticker}: {str(e)[:50]}")
            continue
    
    print(f"Hoàn tất. Đã lấy thành công {len(result)}/{len(tickers_limit)} mã.")
    return result

if __name__ == "__main__":
    data = fetch_all_stocks_tcbs()
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Đã lưu vào market_data.json")
