import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Đường dẫn tới file sales
file_path = '../datathon-2026-round-1/sales.csv'
output_dir = 'yearly_plots'

# Tạo thư mục chứa ảnh nếu chưa có
os.makedirs(output_dir, exist_ok=True)

# Đọc dữ liệu
df = pd.read_csv(file_path, parse_dates=['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Cài đặt style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

# Lấy danh sách các năm
years = sorted(df['Year'].unique())

for year in years:
    # Lọc dữ liệu theo năm
    df_year = df[df['Year'] == year].copy()
    
    # Tính Lợi nhuận (Profit = Revenue - COGS)
    df_year['Profit'] = df_year['Revenue'] - df_year['COGS']
    
    # Tính tổng doanh thu và lợi nhuận theo từng tháng
    monthly_data = df_year.groupby('Month')[['Revenue', 'Profit']].sum().reset_index()
    
    # Đảm bảo trục X luôn có đủ 12 tháng (kể cả năm 2012 bị thiếu các tháng đầu)
    all_months = pd.DataFrame({'Month': range(1, 13)})
    monthly_data = pd.merge(all_months, monthly_data, on='Month', how='left').fillna(0)
    
    # Vẽ biểu đồ
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Thiết lập vị trí các cột để vẽ bar chart song song
    width = 0.35
    x = monthly_data['Month']
    
    # Vẽ cột Doanh thu và Lợi nhuận
    ax.bar(x - width/2, monthly_data['Revenue'], width, label='Revenue (Doanh thu)', color='#2ca02c')
    ax.bar(x + width/2, monthly_data['Profit'], width, label='Profit (Lợi nhuận)', color='#ff7f0e')
    
    # Định dạng biểu đồ
    ax.set_title(f'Tổng Doanh Thu và Lợi Nhuận Theo Tháng - Năm {year}', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Tháng', fontsize=14, labelpad=10)
    ax.set_ylabel('Tổng Giá trị (VNĐ)', fontsize=14, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f'Tháng {m}' for m in x], fontsize=12)
    ax.legend(fontsize=12, loc='upper left')
    
    # Định dạng trục Y hiển thị số dạng chuỗi có dấu phẩy thay vì dạng khoa học (vd: 1e8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'sales_{year}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"Đã cập nhật và lưu thành công {len(years)} biểu đồ (Revenue vs Profit) vào thư mục: {os.path.abspath(output_dir)}")
