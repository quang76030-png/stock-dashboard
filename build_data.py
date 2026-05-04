import json
from datetime import datetime, timezone, timedelta
import sys
import pandas as pd

# 1. Import và cài đặt thư viện
try:
    from vnstock import Listing, Trading
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vnstock"])
    from vnstock import Listing, Trading

def fetch_all_market_data():
    """
    Lấy dữ liệu thị trường cho TẤT CẢ cổ phiếu
    """
    print("Bắt tải dữ liệu toàn thị trường...")
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")

    # 2. Lấy danh sách tất cả mã cổ phiếu
    print("Đang lấy danh sách mã cổ phiếu...")
    listing = Listing(source="vci")
    all_stocks_df = listing.all_symbols()
    all_stocks = all_stocks_df['symbol'].tolist()
    print(f"Đã tìm thấy {len(all_stocks)} mã cổ phiếu.")

    all_results = []
    batch_size = 50  # Chia làm nhiều đợt để tránh quá tải

    # 3. Chia danh sách mã thành nhiều đợt nhỏ
    for i in range(0, len(all_stocks), batch_size):
        batch = all_stocks[i:i+batch_size]
        print(f"Đang xử lý {len(batch)} mã (từ {i+1} đến {i+len(batch)})...")

        try:
            # 4. Lấy bảng giá cho một lượt các mã
            trading = Trading(source="KBS")
            price_board = trading.price_board(symbols_list=batch)

            # 5. Chuẩn hóa dữ liệu về đúng định dạng cho Dashboard
            for _, row in price_board.iterrows():
                ticker = row['symbol']
                all_results.append({
                    "ticker": ticker,
                    "price": round(row['close_price'], 2),
                    "change": round(row['price_change'], 2),
                    "changePercent": round(row['percent_change'], 2),
                    "volume": int(row.get('total_volume', 0)),
                    "lastUpdate": now
                })
            print(f"Thành công: Đã lấy dữ liệu cho {len(batch)} mã.")
        except Exception as e:
            print(f"Lỗi khi xử lý đợt mã bắt đầu với {batch[0]}: {e}")

    return all_results

def main():
    data = fetch_all_market_data()
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Hoàn tất! Đã cập nhật dữ liệu cho {len(data)} mã cổ phiếu.")

if __name__ == "__main__":
    main()
