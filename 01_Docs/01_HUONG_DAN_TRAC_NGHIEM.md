# 📝 PHẦN 1 — HƯỚNG DẪN GIẢI CÂU HỎI TRẮC NGHIỆM

> **Tổng điểm:** 20đ | **Số câu:** 10 câu × 2đ | **Không trừ điểm sai**  
> **Yêu cầu:** Tính toán trực tiếp từ dữ liệu (Python/pandas)

---

## ⚡ Setup môi trường (chạy 1 lần đầu)

```python
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load toàn bộ data một lần
DATA_PATH = "datathon-2026-round-1/"

products    = pd.read_csv(DATA_PATH + "products.csv")
customers   = pd.read_csv(DATA_PATH + "customers.csv")
promotions  = pd.read_csv(DATA_PATH + "promotions.csv")
geography   = pd.read_csv(DATA_PATH + "geography.csv")
orders      = pd.read_csv(DATA_PATH + "orders.csv", parse_dates=["order_date"])
order_items = pd.read_csv(DATA_PATH + "order_items.csv")
payments    = pd.read_csv(DATA_PATH + "payments.csv")
shipments   = pd.read_csv(DATA_PATH + "shipments.csv", parse_dates=["ship_date","delivery_date"])
returns     = pd.read_csv(DATA_PATH + "returns.csv", parse_dates=["return_date"])
reviews     = pd.read_csv(DATA_PATH + "reviews.csv")
sales       = pd.read_csv(DATA_PATH + "sales.csv", parse_dates=["Date"])
inventory   = pd.read_csv(DATA_PATH + "inventory.csv")
web_traffic = pd.read_csv(DATA_PATH + "web_traffic.csv")

print("✅ Data loaded!")
```

---

## Q1 — Trung vị khoảng cách giữa các đơn hàng (Inter-order Gap)

### Đề bài
> Trong số các khách hàng có nhiều hơn một đơn hàng, trung vị số ngày giữa hai lần mua liên tiếp (inter-order gap) xấp xỉ là bao nhiêu?

**Đáp án:** **C) 144 ngày**

### Code giải

```python
# Bước 1: Sort theo customer_id và order_date
orders_sorted = orders.sort_values(['customer_id', 'order_date'])

# Bước 2: Lấy ngày đơn hàng trước của cùng khách hàng
orders_sorted['prev_date'] = orders_sorted.groupby('customer_id')['order_date'].shift(1)

# Bước 3: Tính khoảng cách (ngày)
orders_sorted['gap_days'] = (orders_sorted['order_date'] - orders_sorted['prev_date']).dt.days

# Bước 4: Chỉ lấy khách có hơn 1 đơn hàng
multi_buyers = orders_sorted[
    orders_sorted.groupby('customer_id')['order_id'].transform('count') > 1
]

# Bước 5: Tính trung vị
gaps = multi_buyers['gap_days'].dropna()
print(f"Median inter-order gap: {gaps.median():.1f} ngày")
# Kết quả: 144.0 ngày → Đáp án C
```

### 💡 Giải thích
- **Inter-order gap** = khoảng cách ngày giữa 2 đơn hàng liên tiếp của cùng 1 khách
- Dùng `shift(1)` sau khi group by `customer_id` để lấy đơn hàng liền trước
- Trung vị 144 ngày (~5 tháng) cho thấy khách hàng thời trang mua khá thưa

---

## Q2 — Phân khúc sản phẩm có tỷ suất lợi nhuận gộp cao nhất

### Đề bài
> Phân khúc sản phẩm (segment) nào có tỷ suất lợi nhuận gộp trung bình cao nhất với công thức `(price − cogs)/price`?

**Đáp án:** **D) Standard**

### Code giải

```python
# Tính gross margin cho từng sản phẩm
products['gross_margin'] = (products['price'] - products['cogs']) / products['price']

# Tính trung bình theo segment
margin_by_segment = (
    products.groupby('segment')['gross_margin']
    .mean()
    .sort_values(ascending=False)
)
print(margin_by_segment)
# Kết quả: Standard ~31.3% cao nhất
```

### 💡 Giải thích
- Nhiều người sẽ đoán "Premium" nhưng **Standard** mới là phân khúc có biên lợi nhuận gộp cao nhất (~31.3%)
- Điều này phổ biến trong thực tế: sản phẩm phổ thông thường có chi phí sản xuất thấp hơn tương đối so với giá bán
- Lưu ý: Đây là *tỷ suất*, không phải *giá trị tuyệt đối* lợi nhuận

---

## Q3 — Lý do trả hàng phổ biến nhất cho danh mục Streetwear

### Đề bài
> Trong các bản ghi trả hàng liên kết với sản phẩm thuộc danh mục **Streetwear**, lý do trả hàng nào xuất hiện nhiều nhất?

**Đáp án:** **B) wrong_size**

### Code giải

```python
# Bước 1: Join returns với products để lấy category
returns_with_cat = returns.merge(
    products[['product_id', 'category']],
    on='product_id',
    how='left'
)

# Bước 2: Lọc chỉ Streetwear
streetwear_returns = returns_with_cat[
    returns_with_cat['category'] == 'Streetwear'
]

# Bước 3: Đếm lý do trả hàng
print(streetwear_returns['return_reason'].value_counts())
# Kết quả:
# wrong_size          7626  ← Nhiều nhất
# defective           4330
# not_as_described    3854
# changed_mind        3830
# late_delivery       2159
```

### 💡 Giải thích
- `wrong_size` là lý do phổ biến nhất cho Streetwear vì đây là thời trang đường phố — kích thước fit rất quan trọng
- Thông tin này có giá trị kinh doanh: có thể cải thiện bảng size chart, thêm hướng dẫn chọn size

---

## Q4 — Nguồn truy cập có tỷ lệ thoát thấp nhất

### Đề bài
> Trong `web_traffic.csv`, nguồn truy cập (traffic_source) nào có tỷ lệ thoát trung bình (bounce_rate) **thấp nhất**?

**Đáp án:** **C) email_campaign**

### Code giải

```python
# Tính bounce_rate trung bình theo từng nguồn traffic
bounce_by_source = (
    web_traffic.groupby('traffic_source')['bounce_rate']
    .mean()
    .sort_values()  # Tăng dần → thấp nhất ở đầu
)
print(bounce_by_source)
# Kết quả:
# email_campaign    0.004458  ← Thấp nhất
# social_media      0.004476
# paid_search       0.004478
# referral          0.004499
# organic_search    0.004504
# direct            0.004511
```

### 💡 Giải thích
- **email_campaign** có bounce rate thấp nhất vì người nhận email thường đã có ý định mua → engagement cao hơn
- Các nguồn organic/direct có bounce rate cao hơn vì nhiều lượt xem chỉ để khảo sát
- Sự chênh lệch nhỏ (~0.001) nhưng kết quả nhất quán

---

## Q5 — Tỷ lệ order_items có áp dụng khuyến mãi

### Đề bài
> Tỷ lệ phần trăm các dòng trong `order_items.csv` có áp dụng khuyến mãi (promo_id không null) xấp xỉ là bao nhiêu?

**Đáp án:** **C) 39%**

### Code giải

```python
# Tính tỷ lệ dòng có promo_id không null
pct_with_promo = order_items['promo_id'].notna().mean() * 100
print(f"Tỷ lệ có khuyến mãi: {pct_with_promo:.1f}%")
# Kết quả: 38.7% ≈ 39%

# Kiểm tra cả promo_id_2 (khuyến mãi thứ 2)
pct_with_promo2 = order_items['promo_id_2'].notna().mean() * 100
print(f"Tỷ lệ có khuyến mãi thứ 2: {pct_with_promo2:.1f}%")
```

### 💡 Giải thích
- Gần 2/5 dòng sản phẩm được áp dụng khuyến mãi → chiến dịch promotion rất tích cực
- Điều này sẽ quan trọng khi phân tích EDA về hiệu quả khuyến mãi

---

## Q6 — Nhóm tuổi có số đơn hàng trung bình cao nhất

### Đề bài
> Xét các khách hàng có `age_group` khác null, nhóm tuổi nào có số đơn hàng trung bình trên mỗi khách hàng cao nhất?

**Đáp án:** **A) 55+**

### Code giải

```python
# Bước 1: Đếm số đơn hàng mỗi khách hàng
cust_order_count = (
    orders.groupby('customer_id')['order_id']
    .count()
    .reset_index()
    .rename(columns={'order_id': 'order_count'})
)

# Bước 2: Join với customers (chỉ lấy các khách có age_group)
cust_with_age = customers[customers['age_group'].notna()].merge(
    cust_order_count, on='customer_id', how='left'
)
cust_with_age['order_count'] = cust_with_age['order_count'].fillna(0)

# Bước 3: Tính trung bình theo nhóm tuổi
avg_orders_by_age = (
    cust_with_age.groupby('age_group')['order_count']
    .mean()
    .sort_values(ascending=False)
)
print(avg_orders_by_age)
# Kết quả:
# 55+      5.41  ← Cao nhất
# 45-54    5.36
# 35-44    5.34
# 25-34    5.25
# 18-24    5.23
```

### 💡 Giải thích
- Nhóm **55+** mua hàng nhiều nhất tính trung bình (~5.4 đơn/khách) dù ít người nghĩ vậy
- Điều này cho thấy phân khúc khách hàng cao tuổi có loyalty cao và giá trị vòng đời cao
- Khác biệt giữa các nhóm nhỏ (5.23 – 5.41) nhưng 55+ vẫn dẫn đầu nhất quán

---

## Q7 — Vùng tạo ra tổng doanh thu cao nhất

### Đề bài
> Vùng (region) nào trong `geography.csv` tạo ra tổng doanh thu cao nhất trong `sales_train.csv`?

**Đáp án:** **C) East**

### Code giải

```python
# Bước 1: Join orders với geography để lấy region
orders_with_region = orders.merge(
    geography[['zip', 'region']],
    on='zip',
    how='left'
)

# Bước 2: Join với order_items để lấy chi tiết doanh thu
orders_items_region = orders_with_region.merge(
    order_items,
    on='order_id'
)

# Bước 3: Tính doanh thu thuần mỗi dòng
orders_items_region['net_revenue'] = (
    orders_items_region['unit_price'] * orders_items_region['quantity']
    - orders_items_region['discount_amount']
)

# Bước 4: Tổng hợp theo vùng
revenue_by_region = (
    orders_items_region.groupby('region')['net_revenue']
    .sum()
    .sort_values(ascending=False)
)
print(revenue_by_region)
# Kết quả:
# East       7.29 tỷ  ← Cao nhất
# Central    4.72 tỷ
# West       3.67 tỷ
```

### 💡 Giải thích
- Vùng **East** (Miền Đông) dẫn đầu với ~7.3 tỷ đồng doanh thu, gấp đôi Miền Tây
- Tương ứng với thực tế: TP.HCM và các tỉnh miền Đông là trung tâm kinh tế lớn nhất

---

## Q8 — Phương thức thanh toán phổ biến nhất trong đơn hàng bị huỷ

### Đề bài
> Trong các đơn hàng có `order_status = 'cancelled'`, phương thức thanh toán nào được sử dụng nhiều nhất?

**Đáp án:** **A) credit_card**

### Code giải

```python
# Lọc đơn hàng bị huỷ
cancelled_orders = orders[orders['order_status'] == 'cancelled']

# Đếm phương thức thanh toán
payment_counts = cancelled_orders['payment_method'].value_counts()
print(payment_counts)
# Kết quả:
# credit_card      28452  ← Nhiều nhất
# cod              15468
# paypal            7817
# apple_pay         5190
# bank_transfer     2535

# Xác nhận tỷ lệ
print(f"Tỷ lệ credit_card: {payment_counts['credit_card'] / payment_counts.sum() * 100:.1f}%")
```

### 💡 Giải thích
- **credit_card** xuất hiện nhiều nhất trong đơn huỷ vì nó cũng là phương thức phổ biến nhất nói chung
- Để phân tích ý nghĩa hơn, cần tính **tỷ lệ huỷ** theo từng phương thức (cancellation rate)

---

## Q9 — Kích thước sản phẩm có tỷ lệ trả hàng cao nhất

### Đề bài
> Trong bốn kích thước (S, M, L, XL), kích thước nào có tỷ lệ trả hàng cao nhất (số bản ghi returns / số dòng order_items)?

**Đáp án:** **A) S**

### Code giải

```python
# Bước 1: Join returns với products để lấy size
returns_with_size = returns.merge(
    products[['product_id', 'size']],
    on='product_id'
)

# Bước 2: Join order_items với products để lấy size
items_with_size = order_items.merge(
    products[['product_id', 'size']],
    on='product_id'
)

# Bước 3: Đếm số lượng mỗi size
returns_count = returns_with_size.groupby('size').size()
items_count = items_with_size.groupby('size').size()

# Bước 4: Tính tỷ lệ
return_rate_by_size = (returns_count / items_count).sort_values(ascending=False)
print(return_rate_by_size)
# Kết quả:
# S     0.0565  ← Cao nhất
# L     0.0563
# M     0.0557
# XL    0.0552
```

### 💡 Giải thích
- Size **S** có tỷ lệ trả hàng cao nhất (5.65%) dù chênh lệch nhỏ
- Khách hàng nhỏ người thường khó tìm đúng size → dễ phải trả hàng hơn
- Insight: Cần cải thiện hướng dẫn chọn size cho khách hàng size S

---

## Q10 — Kế hoạch trả góp có giá trị thanh toán trung bình cao nhất

### Đề bài
> Trong `payments.csv`, kế hoạch trả góp nào có giá trị thanh toán trung bình trên mỗi đơn hàng cao nhất?

**Đáp án:** **C) 6 kỳ**

### Code giải

```python
# Tính giá trị trung bình mỗi đơn theo số kỳ trả góp
avg_payment_by_installments = (
    payments.groupby('installments')['payment_value']
    .mean()
    .sort_values(ascending=False)
)
print(avg_payment_by_installments)
# Kết quả:
# 6     24,447  ← Cao nhất
# 3     24,400
# 12    24,246
# 1     24,113
# (2 rất thấp → bất thường, có thể là đơn đặc biệt)
```

### 💡 Giải thích
- **6 kỳ** (6 months installment) có giá trị trung bình cao nhất (~24,447/đơn)
- Đơn giá trị cao thường được chọn trả góp 6 kỳ — cân bằng giữa số tiền hàng tháng và tổng thời gian
- Lưu ý: Installment = 2 có giá trị bất thường thấp → có thể là đơn test/đặc biệt

---

## 📊 Tổng hợp đáp án

| Câu | Đáp án | Nội dung chính |
|-----|--------|----------------|
| Q1 | **C** | Trung vị gap = 144 ngày |
| Q2 | **D** | Standard có margin ~31.3% |
| Q3 | **B** | wrong_size (7,626 lần) |
| Q4 | **C** | email_campaign bounce_rate thấp nhất |
| Q5 | **C** | ~38.7% ≈ 39% có promo |
| Q6 | **A** | 55+ avg 5.41 đơn/khách |
| Q7 | **C** | East ~7.3 tỷ doanh thu |
| Q8 | **A** | credit_card 28,452 đơn huỷ |
| Q9 | **A** | S size tỷ lệ trả 5.65% |
| Q10 | **C** | 6 kỳ avg 24,447/đơn |

> 📄 Xem đáp án đầy đủ với giải thích chi tiết: **[01b_DAP_AN_TRAC_NGHIEM.md](./01b_DAP_AN_TRAC_NGHIEM.md)**
