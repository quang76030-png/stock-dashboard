# build_data.py
import json
import pandas as pd
from datetime import datetime, timedelta
from vnstock import Vnstock

def fetch_and_process_data():
    """Hàm chính để lấy và xử lý dữ liệu thị trường."""
    print("🚀 Bắt đầu quá trình lấy dữ liệu...")
    
    # 1. Lấy danh sách cổ phiếu
    print("Bước 1: Lấy danh sách cổ phiếu...")
    listing_data = Vnstock().listing().all_symbols()
    all_tickers = listing_data['ticker'].tolist()
    print(f"   > Đã tìm thấy {len(all_tickers)} mã cổ phiếu.")
    
    # *** GIỚI HẠN 50 MÃ ĐỂ TEST ***
    tickers_to_process = all_tickers[:50]
    
    final_data = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("Bước 2: Bắt đầu lấy dữ liệu cho 50 mã đầu tiên...")
    for index, ticker in enumerate(tickers_to_process):
        try:
            # 2. Lấy dữ liệu giá lịch sử cho mỗi mã
            historical_data = Vnstock().stock().historical.data(
                symbol=ticker,
                start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            if historical_data is not None and len(historical_data) > 0:
                # Lấy giá mới nhất
                latest_price = historical_data['close'].iloc[-1]
                # Tính % thay đổi (ví dụ: so với ngày hôm qua)
                if len(historical_data) > 1:
                    prev_price = historical_data['close'].iloc[-2]
                    change_percent = round((latest_price - prev_price) / prev_price * 100, 2)
                else:
                    change_percent = 0
                
                # Lưu thông tin cơ bản
                final_data.append({
                    "ticker": ticker,
                    "price": round(latest_price, 2),
                    "changePercent": change_percent,
                    "volume": int(historical_data['volume'].iloc[-1]),
                    "lastUpdate": current_time
                })
                print(f"   > [{index+1}/{len(tickers_to_process)}] Đã xử lý thành công mã {ticker}")
            else:
                print(f"   > [{index+1}/{len(tickers_to_process)}] Không có dữ liệu cho mã {ticker}")
                
        except Exception as e:
            print(f"   > ❌ Lỗi khi xử lý mã {ticker}: {str(e)}")
            continue
    
    # 3. Lưu kết quả vào file JSON
    with open("market_data.json", "w") as file:
        json.dump(final_data, file, indent=2)
    
    print("✅ Quá trình hoàn tất! Dữ liệu đã được lưu vào file market_data.json.")

if __name__ == "__main__":
    fetch_and_process_data()
