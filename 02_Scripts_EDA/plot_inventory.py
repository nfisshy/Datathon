import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Đường dẫn file
file_path = '../datathon-2026-round-1/inventory.csv'
output_dir = 'yearly_inventory_plots'

# Tạo thư mục chứa ảnh nếu chưa có
os.makedirs(output_dir, exist_ok=True)

# Đọc dữ liệu
print("Đang đọc và xử lý dữ liệu inventory.csv...")
df = pd.read_csv(file_path, parse_dates=['snapshot_date'])

# Groupby theo ngày snapshot để lấy tổng toàn bộ sản phẩm
monthly_inv = df.groupby('snapshot_date')[['stock_on_hand', 'units_received', 'units_sold']].sum().reset_index()

# Lấy năm và tháng
monthly_inv['Year'] = monthly_inv['snapshot_date'].dt.year
monthly_inv['Month'] = monthly_inv['snapshot_date'].dt.month

# Cài đặt style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

years = sorted(monthly_inv['Year'].unique())

for year in years:
    df_year = monthly_inv[monthly_inv['Year'] == year].copy()
    
    # Đảm bảo đủ 12 tháng
    all_months = pd.DataFrame({'Month': range(1, 13)})
    df_year = pd.merge(all_months, df_year, on='Month', how='left').fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    width = 0.3
    x = df_year['Month']
    
    # Vẽ Tồn kho bằng biểu đồ đường/vùng (Line/Area chart) để làm nền dài hạn
    ax.plot(x, df_year['stock_on_hand'], color='#34495e', linewidth=3, marker='o', markersize=8, label='Tồn kho cuối tháng (Stock on Hand)')
    ax.fill_between(x, df_year['stock_on_hand'], color='#bdc3c7', alpha=0.3)
    
    # Vẽ Nhập hàng và Bán ra bằng Bar chart song song
    ax.bar(x - width/2, df_year['units_received'], width, label='Nhập kho mới (Units Received)', color='#2ecc71', alpha=0.85)
    ax.bar(x + width/2, df_year['units_sold'], width, label='Đã bán ra (Units Sold)', color='#e74c3c', alpha=0.85)
    
    # Định dạng
    ax.set_title(f'Bức Tranh Dòng Chảy Tồn Kho: Nhập - Bán - Tồn Cuối Tháng (Năm {year})', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Tháng', fontsize=14, labelpad=10)
    ax.set_ylabel('Số lượng sản phẩm (Units)', fontsize=14, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f'Tháng {m}' for m in x], fontsize=12)
    ax.legend(fontsize=12, loc='upper right')
    
    # Format trục y có dấu phẩy
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'inventory_flow_{year}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"Đã lưu thành công {len(years)} biểu đồ Tồn Kho (Nhập/Bán/Tồn) vào thư mục: {os.path.abspath(output_dir)}")
