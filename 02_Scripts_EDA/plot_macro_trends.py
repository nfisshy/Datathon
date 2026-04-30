import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

print("Đang đọc dữ liệu...")
sales = pd.read_csv('../datathon-2026-round-1/sales.csv', parse_dates=['Date'])
customers = pd.read_csv('../datathon-2026-round-1/customers.csv', parse_dates=['signup_date'])
web_traffic = pd.read_csv('../datathon-2026-round-1/web_traffic.csv', parse_dates=['date'])
inventory = pd.read_csv('../datathon-2026-round-1/inventory.csv', parse_dates=['snapshot_date'])

print("Đang tổng hợp dữ liệu theo năm...")
# 1. Xử lý Revenue & Profit
sales['Year'] = sales['Date'].dt.year
sales['Profit'] = sales['Revenue'] - sales['COGS']
sales_yearly = sales.groupby('Year')[['Revenue', 'Profit']].sum().reset_index()

# 2. Xử lý Khách hàng (Cumulative Signups)
customers['Year'] = customers['signup_date'].dt.year
cust_yearly = customers.groupby('Year').size().reset_index(name='New_Signups')
cust_yearly['Cumulative_Customers'] = cust_yearly['New_Signups'].cumsum()

# 3. Xử lý Web Traffic
web_traffic['Year'] = web_traffic['date'].dt.year
web_yearly = web_traffic.groupby('Year')['sessions'].sum().reset_index()

# 4. Xử lý Inventory (Trung bình tồn kho mỗi năm)
# Tính tổng tồn kho của toàn bộ sản phẩm tại mỗi thời điểm cuối tháng
inv_monthly = inventory.groupby(['snapshot_date'])['stock_on_hand'].sum().reset_index()
inv_monthly['Year'] = inv_monthly['snapshot_date'].dt.year
# Lấy trung bình của 12 tháng trong năm đó
inv_yearly = inv_monthly.groupby('Year')['stock_on_hand'].mean().reset_index(name='Avg_Stock_On_Hand')

# 5. Merge tất cả lại
df_trend = sales_yearly.merge(cust_yearly, on='Year', how='left')
df_trend = df_trend.merge(web_yearly, on='Year', how='left')
df_trend = df_trend.merge(inv_yearly, on='Year', how='left')

print("Đang vẽ biểu đồ...")
# Vẽ biểu đồ 5 subplots
fig, axes = plt.subplots(5, 1, figsize=(14, 20), sharex=True)
plt.style.use('ggplot')

years = df_trend['Year']

def add_values_to_line(ax, x, y, format_str):
    for i, j in zip(x, y):
        if not np.isnan(j):
            ax.text(i, j + (max(y.dropna()) * 0.05), format_str.format(j), 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

# Plot 1: Revenue
axes[0].plot(years, df_trend['Revenue'] / 1e9, color='#2980b9', marker='o', linewidth=3, markersize=8)
axes[0].set_title('Tổng Doanh Thu (Tỷ VND)', fontsize=16, fontweight='bold', pad=15)
axes[0].set_ylabel('Tỷ VND', fontsize=12)
add_values_to_line(axes[0], years, df_trend['Revenue'] / 1e9, "{:.0f}")

# Plot 2: Profit
axes[1].plot(years, df_trend['Profit'] / 1e9, color='#27ae60', marker='o', linewidth=3, markersize=8)
axes[1].set_title('Tổng Lợi Nhuận (Tỷ VND)', fontsize=16, fontweight='bold', pad=15)
axes[1].set_ylabel('Tỷ VND', fontsize=12)
add_values_to_line(axes[1], years, df_trend['Profit'] / 1e9, "{:.0f}")

# Plot 3: Cumulative Customers
axes[2].plot(years, df_trend['Cumulative_Customers'] / 1000, color='#8e44ad', marker='o', linewidth=3, markersize=8)
axes[2].set_title('Quy Mô Tập Khách Hàng Tích Lũy (Nghìn Người)', fontsize=16, fontweight='bold', pad=15)
axes[2].set_ylabel('Nghìn Người', fontsize=12)
add_values_to_line(axes[2], years, df_trend['Cumulative_Customers'] / 1000, "{:.0f}")

# Plot 4: Web Traffic
axes[3].plot(years, df_trend['sessions'] / 1e6, color='#e67e22', marker='o', linewidth=3, markersize=8)
axes[3].set_title('Tổng Lượt Truy Cập Web (Triệu Sessions)', fontsize=16, fontweight='bold', pad=15)
axes[3].set_ylabel('Triệu Lượt', fontsize=12)
add_values_to_line(axes[3], years, df_trend['sessions'] / 1e6, "{:.1f}")

# Plot 5: Average Inventory
axes[4].plot(years, df_trend['Avg_Stock_On_Hand'] / 1000, color='#c0392b', marker='o', linewidth=3, markersize=8)
axes[4].set_title('Trung Bình Lượng Tồn Kho Mỗi Tháng Trong Năm (Nghìn Sản Phẩm)', fontsize=16, fontweight='bold', pad=15)
axes[4].set_ylabel('Nghìn SP', fontsize=12)
axes[4].set_xlabel('Năm', fontsize=14)
add_values_to_line(axes[4], years, df_trend['Avg_Stock_On_Hand'] / 1000, "{:.0f}")

# Format x axis
axes[4].set_xticks(years)
axes[4].set_xticklabels([str(int(y)) for y in years], fontsize=12)

# Thêm giới hạn trên cho các trục Y để text không bị cắt
for ax in axes:
    ax.grid(True, linestyle='--', alpha=0.7)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax * 1.15)

plt.tight_layout()
plt.savefig('macro_trends_yearly.png', dpi=300)
print("Đã lưu biểu đồ thành công: macro_trends_yearly.png")
