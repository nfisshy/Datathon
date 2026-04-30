import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

file_path = '../datathon-2026-round-1/customers.csv'
output_dir = 'yearly_signup_plots'

os.makedirs(output_dir, exist_ok=True)

print("Đang đọc dữ liệu customers.csv...")
df = pd.read_csv(file_path, parse_dates=['signup_date'])

df['Year'] = df['signup_date'].dt.year
df['Month'] = df['signup_date'].dt.month

# Đếm số lượng khách hàng đăng ký mới theo tháng
monthly_signups = df.groupby(['Year', 'Month'])['customer_id'].count().reset_index()
monthly_signups.rename(columns={'customer_id': 'new_customers'}, inplace=True)

plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

years = sorted(monthly_signups['Year'].unique())

for year in years:
    df_year = monthly_signups[monthly_signups['Year'] == year].copy()
    
    # Đảm bảo đủ 12 tháng
    all_months = pd.DataFrame({'Month': range(1, 13)})
    df_year = pd.merge(all_months, df_year, on='Month', how='left').fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Vẽ Bar chart
    sns.barplot(data=df_year, x='Month', y='new_customers', color='#9b59b6', ax=ax)
    
    # Vẽ thêm đường Line nối các đỉnh cột
    ax.plot(df_year['Month'] - 1, df_year['new_customers'], color='#8e44ad', marker='o', linewidth=2)
    
    ax.set_title(f'Số Lượng Khách Hàng Đăng Ký Mới Theo Tháng - Năm {year}', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Tháng', fontsize=12)
    ax.set_ylabel('Số Khách Hàng Đăng Ký Mới', fontsize=12)
    ax.set_xticks(range(0, 12))
    ax.set_xticklabels([f'Thg {m}' for m in range(1, 13)])
    
    # Ghi số trực tiếp lên cột
    for i, val in enumerate(df_year['new_customers']):
        if val > 0:
            ax.text(i, val + (df_year['new_customers'].max() * 0.02), f"{int(val):,}", 
                    ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
                    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'signups_{year}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"Đã lưu thành công {len(years)} biểu đồ đăng ký khách hàng vào thư mục: {os.path.abspath(output_dir)}")
