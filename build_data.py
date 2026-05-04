import json
import time
from datetime import datetime, timezone, timedelta
from vnstock import *

def fetch_all_stocks():
    print(f"Bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Lấy danh sách tất cả mã cổ phiếu
    print("Đang tải danh sách mã...")
    all_symbols_df = listing.all_symbols()
    tickers = all_symbols_df['ticker'].tolist()
    print(f"Tổng số mã: {len(tickers)}")
    
    result = []
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. Lấy dữ liệu giá cho từng mã (có thể giới hạn số lượng nếu muốn)
    # Nếu bạn muốn giới hạn chỉ lấy top N mã, sửa dòng dưới
    # tickers = tickers[:100]  # ví dụ chỉ lấy 100 mã đầu
    
    for idx, ticker in enumerate(tickers, 1):
        try:
            # Lấy dữ liệu lịch sử 5 ngày gần nhất (để tính thay đổi)
            df = stock_historical_data(
                symbol=ticker,
                start_date=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            if df is None or len(df) < 2:
                print(f"[{idx}/{len(tickers)}] {ticker}: Không đủ dữ liệu")
                continue
            
            # Dữ liệu mới nhất và ngày trước đó
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            price = latest['close']
            change = price - prev['close']
            change_percent = (change / prev['close']) * 100
            
            result.append({
                "ticker": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "volume": int(latest['volume']),
                "lastUpdate": now
            })
            print(f"[{idx}/{len(tickers)}] ✓ {ticker}: {price} ({change_percent:+.2f}%)")
            
            # Chờ 0.2 giây để tránh quá tải API (20 requests/giây là an toàn)
            time.sleep(0.2)
            
        except Exception as e:
            print(f"[{idx}/{len(tickers)}] ✗ {ticker}: Lỗi - {str(e)[:50]}")
            continue
    
    print(f"Hoàn tất. Đã lấy thành công {len(result)}/{len(tickers)} mã.")
    return result

if __name__ == "__main__":
    data = fetch_all_stocks()
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Đã lưu vào market_data.json")
