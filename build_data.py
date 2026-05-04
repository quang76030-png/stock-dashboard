import json
import requests
import time
from datetime import datetime, timezone, timedelta
import os

# Hàm lấy danh sách mã và ngành (từ TCBS)
def get_all_tickers_and_sector():
    url_list = "https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url_list, headers=headers, timeout=30)
        data = resp.json()
        # Trả về list dict: {"ticker":..., "sector":...}
        # Lưu ý: TCBS trả về "industry" hoặc "sector"
        stocks = []
        for item in data:
            ticker = item.get("ticker")
            sector = item.get("industryName", "Khác")
            if ticker and sector:
                stocks.append({"ticker": ticker, "sector": sector})
        return stocks
    except Exception as e:
        print(f"Lỗi lấy danh sách mã: {e}")
        return []

# Hàm lấy dữ liệu giá lịch sử 50 ngày cho một mã
def get_historical_data(ticker, days=50):
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/stock/{ticker}/yearly"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        # Dữ liệu trả về list các ngày, mỗi ngày có close, volume
        if not data:
            return []
        # Lấy `days` ngày gần nhất
        return data[-days:] if len(data) >= days else data
    except:
        return []

# Tính RSI (14 ngày)
def calculate_rsi(prices, period=14):
    if len(prices) < period+1:
        return 50
    gains = []
    losses = []
    for i in range(1, period+1):
        change = prices[i] - prices[i-1]
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = sum(gains)/period
    avg_loss = sum(losses)/period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return round(rsi, 2)

# Tính MA (trung bình trượt)
def calculate_ma(values, period):
    if len(values) < period:
        return None
    return round(sum(values[-period:])/period, 2)

def main():
    print("=== BẮT ĐẦU CẬP NHẬT DỮ LIỆU ===")
    stocks_info = get_all_tickers_and_sector()
    if not stocks_info:
        print("Không thể lấy danh sách mã. Dừng.")
        return
    print(f"Tổng số mã: {len(stocks_info)}")
    
    # Giới hạn để test nhanh: lấy 50 mã đầu thôi. Sau đó có thể bỏ comment để lấy tất cả
    # stocks_info = stocks_info[:50]  # 👈 Bạn có thể bỏ comment này để test
    
    results = []
    for idx, stock in enumerate(stocks_info, 1):
        ticker = stock["ticker"]
        sector = stock["sector"]
        hist = get_historical_data(ticker, days=50)
        if len(hist) < 20:  # Cần ít nhất 20 ngày để tính MA20
            print(f"[{idx}/{len(stocks_info)}] {ticker}: không đủ dữ liệu")
            continue
        
        # Trích xuất danh sách giá đóng cửa và volume
        closes = [day["close"] for day in hist]
        volumes = [day["volume"] for day in hist]
        
        # Giá và volume hiện tại
        last_price = closes[-1]
        last_volume = volumes[-1]
        
        # MA20 (giá)
        ma20_price = calculate_ma(closes, 20) if len(closes) >= 20 else None
        # MA10 (giá)
        ma10_price = calculate_ma(closes, 10) if len(closes) >= 10 else None
        # MA20 volume
        ma20_volume = calculate_ma(volumes, 20) if len(volumes) >= 20 else None
        # % volume so với MA20
        volume_ratio = round((last_volume / ma20_volume)*100, 1) if ma20_volume and ma20_volume > 0 else 0
        
        # RSI 14 ngày
        rsi = calculate_rsi(closes, 14)
        
        # Thay đổi giá 1 ngày, 5 ngày, 20 ngày
        change_1d = round(last_price - closes[-2], 2) if len(closes) >= 2 else 0
        change_1d_pct = round((change_1d/closes[-2])*100, 2) if len(closes) >= 2 and closes[-2]!=0 else 0
        change_5d = round(last_price - closes[-6], 2) if len(closes) >= 6 else 0
        change_20d = round(last_price - closes[-21], 2) if len(closes) >= 21 else 0
        
        results.append({
            "ticker": ticker,
            "sector": sector,
            "price": last_price,
            "change_1d": change_1d,
            "change_1d_pct": change_1d_pct,
            "change_5d": change_5d,
            "change_20d": change_20d,
            "volume": last_volume,
            "ma10_price": ma10_price,
            "ma20_price": ma20_price,
            "ma20_volume": ma20_volume,
            "volume_ratio": volume_ratio,
            "rsi": rsi,
            "lastUpdate": datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"[{idx}/{len(stocks_info)}] ✓ {ticker} | Giá:{last_price} | RSI:{rsi} | Vol ratio:{volume_ratio}%")
        time.sleep(0.05)  # Tránh quá tải
    
    # Lưu kết quả vào market_data.json (để web đọc)
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Tổng hợp độ rộng thị trường
    total = len(results)
    gainers = sum(1 for r in results if r["change_1d"] > 0)
    losers = sum(1 for r in results if r["change_1d"] < 0)
    unchanged = total - gainers - losers
    advance_decline_ratio = round(gainers / losers, 2) if losers > 0 else gainers
    
    # Lưu thêm file breadth.json cho dashboard
    breadth = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total": total,
        "gainers": gainers,
        "losers": losers,
        "unchanged": unchanged,
        "advance_decline_ratio": advance_decline_ratio,
        "percent_gainers": round(gainers/total*100, 1) if total else 0
    }
    with open("breadth.json", "w", encoding="utf-8") as f:
        json.dump(breadth, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== HOÀN TẤT ===")
    print(f"Đã lấy {len(results)} mã.")
    print(f"Độ rộng: Tăng {gainers}, Giảm {losers}, Tỷ lệ tăng/giảm: {advance_decline_ratio}")

if __name__ == "__main__":
    main()
