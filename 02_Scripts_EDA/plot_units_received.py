import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Đường dẫn file
file_path = '../datathon-2026-round-1/inventory.csv'
output_dir = 'yearly_received_plots'

# Tạo thư mục chứa ảnh nếu chưa có
os.makedirs(output_dir, exist_ok=True)

# Đọc dữ liệu
print("Đang đọc dữ liệu inventory.csv...")
df = pd.read_csv(file_path, parse_dates=['snapshot_date'])

# Groupby theo ngày snapshot để tính tổng lượng hàng nhập về (units_received)
monthly_received = df.groupby('snapshot_date')['units_received'].sum().reset_index()

monthly_received['Year'] = monthly_received['snapshot_date'].dt.year
monthly_received['Month'] = monthly_received['snapshot_date'].dt.month

plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

years = sorted(monthly_received['Year'].unique())

for year in years:
    df_year = monthly_received[monthly_received['Year'] == year].copy()
    
    # Đảm bảo đủ 12 tháng
    all_months = pd.DataFrame({'Month': range(1, 13)})
    df_year = pd.merge(all_months, df_year, on='Month', how='left').fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Vẽ Bar chart cho số lượng nhập
    sns.barplot(data=df_year, x='Month', y='units_received', color='#2ecc71', ax=ax)
    
    # Vẽ thêm đường Line nối các đỉnh cột để dễ nhìn xu hướng
    ax.plot(df_year['Month'] - 1, df_year['units_received'], color='#27ae60', marker='o', linewidth=2)
    
    ax.set_title(f'Tổng Số Lượng Hàng Nhập Kho Theo Tháng - Năm {year}', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Tháng', fontsize=12)
    ax.set_ylabel('Số lượng nhập (Units Received)', fontsize=12)
    ax.set_xticks(range(0, 12))
    ax.set_xticklabels([f'Thg {m}' for m in range(1, 13)])
    
    # Ghi số trực tiếp lên cột
    for i, val in enumerate(df_year['units_received']):
        if val > 0:
            ax.text(i, val + (df_year['units_received'].max() * 0.02), f"{int(val):,}", 
                    ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
                    
    # Format trục Y có dấu phẩy
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'received_{year}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"Đã lưu thành công {len(years)} biểu đồ Hàng Nhập vào thư mục: {os.path.abspath(output_dir)}")
