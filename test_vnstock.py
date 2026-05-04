# test_vnstock.py
from vnstock import Vnstock

# Khởi tạo đối tượng chính
stock = Vnstock().stock()

# 1. Lấy danh sách tất cả mã cổ phiếu
print("Danh sách 10 mã cổ phiếu đầu tiên:")
df_all = Vnstock().listing().all_symbols()
print(df_all.head(10))

# 2. Lấy dữ liệu giá lịch sử của một mã cổ phiếu
print("Dữ liệu giá 30 ngày gần nhất của mã VNINDEX:")
df_price = stock.historical.data(symbol="VNINDEX", start_date="2025-04-01", end_date="2025-05-04")
print(df_price.head())
