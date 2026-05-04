import json
import requests
from datetime import datetime, timezone, timedelta

def fetch_vn100_data():
    print("Đang lấy danh sách VN100...")
    # Danh sách 100 mã VN100 (lấy từ TCBS)
    url = "https://apipubaws.tcbs.com.vn/tcanalysis/v1/stock/insight"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()
        # Dữ liệu trả về có key "stockList" chứa các mã
        stocks = data.get("stockList", [])
        tickers = [item["ticker"] for item in stocks if "ticker" in item]
        print(f"Tìm thấy {len(tickers)} mã VN100")
    except:
        # Nếu không lấy được, dùng danh sách cố định 50 mã tiêu biểu
        tickers = ["ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
                   "MBB", "MSN", "MWG", "NVL", "POW", "SAB", "SHB", "SSI", "STB", "TCB",
                   "TPB", "VCB", "VHM", "VIC", "VJC", "VNM", "VPB", "VRE", "VIB", "VEA",
                   "DGC", "DGW", "DXG", "FTS", "GEX", "HDG", "HNG", "HSG", "IDC", "IMP",
                   "KBC", "KDH", "KOS", "KSB", "LHG", "MCH", "NKG", "NLG", "NVL", "PHR"]
        print("Dùng danh sách mặc định 50 mã")
    
    # Lấy batch dữ liệu giá
    result = []
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    
    # Chia nhỏ mỗi lần 50 mã
    batch_size = 50
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        param = ",".join(batch)
        url_price = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/stock/batch?ticker={param}"
        try:
            r = requests.get(url_price, headers=headers, timeout=30)
            batch_data = r.json()
            for item in batch_data:
                ticker = item.get("ticker")
                price = item.get("close", 0)
                if price == 0:
                    continue
                change = item.get("change", 0)
                change_pct = item.get("changePercent", 0)
                volume = item.get("volume", 0)
                # Thêm dữ liệu mẫu cho RSI, MA20 (vì API batch không cung cấp)
                result.append({
                    "ticker": ticker,
                    "price": round(price, 2),
                    "change_1d": round(change, 2),
                    "change_1d_pct": round(change_pct, 2),
                    "volume": volume,
                    "rsi": 50,  # placeholder, sẽ tính sau
                    "ma20_price": 0,
                    "volume_ratio": 100,
                    "sector": "VN100",
                    "lastUpdate": now
                })
            print(f"Batch {i//batch_size + 1} thành công")
        except Exception as e:
            print(f"Lỗi batch: {e}")
            continue
    
    # Tính thêm VNINDEX
    try:
        vnindex_url = "https://apipubaws.tcbs.com.vn/tcanalysis/v1/index/VNINDEX"
        idx_resp = requests.get(vnindex_url, headers=headers, timeout=30)
        idx_data = idx_resp.json()
        idx_price = idx_data.get("close", 1280.5)
        idx_change = idx_data.get("change", 0)
        result.insert(0, {
            "ticker": "VNINDEX",
            "price": round(idx_price, 2),
            "change_1d": round(idx_change, 2),
            "change_1d_pct": round((idx_change/idx_price)*100, 2),
            "volume": 0,
            "rsi": 50,
            "ma20_price": 0,
            "volume_ratio": 100,
            "sector": "Chỉ số",
            "lastUpdate": now
        })
    except:
        pass
    
    # Lưu file
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Tạo breadth.json đơn giản
    gainers = sum(1 for r in result if r.get("change_1d", 0) > 0)
    losers = sum(1 for r in result if r.get("change_1d", 0) < 0)
    breadth = {
        "date": now[:10],
        "total": len(result),
        "gainers": gainers,
        "losers": losers,
        "advance_decline_ratio": round(gainers/losers, 2) if losers else gainers,
        "percent_gainers": round(gainers/len(result)*100, 1) if len(result) else 0
    }
    with open("breadth.json", "w", encoding="utf-8") as f:
        json.dump(breadth, f, ensure_ascii=False, indent=2)
    
    print(f"Thành công! Đã lấy {len(result)} mã.")

if __name__ == "__main__":
    fetch_vn100_data()
