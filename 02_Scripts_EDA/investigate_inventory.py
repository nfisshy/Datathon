import pandas as pd
import numpy as np

print("Đang đọc và xử lý dữ liệu...")
# Đọc sales và tính Profit theo tháng
sales = pd.read_csv('../datathon-2026-round-1/sales.csv', parse_dates=['Date'])
sales['Month_Period'] = sales['Date'].dt.to_period('M')
sales['Profit'] = sales['Revenue'] - sales['COGS']

monthly_sales = sales.groupby('Month_Period')[['Revenue', 'COGS', 'Profit']].sum().reset_index()
monthly_sales['Profit_Margin'] = monthly_sales['Profit'] / monthly_sales['Revenue']

# Đọc inventory
inv = pd.read_csv('../datathon-2026-round-1/inventory.csv', parse_dates=['snapshot_date'])
inv['Month_Period'] = inv['snapshot_date'].dt.to_period('M')

monthly_inv = inv.groupby('Month_Period').agg(
    stock_on_hand=('stock_on_hand', 'sum'),
    overstock_pct=('overstock_flag', 'mean'),
    stockout_pct=('stockout_flag', 'mean'),
    fill_rate=('fill_rate', 'mean')
).reset_index()

# Merge
df = pd.merge(monthly_sales, monthly_inv, on='Month_Period', how='inner')

# Create Lag features for inventory (Tồn kho tháng trước ảnh hưởng lợi nhuận tháng này)
df['stock_on_hand_lag1'] = df['stock_on_hand'].shift(1)
df['overstock_pct_lag1'] = df['overstock_pct'].shift(1)
df['stockout_pct_lag1'] = df['stockout_pct'].shift(1)

# Drop NaN from shift
df = df.dropna()

print("\n=========================================================")
print("1. HỆ SỐ TƯƠNG QUAN (CORRELATION) GIỮA TỒN KHO VÀ KINH DOANH")
print("=========================================================")
corr_cols = [
    'stock_on_hand', 'overstock_pct', 'stockout_pct', 'fill_rate',
    'stock_on_hand_lag1', 'overstock_pct_lag1', 'stockout_pct_lag1'
]
corr_matrix = df[['Profit', 'Profit_Margin', 'Revenue'] + corr_cols].corr()
print(corr_matrix.loc[corr_cols, ['Profit', 'Profit_Margin', 'Revenue']].round(3))

print("\n=========================================================")
print("2. TÁC ĐỘNG CỦA TÌNH TRẠNG 'OVERSTOCK' THÁNG TRƯỚC ĐẾN THÁNG NÀY")
print("=========================================================")
# Chia làm 2 nhóm: Tháng trước tồn kho vượt mức (Cao) và Bình thường (Thấp)
median_overstock = df['overstock_pct_lag1'].median()
df['Overstock_Lag1_Level'] = np.where(df['overstock_pct_lag1'] > median_overstock, 'Cao (Nhiều hàng ế)', 'Thấp (Bình thường)')

impact = df.groupby('Overstock_Lag1_Level').agg(
    Avg_Profit_Margin=('Profit_Margin', lambda x: f"{x.mean()*100:.2f}%"),
    Avg_Revenue=('Revenue', 'mean'),
    Avg_Profit=('Profit', 'mean')
).reset_index()
print(impact)

print("\n=========================================================")
print("3. PHÂN TÍCH NHỮNG THÁNG LỖ NẶNG NHẤT (PROFIT MARGIN < 0)")
print("=========================================================")
loss_months = df[df['Profit_Margin'] < 0].copy()
print(loss_months[['Month_Period', 'Profit_Margin', 'overstock_pct_lag1', 'stock_on_hand_lag1']].sort_values('Profit_Margin').head(5))
