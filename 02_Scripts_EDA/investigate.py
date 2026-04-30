import pandas as pd

# Đọc dữ liệu
sales = pd.read_csv('../datathon-2026-round-1/sales.csv', parse_dates=['Date'])
promos = pd.read_csv('../datathon-2026-round-1/promotions.csv', parse_dates=['start_date', 'end_date'])

sales['Year'] = sales['Date'].dt.year
sales['Month'] = sales['Date'].dt.month
sales['Profit'] = sales['Revenue'] - sales['COGS']

print("==================================================")
print("1. PHÂN TÍCH THÁNG 8: NĂM NÀO LỜI, NĂM NÀO LỖ?")
print("==================================================")
august = sales[sales['Month'] == 8].groupby('Year')[['Revenue', 'Profit']].sum()
august['Profit_Margin(%)'] = (august['Profit'] / august['Revenue'] * 100).round(2)
print(august)

print("\n==================================================")
print("2. TÌM CHIẾN DỊCH KHUYẾN MÃI TRONG THÁNG 8 CÁC NĂM")
print("==================================================")
# Lấy các khuyến mãi có chạy trong tháng 8
aug_promos = promos[((promos['start_date'].dt.month <= 8) & (promos['end_date'].dt.month >= 8))]
aug_promos['Year'] = aug_promos['start_date'].dt.year
print(aug_promos[['Year', 'promo_name', 'promo_type', 'discount_value', 'start_date', 'end_date']].sort_values('Year'))

print("\n==================================================")
print("3. TÌM NGUYÊN NHÂN THÁNG 4, 5, 6 LỢI NHUẬN CAO")
print("==================================================")
q2_promos = promos[promos['start_date'].dt.month.isin([4,5,6])]
print(q2_promos[['promo_name', 'promo_type', 'discount_value', 'start_date', 'end_date']])
