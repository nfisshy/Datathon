import pandas as pd
import numpy as np

# Đọc dữ liệu
sales = pd.read_csv('../datathon-2026-round-1/sales.csv', parse_dates=['Date'])
sales['Year'] = sales['Date'].dt.year
sales['Month'] = sales['Date'].dt.month

inv = pd.read_csv('../datathon-2026-round-1/inventory.csv', parse_dates=['snapshot_date'])
inv['Year'] = inv['snapshot_date'].dt.year
inv['Month'] = inv['snapshot_date'].dt.month

# Lọc dữ liệu từ tháng 1 đến tháng 7 (Trước thời điểm diễn ra chiến dịch Xả kho tháng 8)
sales_h1 = sales[sales['Month'] <= 7].groupby('Year')['Revenue'].sum().reset_index()
sales_h1['Is_Odd_Year'] = sales_h1['Year'] % 2 != 0

inv_h1 = inv[inv['Month'] <= 7].groupby('Year')[['units_received', 'units_sold']].sum().reset_index()
inv_h1['Is_Odd_Year'] = inv_h1['Year'] % 2 != 0

# Merge
df = pd.merge(sales_h1, inv_h1, on=['Year', 'Is_Odd_Year'])

# Tính toán so sánh
print("==================================================================")
print("SO SÁNH GIAI ĐOẠN TÍCH LŨY (THÁNG 1 -> THÁNG 7) TRƯỚC KHI XẢ KHO")
print("==================================================================")
summary = df.groupby('Is_Odd_Year').agg(
    Avg_Revenue=('Revenue', 'mean'),
    Avg_Units_Received=('units_received', 'mean'),
    Avg_Units_Sold=('units_sold', 'mean')
).reset_index()

summary['Is_Odd_Year'] = summary['Is_Odd_Year'].map({True: 'Năm LẺ (Bị overstock)', False: 'Năm CHẴN (Bán tốt)'})
summary['Over_Ordering_Ratio'] = summary['Avg_Units_Received'] / summary['Avg_Units_Sold']

print(summary)
