import json
from datetime import datetime, timezone, timedelta
from vnstock import * # Gọi thư viện vnstock

def fetch_all_data():
    # 1. Lấy danh sách tất cả mã cổ phiếu
    print("Đang lấy danh sách tất cả mã...")
    all_stocks = listing.all_symbols() # all_symbols() trả về danh sách tất cả mã
    tickers_list = all_stocks['ticker'].tolist() # Chuyển cột 'ticker' thành list Python
    
    print(f"Tìm thấy {len(tickers_list)} mã cổ phiếu. Bắt đầu cập nhật giá...")
    
    result = []
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. Lặp qua từng mã và lấy dữ liệu giá mới nhất
    for ticker in tickers_list:
        try:
            # Lấy dữ liệu lịch sử 5 ngày gần nhất
            df = stock_historical_data(symbol=ticker, start_date="2024-01-01", end_date=datetime.now().strftime("%Y-%m-%d"))
            if df.empty: 
                continue
                
            # Lấy giá đóng cửa của 2 ngày gần nhất để tính thay đổi
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            result.append({
                "ticker": ticker,
                "price": round(latest['close'], 2),
                "change": round(latest['close'] - prev['close'], 2),
                "changePercent": round(((latest['close'] - prev['close']) / prev['close']) * 100, 2),
                "volume": int(latest['volume']),
                "lastUpdate": now
            })
            
            # In ra tiến độ để theo dõi
            print(f"Đã lấy xong {ticker}")
        except Exception as e:
            print(f"Lỗi khi lấy mã {ticker}: {e}")
            continue
            
    return result

if __name__ == "__main__":
    data = fetch_all_data()
    # Lưu kết quả vào file JSON
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Hoàn tất cập nhật dữ liệu cho tất cả mã!")
