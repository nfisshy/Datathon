import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Đường dẫn
sales_path = '../datathon-2026-round-1/sales.csv'
output_dir = 'yearly_daily_sales_plots'

os.makedirs(output_dir, exist_ok=True)

# Đọc dữ liệu
print("Đang đọc dữ liệu sales.csv...")
df = pd.read_csv(sales_path, parse_dates=['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayOfWeek'] = df['Date'].dt.dayofweek # 0=Monday, 6=Sunday
df['DayName'] = df['Date'].dt.day_name()

# 1. Vẽ biểu đồ daily theo từng năm
years = sorted(df['Year'].dropna().unique())
plt.style.use('ggplot')

import matplotlib.dates as mdates

def get_holidays(year):
    """Trả về dictionary chứa các ngày lễ cố định trong năm"""
    holidays = {
        'New Year': pd.Timestamp(year, 1, 1),
        'Valentine': pd.Timestamp(year, 2, 14),
        'Women Day': pd.Timestamp(year, 3, 8),
        'Lễ 30/4': pd.Timestamp(year, 4, 30),
        'Lễ 1/5': pd.Timestamp(year, 5, 1),
        'Quốc Khánh': pd.Timestamp(year, 9, 2),
        'Black Friday': pd.date_range(f'{year}-11-01', f'{year}-11-30', freq='W-FRI')[3],
        'Christmas': pd.Timestamp(year, 12, 25)
    }
    return holidays

for year in years:
    df_year = df[df['Year'] == year].copy()
    
    # Tăng kích thước chiều ngang để chứa đủ 365 ngày
    fig, ax = plt.subplots(figsize=(40, 8))
    
    ax.plot(df_year['Date'], df_year['Revenue'] / 1e6, color='#2980b9', linewidth=1.5, label='Doanh thu hàng ngày')
    
    # Highlight các ngày có doanh thu đột biến (Top 5% của năm đó)
    threshold = df_year['Revenue'].quantile(0.95)
    spikes = df_year[df_year['Revenue'] > threshold]
    ax.scatter(spikes['Date'], spikes['Revenue'] / 1e6, color='#e74c3c', zorder=5, s=60, label='Ngày bùng nổ (Top 5%)')
    
    # --- ĐỊNH DẠNG TRỤC X ĐA TẦNG (NGÀY -> TUẦN -> THÁNG) ---
    # 1. Cấp độ Tháng (Major ticks) - Hiển thị phía dưới cùng
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('\n\nTháng %m'))
    ax.tick_params(axis='x', which='major', labelsize=16, labelcolor='black')
    
    # 2. Cấp độ Ngày (Minor ticks) - Hiển thị ngay sát trục X
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    ax.tick_params(axis='x', which='minor', labelsize=10, rotation=90)
    
    # 3. Cấp độ Tuần - Kẻ đường sọc dọc màu xanh phân chia mỗi Thứ Hai
    mondays = pd.date_range(start=df_year['Date'].min(), end=df_year['Date'].max(), freq='W-MON')
    for monday in mondays:
        ax.axvline(x=monday, color='#27ae60', linestyle='--', alpha=0.5, linewidth=1.5)
        
    # Đường phân ranh giới Tháng (Đậm hơn)
    for month_start in pd.date_range(start=df_year['Date'].min(), end=df_year['Date'].max(), freq='MS'):
        ax.axvline(x=month_start, color='black', linestyle='-', alpha=0.8, linewidth=2)
    
    # 4. Hiển thị các ngày Lễ (Holidays)
    holidays = get_holidays(year)
    y_max = df_year['Revenue'].max() / 1e6
    for h_name, h_date in holidays.items():
        if df_year['Date'].min() <= h_date <= df_year['Date'].max():
            ax.axvline(x=h_date, color='#8e44ad', linestyle='-.', alpha=0.9, linewidth=2)
            # Thêm Text nhãn ngày lễ
            ax.text(h_date, y_max * 0.95, f' {h_name}', color='#8e44ad', rotation=90, 
                    verticalalignment='top', horizontalalignment='right', 
                    fontsize=14, fontweight='bold', backgroundcolor='white')
    
    ax.set_title(f'BIẾN ĐỘNG DOANH THU HÀNG NGÀY - NĂM {year}', fontsize=22, fontweight='bold', pad=20)
    ax.set_ylabel('Doanh thu (Triệu VNĐ)', fontsize=16, fontweight='bold')
    
    # Thêm chú thích cho Tuần và Lễ
    import matplotlib.lines as mlines
    week_line = mlines.Line2D([], [], color='#27ae60', linestyle='--', label='Bắt đầu Tuần mới (Thứ 2)')
    month_line = mlines.Line2D([], [], color='black', linestyle='-', linewidth=2, label='Chuyển Tháng')
    holiday_line = mlines.Line2D([], [], color='#8e44ad', linestyle='-.', linewidth=2, label='Ngày Lễ (Holidays)')
    handles, labels = ax.get_legend_handles_labels()
    handles.extend([week_line, month_line, holiday_line])
    ax.legend(handles=handles, loc='upper right', fontsize=14)
    
    # Lưới ngang trục Y
    ax.grid(True, which='major', axis='y', linestyle=':', color='gray', alpha=0.7)
    # Tắt lưới dọc mặc định vì đã vẽ custom vline
    ax.grid(False, axis='x')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'daily_sales_{year}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

print(f"Đã lưu {len(years)} biểu đồ daily sales vào thư mục: {os.path.abspath(output_dir)}")

# 2. Phân tích thống kê để rút ra xu hướng
print("\n--- TRUNG BÌNH DOANH THU THEO THỨ TRONG TUẦN (Triệu VNĐ) ---")
# Tính trung bình doanh thu mỗi ngày trong tuần qua tất cả các năm
dow_stats = df.groupby('DayName')['Revenue'].mean().sort_values(ascending=False)
for name, val in dow_stats.items():
    print(f"{name:10}: {val/1e6:,.0f} Triệu")

print("\n--- TOP 10 NGÀY TRONG THÁNG CÓ DOANH THU CAO NHẤT (Triệu VNĐ) ---")
# Tính trung bình doanh thu mỗi ngày trong tháng
dom_stats = df.groupby('Day')['Revenue'].mean().sort_values(ascending=False).head(10)
for name, val in dom_stats.items():
    print(f"Ngày {name:2}: {val/1e6:,.0f} Triệu")

print("\n--- TOP 10 NGÀY BÁN CHẠY NHẤT TRONG NĂM (Tính theo trung bình lịch sử) ---")
# Tính trung bình theo từng ngày cụ thể trong năm (ví dụ: ngày 15/04)
doy_stats = df.groupby(['Month', 'Day'])['Revenue'].mean().reset_index()
doy_stats = doy_stats.sort_values(by='Revenue', ascending=False).head(10)
for idx, row in doy_stats.iterrows():
    print(f"Ngày {int(row['Day']):02d} Tháng {int(row['Month']):02d}: {row['Revenue']/1e6:,.0f} Triệu")
