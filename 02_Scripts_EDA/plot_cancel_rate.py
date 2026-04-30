import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

file_path = '../datathon-2026-round-1/orders.csv'
output_dir = 'yearly_cancel_plots'

os.makedirs(output_dir, exist_ok=True)

print("Đang đọc dữ liệu orders.csv...")
orders = pd.read_csv(file_path, parse_dates=['order_date'])

orders['Year'] = orders['order_date'].dt.year
orders['Month'] = orders['order_date'].dt.month

# Tính số lượng đơn và số lượng cancel
monthly_orders = orders.groupby(['Year', 'Month']).agg(
    Total_Orders=('order_id', 'count'),
    Cancelled_Orders=('order_status', lambda x: (x == 'cancelled').sum())
).reset_index()

monthly_orders['Cancel_Rate'] = monthly_orders['Cancelled_Orders'] / monthly_orders['Total_Orders'] * 100

plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

years = sorted(monthly_orders['Year'].unique())

for year in years:
    df_year = monthly_orders[monthly_orders['Year'] == year].copy()
    
    all_months = pd.DataFrame({'Month': range(1, 13)})
    df_year = pd.merge(all_months, df_year, on='Month', how='left').fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot Cancel Rate
    sns.lineplot(data=df_year, x='Month', y='Cancel_Rate', color='#e74c3c', marker='o', linewidth=2.5, ax=ax)
    
    ax.set_title(f'Tỷ Lệ Hủy Đơn Hàng Theo Tháng - Năm {year}', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Tháng', fontsize=12)
    ax.set_ylabel('Tỷ lệ Hủy Đơn (%)', fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f'Thg {m}' for m in range(1, 13)])
    
    for i, row in df_year.iterrows():
        val = row['Cancel_Rate']
        if val > 0:
            ax.text(row['Month'], val + (df_year['Cancel_Rate'].max() * 0.05), f"{val:.1f}%", 
                    ha='center', va='bottom', fontsize=10, color='red', fontweight='bold')
            
    # Scale Y axis appropriately
    ax.set_ylim(0, max(15, df_year['Cancel_Rate'].max() * 1.2))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'cancel_rate_{year}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

print(f"Đã lưu thành công {len(years)} biểu đồ tỷ lệ hủy đơn vào thư mục: {os.path.abspath(output_dir)}")
print("\n--- THỐNG KÊ NHANH ---")
print(monthly_orders.groupby('Month')['Cancel_Rate'].mean().reset_index().rename(columns={'Cancel_Rate': 'Avg_Cancel_Rate_All_Years'}))
