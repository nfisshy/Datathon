# 📊 PHẦN 2 — HƯỚNG DẪN TRỰC QUAN HOÁ & PHÂN TÍCH DỮ LIỆU (EDA)

> **Tổng điểm:** 60/100 (60%) — Phần quan trọng nhất!  
> **Nguyên tắc:** Không có đáp án đúng duy nhất — Ban giám khảo đánh giá khả năng **data storytelling**

---

## 🎯 Framework 4 Cấp Độ Phân Tích (DDPP)

Đây là cấu trúc cốt lõi để đạt điểm tối đa. **Mỗi insight cần leo được lên cấp Prescriptive.**

```
Descriptive  → "Doanh thu Q4/2021 tăng 45% so với Q4/2020"
     ↓
Diagnostic   → "Nguyên nhân: Campaign Black Friday kết hợp mở rộng vùng East"
     ↓
Predictive   → "Dự báo Q4/2022 sẽ tăng ~30% nếu repeat campaign với budget gấp 1.5x"
     ↓
Prescriptive → "Khuyến nghị: Tập trung budget vào email_campaign + vùng East; ưu tiên SKU Premium/Streetwear"
```

---

## 📐 Rubric Đánh Giá Chi Tiết

| Tiêu chí | Điểm tối đa | Để đạt điểm cao |
|----------|-------------|-----------------|
| Chất lượng trực quan hoá | 15đ | Tiêu đề rõ, nhãn trục đầy đủ, loại biểu đồ phù hợp |
| Chiều sâu phân tích | 25đ | Đạt cả 4 cấp DDPP với số liệu cụ thể |
| Insight kinh doanh | 15đ | Đề xuất action cụ thể, định lượng được |
| Tính sáng tạo | 5đ | Góc nhìn độc đáo, kết nối nhiều bảng dữ liệu |

---

## 🗺️ Kế Hoạch Phân Tích Gợi Ý

### 🔴 Ưu tiên cao (nhiều điểm nhất)

#### Theme 1: Phân tích Doanh thu & Tính Mùa Vụ
*Kết nối: `sales.csv` + `orders.csv` + `order_items.csv`*

**1.1 Xu hướng doanh thu theo thời gian**
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sales = pd.read_csv("sales.csv", parse_dates=["Date"])

# Doanh thu theo tháng
sales['month'] = sales['Date'].dt.to_period('M')
monthly = sales.groupby('month')['Revenue'].sum()

fig, ax = plt.subplots(figsize=(15, 5))
monthly.plot(ax=ax, color='#2196F3', linewidth=1.5)
ax.fill_between(range(len(monthly)), monthly.values, alpha=0.2)
ax.set_title('Doanh thu hàng tháng (2012–2022)', fontsize=14, fontweight='bold')
ax.set_xlabel('Tháng')
ax.set_ylabel('Doanh thu (VNĐ)')
plt.tight_layout()
plt.savefig('revenue_trend.png', dpi=150, bbox_inches='tight')
```

**Insight cần khai thác:**
- Doanh thu tổng thể tăng/giảm theo năm như thế nào?
- Tháng nào peak (thường là tháng 11-12 do Black Friday, Tết)?
- Có yếu tố COVID-19 ảnh hưởng 2020-2021 không?

**1.2 Tính mùa vụ (Seasonality)**
```python
sales['year'] = sales['Date'].dt.year
sales['month_num'] = sales['Date'].dt.month

# Heatmap doanh thu theo năm × tháng
pivot = sales.pivot_table(values='Revenue', index='year', columns='month_num', aggfunc='sum')
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, fmt='.0f', cmap='YlOrRd', ax=ax,
            xticklabels=['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12'])
ax.set_title('Heatmap Doanh thu theo Năm × Tháng', fontsize=14)
```

---

#### Theme 2: Phân Tích Khách Hàng (Customer Segmentation)
*Kết nối: `customers.csv` + `orders.csv` + `order_items.csv` + `geography.csv`*

**2.1 RFM Analysis (Recency - Frequency - Monetary)**
```python
from datetime import datetime

orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
order_items = pd.read_csv("order_items.csv")

# Tính doanh thu mỗi đơn
order_revenue = order_items.groupby('order_id').apply(
    lambda x: (x['unit_price'] * x['quantity'] - x['discount_amount']).sum()
).reset_index(name='order_value')

orders_with_value = orders.merge(order_revenue, on='order_id')

reference_date = orders['order_date'].max()

rfm = orders_with_value.groupby('customer_id').agg(
    Recency=('order_date', lambda x: (reference_date - x.max()).days),
    Frequency=('order_id', 'count'),
    Monetary=('order_value', 'sum')
).reset_index()

# Phân nhóm RFM score 1-5
for col in ['Recency', 'Frequency', 'Monetary']:
    if col == 'Recency':
        rfm[f'{col}_score'] = pd.qcut(rfm[col], 5, labels=[5,4,3,2,1])
    else:
        rfm[f'{col}_score'] = pd.qcut(rfm[col].rank(method='first'), 5, labels=[1,2,3,4,5])

rfm['RFM_segment'] = rfm['Recency_score'].astype(str) + rfm['Frequency_score'].astype(str) + rfm['Monetary_score'].astype(str)

# Champions: RFM score 555
champions = rfm[rfm['RFM_segment'] == '555']
print(f"Champions: {len(champions)} khách ({len(champions)/len(rfm)*100:.1f}%)")
```

**Prescriptive Insights:**
- **Champions (RFM=555):** Tặng VIP badge, early access sale, referral program
- **At Risk (RFM=5xx mà Frequency/Monetary thấp):** Reactivation campaign, win-back email
- **New Customers (F=1):** Onboarding journey, cross-sell products

**2.2 Phân tích theo kênh acquisition**
```python
customers = pd.read_csv("customers.csv")
cust_orders = orders.groupby('customer_id')['order_id'].count().reset_index()
cust_orders.columns = ['customer_id', 'order_count']

# Join với customers để lấy acquisition channel
cust_full = customers.merge(cust_orders, on='customer_id', how='left')
cust_full['order_count'] = cust_full['order_count'].fillna(0)

# So sánh kênh acquisition
channel_analysis = cust_full.groupby('acquisition_channel').agg(
    customer_count=('customer_id', 'count'),
    avg_orders=('order_count', 'mean')
).sort_values('avg_orders', ascending=False)

# Visualization: Bar chart với annotated values
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(channel_analysis.index, channel_analysis['avg_orders'], 
              color=['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336'])
ax.set_title('Số đơn hàng trung bình theo kênh Acquisition', fontsize=14)
ax.set_xlabel('Kênh Marketing')
ax.set_ylabel('Avg Orders per Customer')
# Thêm số lên đỉnh cột
for bar, val in zip(bars, channel_analysis['avg_orders']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
            f'{val:.2f}', ha='center', fontsize=10)
```

---

#### Theme 3: Hiệu Quả Khuyến Mãi (Promotion Effectiveness)
*Kết nối: `promotions.csv` + `order_items.csv` + `orders.csv`*

**3.1 Phân tích tác động của khuyến mãi lên doanh thu**
```python
promotions = pd.read_csv("promotions.csv", parse_dates=["start_date", "end_date"])
order_items = pd.read_csv("order_items.csv")
orders = pd.read_csv("orders.csv", parse_dates=["order_date"])

# Đơn có và không có khuyến mãi
items_with_promo = order_items[order_items['promo_id'].notna()].copy()
items_no_promo   = order_items[order_items['promo_id'].isna()].copy()

# Tính AOV (Average Order Value) cho từng nhóm
for items, label in [(items_with_promo, 'Với KM'), (items_no_promo, 'Không KM')]:
    aov = items.merge(orders, on='order_id')
    order_val = aov.groupby('order_id').apply(
        lambda x: (x['unit_price'] * x['quantity'] - x['discount_amount']).sum()
    )
    print(f"AOV {label}: {order_val.mean():,.0f}")
```

**3.2 Hiệu quả từng loại khuyến mãi**
```python
# Join order_items với promotions
items_promo = order_items.merge(
    promotions[['promo_id', 'promo_type', 'discount_value', 'promo_channel']],
    on='promo_id', how='left'
)

promo_analysis = items_promo.groupby('promo_type').agg(
    count=('order_id', 'count'),
    total_discount=('discount_amount', 'sum'),
    avg_discount=('discount_amount', 'mean')
)
print(promo_analysis)
```

---

#### Theme 4: Phân Tích Trả Hàng (Returns Analysis)
*Kết nối: `returns.csv` + `products.csv` + `order_items.csv`*

**4.1 Tỷ lệ trả hàng theo danh mục & phân khúc**
```python
returns = pd.read_csv("returns.csv")
products = pd.read_csv("products.csv")

returns_detail = returns.merge(products[['product_id', 'category', 'segment', 'size']], on='product_id')
items_detail = order_items.merge(products[['product_id', 'category', 'segment']], on='product_id')

# Return rate theo category
cat_returns = returns_detail.groupby('category').size()
cat_items = items_detail.groupby('category').size()
return_rate = (cat_returns / cat_items * 100).sort_values(ascending=False)

# Visualization: Horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 7))
return_rate.plot(kind='barh', ax=ax, color='#F44336')
ax.set_title('Tỷ lệ trả hàng theo danh mục sản phẩm (%)', fontsize=14)
ax.set_xlabel('Return Rate (%)')
for i, (val, name) in enumerate(zip(return_rate.values, return_rate.index)):
    ax.text(val + 0.1, i, f'{val:.2f}%', va='center')
```

---

### 🟡 Ưu tiên trung bình

#### Theme 5: Phân Tích Địa Lý & Vùng Miền
```python
geography = pd.read_csv("geography.csv")
orders = pd.read_csv("orders.csv", parse_dates=["order_date"])

orders_geo = orders.merge(geography, on='zip', how='left')
orders_items = orders_geo.merge(order_items, on='order_id')
orders_items['revenue'] = orders_items['unit_price'] * orders_items['quantity'] - orders_items['discount_amount']

# Revenue theo region và quý
orders_items['quarter'] = orders_items['order_date'].dt.to_period('Q')
region_quarter = orders_items.groupby(['quarter', 'region'])['revenue'].sum().unstack()

# Stacked area chart
fig, ax = plt.subplots(figsize=(15, 6))
region_quarter.plot(kind='area', stacked=True, ax=ax, alpha=0.7,
                    colormap='tab10')
ax.set_title('Doanh thu theo Vùng Miền qua các Quý', fontsize=14)
```

#### Theme 6: Phân Tích Web Traffic & Conversion
```python
web = pd.read_csv("web_traffic.csv", parse_dates=["date"])

# Tính conversion proxy: đơn hàng / sessions
web_daily = web.groupby('date').agg({'sessions': 'sum', 'unique_visitors': 'sum'}).reset_index()
orders_daily = orders.groupby('order_date')['order_id'].count().reset_index()
orders_daily.columns = ['date', 'order_count']

# Merge
combined = web_daily.merge(orders_daily, on='date', how='left')
combined['conversion_rate'] = combined['order_count'] / combined['sessions'] * 100

# Rolling average
combined['conv_7d_ma'] = combined['conversion_rate'].rolling(7).mean()

fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(combined['date'], combined['conv_7d_ma'], label='7-day MA', color='#2196F3')
ax.set_title('Tỷ lệ Chuyển đổi Web → Đơn hàng (7-day Moving Average)', fontsize=14)
```

---

#### Theme 7: Inventory Intelligence
```python
inventory = pd.read_csv("inventory.csv", parse_dates=["snapshot_date"])

# Phân tích stockout theo danh mục
stockout_by_cat = inventory.groupby('category').agg(
    stockout_rate=('stockout_flag', 'mean'),
    avg_days_supply=('days_of_supply', 'mean'),
    fill_rate=('fill_rate', 'mean')
).sort_values('stockout_rate', ascending=False)

# Heatmap: Stockout risk theo category × month
pivot = inventory.groupby(['category', 'month'])['stockout_flag'].mean().unstack()
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, cmap='RdYlGn_r', fmt='.2f', ax=ax, annot=True)
ax.set_title('Tỷ lệ Stockout theo Danh mục × Tháng', fontsize=14)
```

---

## 🎨 Best Practices Visualization

### Chọn loại biểu đồ đúng

| Mục đích | Biểu đồ phù hợp |
|---------|-----------------|
| Xu hướng theo thời gian | Line chart, Area chart |
| So sánh danh mục | Bar chart (horizontal nếu nhiều categories) |
| Phân phối dữ liệu | Histogram, Box plot, Violin plot |
| Tương quan 2 biến | Scatter plot |
| Tỷ lệ phần trăm | Pie chart (≤5 phần), Stacked bar |
| Ma trận tương quan | Heatmap |
| Phân bố địa lý | Choropleth map |

### Template biểu đồ chuẩn

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Style setup
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.dpi': 150,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

fig, ax = plt.subplots(figsize=(10, 6))

# ... vẽ biểu đồ ...

# Luôn có đủ các thành phần:
ax.set_title('Tiêu đề rõ ràng, mô tả đủ thông tin', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Tên trục X (đơn vị)', fontsize=11)
ax.set_ylabel('Tên trục Y (đơn vị)', fontsize=11)
ax.legend(title='Chú thích', loc='upper left')
# Thêm nguồn dữ liệu
fig.text(0.99, 0.01, 'Nguồn: DATATHON 2026 Dataset', ha='right', fontsize=8, color='gray')

plt.tight_layout()
plt.savefig('chart_name.png', dpi=150, bbox_inches='tight')
```

---

## 📝 Cấu Trúc Bài Phân Tích Mẫu (Data Story)

### Cấu trúc cho 1 slide/section phân tích

```
1. TIÊU ĐỀ: "Khách hàng 55+ có vòng đời giá trị cao nhất"

2. BIỂU ĐỒ: Bar chart + line chart kết hợp
   - Trục Y trái: Avg orders per customer
   - Trục Y phải: Avg lifetime value

3. KEY FINDINGS (Descriptive):
   "Nhóm 55+ trung bình 5.41 đơn/khách, cao hơn 18-24 là 3.4%"

4. WHY (Diagnostic):
   "Nhóm 55+ có thu nhập ổn định, brand loyalty cao, ít bị cạnh tranh bởi deals"

5. WHAT NEXT (Predictive):
   "Nếu retention rate 55+ tăng 5%, LTV toàn bộ fleet tăng ~2.8%"

6. ACTION (Prescriptive):
   "Khuyến nghị: Tạo senior loyalty program, giao hàng ưu tiên, hotline hỗ trợ riêng"
```

---

## 🏆 Các Insight Độc Đáo Để Đạt Điểm Tính Sáng Tạo (5đ)

### Idea 1: Cross-analysis Email Campaign × Inventory
*Kết hợp web_traffic + inventory + orders để tìm: "Khi email campaign → tăng traffic → stockout xảy ra không?"*

### Idea 2: Product-Customer Affinity Matrix
*products (category, segment, size) × customers (age_group, region) → tìm nhóm sản phẩm được ưa thích nhất bởi từng phân khúc khách hàng*

### Idea 3: Promotion Cannibalization Analysis
*Khi có khuyến mãi → doanh thu tăng nhưng margin giảm bao nhiêu? Liệu promo có "cannibalize" doanh thu bình thường?*

### Idea 4: Delivery Speed → Review Score Correlation
*shipments (delivery_date - ship_date) × reviews (rating) → Giao hàng chậm bao nhiêu ngày thì rating giảm?*

### Idea 5: Customer Churn Prediction Indicators
*Từ RFM + returns + reviews → xây dựng churn score cho từng khách hàng*

---

## 📋 Checklist Trước Khi Nộp Phần 2

### Visualizations
- [ ] Tất cả biểu đồ có **tiêu đề mô tả đủ** (không chỉ "Bar Chart")
- [ ] Tất cả trục có **nhãn + đơn vị** (VNĐ, %, ngày...)
- [ ] Có **chú thích (legend)** khi có nhiều series
- [ ] Màu sắc nhất quán và dễ phân biệt
- [ ] Font chữ đủ to để đọc được trong PDF

### Analysis Content
- [ ] Bao phủ **ít nhất 3-4 cấp DDPP** trên mỗi insight chính
- [ ] Mỗi claim có **số liệu cụ thể** đi kèm
- [ ] Kết nối **ít nhất 3 bảng dữ liệu** khác nhau
- [ ] Đề xuất **action cụ thể, đo lường được**

### Report Quality
- [ ] Mạch trình bày **coherent** (có đầu có đuôi)
- [ ] Không có lỗi chính tả hay sai số liệu
- [ ] Phần giới thiệu context kinh doanh rõ ràng
- [ ] Kết luận tóm tắt và đề xuất ưu tiên
