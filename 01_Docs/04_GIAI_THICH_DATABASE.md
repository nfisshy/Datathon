# 🗄️ GIẢI THÍCH TOÀN BỘ DATABASE — DATATHON 2026

> Bộ dữ liệu mô phỏng **doanh nghiệp thời trang thương mại điện tử Việt Nam**  
> Giai đoạn: **04/07/2012 – 31/12/2022** | 15 file CSV | 4 lớp dữ liệu

---

## 📐 ERD — Entity Relationship Diagram

> Chạy lệnh sau để sinh ảnh ERD (`erd_datathon2026.png`):
> ```bash
> python erd_generator.py
> ```
> Script: [`erd_generator.py`](./erd_generator.py) | Output: [`erd_datathon2026.png`](./erd_datathon2026.png)

![ERD DATATHON 2026](./erd_datathon2026.png)

**Chú thích màu sắc:**
| Màu | Lớp | Ý nghĩa |
|-----|-----|---------|
| 🔵 Xanh dương | MASTER | Dữ liệu tham chiếu tĩnh |
| 🟠 Cam | TRANSACTION | Giao dịch thực tế |
| 🟢 Xanh lá | ANALYTICAL | Dữ liệu phân tích / Target |
| 🟣 Tím | OPERATIONAL | Dữ liệu vận hành |
| 🔴 `PK` | Primary Key | Khoá chính |
| 🔵 `FK` | Foreign Key | Khoá ngoại |
| 🟡 `TARGET` | Dự báo | Cột cần dự đoán (Revenue, COGS) |

---

## 🗺️ Sơ đồ tổng thể — Quan hệ các bảng

```
                    ┌──────────────┐
                    │ geography    │ (39,948 mã bưu chính)
                    │  zip PK      │
                    └──────┬───────┘
                           │ zip
              ┌────────────┼────────────────────┐
              ▼            ▼                    │
        ┌──────────┐  ┌──────────┐              │
        │customers │  │  orders  │◄─────────────┘
        │ 121,930  │  │ 646,945  │
        └──────────┘  └────┬─────┘
                           │ order_id (1:1)  ──────► payments (646,945)
                           │ order_id (1:0~1) ─────► shipments (566,067)
                           │ order_id (1:0~N) ─────► returns (39,939)
                           │ order_id (1:0~N) ─────► reviews (113,551)
                           │ order_id (N:1)   ─────► order_items (714,669)
                                                           │ product_id
                                                           ▼
                                                      ┌──────────┐
                                                      │ products │◄── inventory
                                                      │  2,412   │    (60,247)
                                                      └──────────┘
                                                           │ promo_id
                                                           ▼
                                                      promotions (50)

Bảng độc lập:
  sales.csv        — Doanh thu tổng hợp theo ngày (TARGET để dự báo)
  web_traffic.csv  — Lưu lượng web theo ngày
```

---

## 📦 LỚP 1: MASTER — Dữ liệu Tham chiếu

### 1. `products.csv` — Danh mục sản phẩm
**Shape:** 2,412 sản phẩm × 8 cột

| Cột | Kiểu | Giá trị mẫu / Thống kê |
|-----|------|------------------------|
| `product_id` | int | PK — từ 1 đến 2412 |
| `product_name` | str | Tên sản phẩm cụ thể |
| `category` | str | Streetwear (1320), Outdoor (743), Casual (201), GenZ (148) |
| `segment` | str | Premium, Standard, Activewear, Performance, All-weather, Balanced, Trendy, Everyday |
| `size` | str | S, M, L, XL |
| `color` | str | black, blue, green, orange, pink, purple, red, silver, white, yellow |
| `price` | float | Min: 9đ, Max: 40,950đ, **Mean: 4,928đ** |
| `cogs` | float | Luôn < price (**Margin trung bình: 26.6%**) |

**💡 Điểm quan trọng:**
- **Streetwear chiếm 55%** tổng sản phẩm — danh mục chủ lực
- Công thức margin: `(price - cogs) / price` → dùng cho Q2 trắc nghiệm
- Ràng buộc: `cogs < price` với **mọi** sản phẩm (đã kiểm tra)

---

### 2. `customers.csv` — Thông tin Khách hàng
**Shape:** 121,930 khách hàng × 7 cột

| Cột | Kiểu | Phân phối / Ghi chú |
|-----|------|---------------------|
| `customer_id` | int | PK |
| `zip` | int | FK → geography.zip |
| `city` | str | Tên thành phố |
| `signup_date` | date | 17/01/2012 → 31/12/2022 |
| `gender` | str | Female: 59,640 \| Male: 57,457 \| Non-binary: 4,833 |
| `age_group` | str | 25-34: 36,342 \| 35-44: 31,920 \| 45-54: 23,172 \| 18-24: 17,039 \| 55+: 13,457 |
| `acquisition_channel` | str | organic_search: 36,450 \| social_media: 24,448 \| paid_search: 24,285 \| ... |

**💡 Điểm quan trọng:**
- **Không có giá trị null** ở gender và age_group (khác với đề bài mô tả là "nullable" — thực tế không có null)
- Nhóm 25–34 chiếm đông nhất; nhóm 55+ ít nhất nhưng mua hàng nhiều nhất/người (Q6)
- `organic_search` là kênh acquisition phổ biến nhất (~30%)

---

### 3. `promotions.csv` — Chiến dịch Khuyến mãi
**Shape:** 50 chiến dịch × 10 cột

| Cột | Kiểu | Giá trị / Ghi chú |
|-----|------|-------------------|
| `promo_id` | str | PK dạng "PROMO-XXXX" |
| `promo_name` | str | Tên chiến dịch kèm năm |
| `promo_type` | str | `percentage` (giảm %) hoặc `fixed` (giảm số tiền cố định) |
| `discount_value` | float | Giá trị giảm (% hoặc số tiền tùy type) |
| `start_date` | date | 31/01/2013 → 18/11/2022 |
| `end_date` | date | 01/03/2013 → 31/12/2022 |
| `applicable_category` | str | Outdoor, Streetwear — **null = áp dụng tất cả** (40/50 chiến dịch null) |
| `promo_channel` | str | all_channels, email, in_store, online, social_media |
| `stackable_flag` | int | 1 = được dùng đồng thời nhiều KM |
| `min_order_value` | float | Giá trị đơn tối thiểu (có thể null) |

**💡 Công thức tính giảm giá:**
```
percentage:  discount = quantity × unit_price × (discount_value / 100)
fixed:       discount = quantity × discount_value
```

---

### 4. `geography.csv` — Dữ liệu Địa lý
**Shape:** 39,948 mã bưu chính × 4 cột

| Cột | Kiểu | Giá trị |
|-----|------|---------|
| `zip` | int | PK — mã bưu chính |
| `city` | str | Tên thành phố |
| `region` | str | **East**, **Central**, **West** |
| `district` | str | Tên quận/huyện |

**💡 Điểm quan trọng:**
- Chỉ có **3 vùng**: East (~46% doanh thu), Central (~30%), West (~24%)
- Join với `orders` qua cột `zip` để phân tích doanh thu theo vùng
- Join với `customers` qua `zip` để phân tích khách hàng theo địa lý

---

## 💳 LỚP 2: TRANSACTION — Dữ liệu Giao dịch

### 5. `orders.csv` — Đơn hàng
**Shape:** 646,945 đơn × 8 cột

| Cột | Kiểu | Phân phối |
|-----|------|-----------|
| `order_id` | int | PK |
| `order_date` | date | 04/07/2012 → 31/12/2022 |
| `customer_id` | int | FK → customers |
| `zip` | int | FK → geography (địa chỉ giao hàng) |
| `order_status` | str | **delivered: 516,716 (79.9%)** \| cancelled: 59,462 (9.2%) \| returned: 36,142 \| shipped: 13,773 \| paid: 13,577 \| created: 7,275 |
| `payment_method` | str | credit_card: 356,352 (55.1%) \| paypal: 97,018 \| cod: 96,681 \| apple_pay: 64,763 \| bank_transfer: 32,131 |
| `device_type` | str | mobile: 291,482 (45%) \| desktop: 258,855 (40%) \| tablet: 96,608 (15%) |
| `order_source` | str | direct \| email_campaign \| organic_search \| paid_search \| referral \| social_media |

**💡 Điểm quan trọng:**
- **80% đơn hàng được giao thành công** (delivered)
- `credit_card` chiếm hơn một nửa phương thức thanh toán
- `mobile` là thiết bị chủ yếu — thị trường mobile-first

---

### 6. `order_items.csv` — Chi tiết Đơn hàng
**Shape:** 714,669 dòng × 7 cột *(nhiều hơn orders vì 1 đơn có thể nhiều sản phẩm)*

| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| `order_id` | int | FK → orders |
| `product_id` | int | FK → products |
| `quantity` | int | Số lượng đặt mua |
| `unit_price` | float | Giá tại thời điểm mua (có thể khác `price` trong products nếu có sale) |
| `discount_amount` | float | Tổng tiền giảm cho dòng này |
| `promo_id` | str | FK → promotions (**null = 438,353 dòng = 61.3% không có KM**) |
| `promo_id_2` | str | KM thứ 2 (**null = 714,463 dòng = 99.97%** — chỉ 206 dòng dùng 2 KM) |

**💡 Điểm quan trọng:**
- ~**38.7% dòng có áp dụng khuyến mãi** (Q5) → công ty dùng promotion khá tích cực
- Doanh thu thuần mỗi dòng = `unit_price × quantity - discount_amount`
- Chỉ 2 promo_id được dùng ở promo_id_2: PROMO-0015 và PROMO-0025

---

### 7. `payments.csv` — Thanh toán
**Shape:** 646,945 dòng × 4 cột *(1:1 với orders)*

| Cột | Kiểu | Giá trị |
|-----|------|---------|
| `order_id` | int | FK → orders (quan hệ 1:1) |
| `payment_method` | str | Giống orders.payment_method |
| `payment_value` | float | Tổng giá trị thanh toán — Mean: **24,238đ**, Max: 331,570đ |
| `installments` | int | Số kỳ trả góp: **1, 2, 3, 6, 12** |

**💡 Điểm quan trọng:**
- 6 kỳ có giá trị trung bình/đơn cao nhất ~24,447đ (Q10)
- Installment = 2 rất ít đơn, giá trị thấp bất thường (có thể đơn đặc biệt)
- `payment_value` thường bao gồm cả shipping_fee

---

### 8. `shipments.csv` — Vận chuyển
**Shape:** 566,067 dòng × 4 cột

| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| `order_id` | int | FK → orders |
| `ship_date` | date | 04/07/2012 → 29/12/2022 |
| `delivery_date` | date | 06/07/2012 → 31/12/2022 |
| `shipping_fee` | float | 0 nếu miễn phí vận chuyển |

**💡 Điểm quan trọng:**
- Chỉ tồn tại cho đơn có status: `shipped`, `delivered`, hoặc `returned`
- **646,945 orders nhưng chỉ 566,067 shipments** → ~80,878 đơn chưa/không được giao (cancelled, created, paid)
- `delivery_date - ship_date` = thời gian giao hàng → có thể join với reviews.rating để phân tích chất lượng giao hàng

---

### 9. `returns.csv` — Trả hàng
**Shape:** 39,939 bản ghi × 7 cột

| Cột | Kiểu | Giá trị |
|-----|------|---------|
| `return_id` | str | PK |
| `order_id` | int | FK → orders |
| `product_id` | int | FK → products |
| `return_date` | date | 11/07/2012 → 31/12/2022 |
| `return_reason` | str | **wrong_size**, defective, changed_mind, not_as_described, late_delivery |
| `return_quantity` | int | Số lượng trả |
| `refund_amount` | float | Số tiền hoàn lại |

**💡 Điểm quan trọng:**
- **39,939 / 646,945 ≈ 6.2%** tỷ lệ trả hàng tổng thể
- `wrong_size` là lý do phổ biến nhất cho Streetwear (Q3)
- Chỉ đơn có `order_status = 'returned'` mới có bản ghi trong bảng này

---

### 10. `reviews.csv` — Đánh giá Sản phẩm
**Shape:** 113,551 đánh giá × 7 cột

| Cột | Kiểu | Giá trị |
|-----|------|---------|
| `review_id` | str | PK |
| `order_id` | int | FK → orders |
| `product_id` | int | FK → products |
| `customer_id` | int | FK → customers |
| `review_date` | date | 10/07/2012 → 31/12/2022 |
| `rating` | int | **1–5** (sao) |
| `review_title` | str | 18 loại tiêu đề chuẩn hoá ("Excellent product!", "Poor quality"...) |

**💡 Điểm quan trọng:**
- ~**17.5% đơn delivered có review** (113,551 / 646,945)
- `rating` từ 1–5 → có thể phân tích tương quan với delivery time, product category
- `review_title` đã được chuẩn hoá thành 18 nhãn cố định → dễ phân tích sentiment

---

## 📈 LỚP 3: ANALYTICAL — Dữ liệu Phân tích

### 11. `sales.csv` — Doanh thu Hàng ngày *(TARGET chính)*
**Shape:** 3,833 ngày × 3 cột

| Cột | Kiểu | Thống kê |
|-----|------|----------|
| `Date` | date | 04/07/2012 → 31/12/2022 |
| `Revenue` | float | Min: 279,814 \| **Mean: 4,286,584** \| Max: 20,905,271 |
| `COGS` | float | Min: 236,576 \| **Mean: 3,695,134** \| Max: 16,535,858 |

**💡 Điểm quan trọng:**
- Đây là **file train** cho bài toán Phần 3
- `Revenue` và `COGS` là **tổng toàn bộ giao dịch trong ngày** (đã được tổng hợp)
- **Phân chia train/test:**
  - Train: sales.csv (2012–2022) — có Revenue thật
  - Test: sample_submission.csv (2023–2024) — cần dự báo
- Gross Profit = Revenue - COGS → Mean ~591,450đ/ngày ≈ margin 13.8%

---

### 12. `sample_submission.csv` — File Nộp Mẫu
**Shape:** 549 ngày × 3 cột

| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| `Date` | date | 01/01/2023 → 01/07/2024 |
| `Revenue` | float | Giá trị mẫu (placeholder) — bạn phải thay bằng dự báo của mình |
| `COGS` | float | Giá trị mẫu (placeholder) |

**⚠️ Lưu ý quan trọng:**
- Giá trị Revenue/COGS trong file này **KHÔNG phải đáp án** — chỉ là ví dụ định dạng
- Kaggle mới có giá trị thật để chấm điểm
- Phải **giữ nguyên thứ tự 549 dòng** khi nộp

---

## ⚙️ LỚP 4: OPERATIONAL — Dữ liệu Vận hành

### 13. `inventory.csv` — Tồn kho Cuối tháng
**Shape:** 60,247 dòng × 17 cột *(1 dòng = 1 sản phẩm × 1 tháng)*

| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| `snapshot_date` | date | Ngày cuối tháng — 07/2012 → 12/2022 |
| `product_id` | int | FK → products |
| `stock_on_hand` | int | Tồn kho cuối tháng |
| `units_received` | int | Hàng nhập kho trong tháng |
| `units_sold` | int | Số lượng bán ra trong tháng |
| `stockout_days` | int | Số ngày hết hàng trong tháng |
| `days_of_supply` | float | Số ngày tồn kho còn đáp ứng được |
| `fill_rate` | float | **Trung bình 96.13%** — tỷ lệ đơn hàng được đáp ứng đủ hàng |
| `stockout_flag` | int | **67.34%** tháng có xảy ra hết hàng |
| `overstock_flag` | int | **76.26%** tháng bị tồn kho vượt mức |
| `reorder_flag` | int | Cờ cần tái đặt hàng |
| `sell_through_rate` | float | Tỷ lệ đã bán / tổng hàng sẵn có |
| `product_name, category, segment` | str | Denormalized từ products (tiện tra cứu) |
| `year, month` | int | Trích từ snapshot_date |

**💡 Điểm quan trọng:**
- **67% tháng có hết hàng** nhưng **fill_rate vẫn đạt 96%** → hết hàng ngắn hạn, phục hồi nhanh
- **76% tháng bị overstock** → vấn đề cân bằng tồn kho nghiêm trọng
- Dữ liệu này có thể dùng làm **feature cho forecasting** (tồn kho tháng trước ảnh hưởng doanh thu tháng này)

---

### 14. `web_traffic.csv` — Lưu lượng Website
**Shape:** 3,652 ngày × 7 cột *(6 nguồn × ~609 ngày mỗi nguồn)*

| Cột | Kiểu | Thống kê |
|-----|------|----------|
| `date` | date | 01/01/2013 → 31/12/2022 |
| `sessions` | int | **Mean: 25,042** \| Max: 50,947 |
| `unique_visitors` | int | Lượt khách duy nhất |
| `page_views` | int | Tổng lượt xem trang |
| `bounce_rate` | float | **Mean: 0.45%** (rất thấp) |
| `avg_session_duration_sec` | float | Thời gian trung bình mỗi phiên (giây) |
| `traffic_source` | str | organic_search: 1,090 \| paid_search: 784 \| social_media: 632 \| email_campaign: 505 \| referral: 375 \| direct: 266 |

**💡 Điểm quan trọng:**
- Mỗi ngày có **nhiều dòng** (1 dòng/nguồn) → cần group by date khi dùng
- `email_campaign` có bounce rate thấp nhất (Q4)
- **Bắt đầu từ 01/01/2013** (không có 2012) → cần xử lý khi merge với sales.csv
- Dùng làm **external feature** cho forecasting: sessions tăng → thường Revenue tăng

---

## 🔗 Hướng dẫn Join các bảng

### Các Join hay dùng nhất

```python
import pandas as pd

# 1. Doanh thu theo vùng địa lý
orders_geo = orders.merge(geography[['zip','region']], on='zip')
orders_items = orders_geo.merge(order_items, on='order_id')
orders_items['net_revenue'] = orders_items['unit_price'] * orders_items['quantity'] - orders_items['discount_amount']
revenue_by_region = orders_items.groupby('region')['net_revenue'].sum()

# 2. Tỷ lệ trả hàng theo danh mục sản phẩm
returns_cat = returns.merge(products[['product_id','category']], on='product_id')
items_cat   = order_items.merge(products[['product_id','category']], on='product_id')
return_rate = returns_cat.groupby('category').size() / items_cat.groupby('category').size()

# 3. Đơn hàng theo nhóm tuổi khách hàng
cust_orders = orders.merge(customers[['customer_id','age_group']], on='customer_id')
avg_orders_age = cust_orders.groupby('age_group')['order_id'].count() / customers.groupby('age_group')['customer_id'].count()

# 4. Delivery time vs Review rating
ship_review = shipments.merge(reviews[['order_id','rating']], on='order_id')
ship_review['delivery_days'] = (pd.to_datetime(ship_review['delivery_date']) - pd.to_datetime(ship_review['ship_date'])).dt.days
corr = ship_review[['delivery_days','rating']].corr()

# 5. Web traffic (tổng theo ngày) merge với sales
web_daily = web_traffic.groupby('date').agg({'sessions':'sum','unique_visitors':'sum'}).reset_index()
web_daily['date'] = pd.to_datetime(web_daily['date'])
sales_web = sales.merge(web_daily.rename(columns={'date':'Date'}), on='Date', how='left')
```

---

## ⚠️ Các Lưu ý Quan trọng Khi Làm Việc Với Data

| Vấn đề | File | Cách xử lý |
|--------|------|-----------|
| `web_traffic` bắt đầu từ 2013 (không có 2012) | web_traffic.csv | Merge `how='left'` → NaN cho 2012, fillna(0) hoặc interpolate |
| `promotions.applicable_category` có 40/50 null | promotions.csv | Null = áp dụng **tất cả** danh mục — không phải missing |
| `order_items` có 714K dòng > `orders` 647K | order_items.csv | Bình thường — 1 đơn nhiều sản phẩm |
| `shipments` ít hơn `orders` | shipments.csv | Chỉ đơn shipped/delivered/returned mới có shipment |
| `inventory` có 67% stockout nhưng fill_rate 96% | inventory.csv | Stockout ngắn hạn, không ảnh hưởng nhiều đến doanh thu |
| `sample_submission` đã có Revenue/COGS | sample_submission.csv | Đây là giá trị **placeholder**, không phải đáp án |
