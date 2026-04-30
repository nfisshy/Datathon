import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# 1. Đọc dữ liệu
print("Đang đọc dữ liệu sales.csv...")
sales = pd.read_csv('../datathon-2026-round-1/sales.csv', parse_dates=['Date'])

# 2. Tạo cột YearMonth để nhóm
sales['YearMonth'] = sales['Date'].dt.to_period('M').dt.to_timestamp()
sales['Profit'] = sales['Revenue'] - sales['COGS']

# 3. Tính tổng theo tháng liên tục
monthly_sales = sales.groupby('YearMonth')[['Revenue', 'Profit']].sum().reset_index()

# 4. Vẽ biểu đồ
plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(20, 8))

# Vẽ Line Doanh Thu
ax.plot(monthly_sales['YearMonth'], monthly_sales['Revenue'] / 1e9, 
        color='#3498db', linewidth=2.5, label='Doanh Thu (Revenue)')

# Vẽ Line Lợi Nhuận
ax.plot(monthly_sales['YearMonth'], monthly_sales['Profit'] / 1e9, 
        color='#e74c3c', linewidth=2.5, label='Lợi Nhuận (Profit)')

# Fill màu vùng lợi nhuận âm để dễ nhìn
ax.fill_between(monthly_sales['YearMonth'], 0, monthly_sales['Profit'] / 1e9, 
                where=(monthly_sales['Profit'] < 0), color='black', alpha=0.3, label='Tháng Lỗ')

# Đường baseline 0
ax.axhline(0, color='black', linewidth=1.5, linestyle='--')

ax.set_title('BỨC TRANH TOÀN CẢNH DOANH THU & LỢI NHUẬN (2012 - 2022)', fontsize=20, fontweight='bold', pad=20)
ax.set_ylabel('Tỷ VND', fontsize=14, fontweight='bold')
ax.set_xlabel('Thời Gian (Năm)', fontsize=14, fontweight='bold')

# Format trục X hiển thị từng năm
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3)) # Đánh dấu mỗi quý

# Grid
ax.grid(True, which='major', linestyle='-', linewidth='0.5', color='black', alpha=0.3)
ax.grid(True, which='minor', linestyle=':', linewidth='0.5', color='gray', alpha=0.3)

ax.legend(fontsize=14, loc='upper left')

plt.tight_layout()
output_path = 'continuous_sales_trend.png'
plt.savefig(output_path, dpi=300)
print(f"Đã lưu biểu đồ thành công: {output_path}")
