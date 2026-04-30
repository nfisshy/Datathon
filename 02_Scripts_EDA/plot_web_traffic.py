import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

file_path = '../datathon-2026-round-1/web_traffic.csv'
output_dir = 'yearly_web_traffic_plots'

os.makedirs(output_dir, exist_ok=True)

print("Đang đọc dữ liệu web_traffic.csv...")
df = pd.read_csv(file_path, parse_dates=['date'])

df['Year'] = df['date'].dt.year
df['Month'] = df['date'].dt.month

# Tính tổng sessions theo tháng
monthly_traffic = df.groupby(['Year', 'Month'])['sessions'].sum().reset_index()

plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

years = sorted(monthly_traffic['Year'].unique())

for year in years:
    df_year = monthly_traffic[monthly_traffic['Year'] == year].copy()
    
    # Đảm bảo đủ 12 tháng
    all_months = pd.DataFrame({'Month': range(1, 13)})
    df_year = pd.merge(all_months, df_year, on='Month', how='left').fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot Traffic
    sns.barplot(data=df_year, x='Month', y='sessions', color='#3498db', ax=ax)
    ax.plot(df_year['Month'] - 1, df_year['sessions'], color='#2980b9', marker='o', linewidth=2)
    
    ax.set_title(f'Tổng Lượt Truy Cập (Sessions) Theo Tháng - Năm {year}', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Tháng', fontsize=12)
    ax.set_ylabel('Số Lượt Truy Cập (Sessions)', fontsize=12)
    ax.set_xticks(range(0, 12))
    ax.set_xticklabels([f'Thg {m}' for m in range(1, 13)])
    
    # Thêm số liệu lên đỉnh cột
    for i, val in enumerate(df_year['sessions']):
        if val > 0:
            ax.text(i, val + (df_year['sessions'].max() * 0.02), f"{int(val):,}", 
                    ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
                    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'web_traffic_{year}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"Đã lưu thành công {len(years)} biểu đồ lưu lượng web vào thư mục: {os.path.abspath(output_dir)}")
