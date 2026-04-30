# 🔍 CHI TIẾT TỪNG TRƯỜNG VÀ QUAN HỆ GIỮA CÁC BẢNG

---

## 1. Giải thích chi tiết từng trường

### `products.csv`

| Trường | Ý nghĩa thực tế | Giá trị hợp lệ | Dùng để làm gì |
|--------|----------------|----------------|----------------|
| `product_id` | Mã định danh duy nhất cho mỗi SKU | 1 – 2412 | Join với order_items, returns, reviews, inventory |
| `product_name` | Tên đầy đủ sản phẩm | Chuỗi tự do | Hiển thị, không dùng để group |
| `category` | Nhóm sản phẩm lớn | Streetwear, Outdoor, Casual, GenZ | Group phân tích doanh thu, trả hàng |
| `segment` | Phân khúc thị trường nhắm đến | Premium, Standard, Activewear, Performance, All-weather, Balanced, Trendy, Everyday | Phân tích margin, định giá |
| `size` | Kích cỡ vật lý sản phẩm | S, M, L, XL | Phân tích tỷ lệ trả hàng theo size |
| `color` | Màu sắc sản phẩm | 10 màu | Phân tích xu hướng màu sắc |
| `price` | Giá bán lẻ niêm yết (VNĐ) | 9 – 40,950 | Tính margin = (price-cogs)/price |
| `cogs` | Cost of Goods Sold — Giá vốn | Luôn < price | Tính lợi nhuận gộp |

> **Công thức quan trọng:**
> - `gross_margin = (price - cogs) / price` → Standard cao nhất ~31.3%
> - `gross_profit_per_unit = price - cogs`

---

### `customers.csv`

| Trường | Ý nghĩa thực tế | Lưu ý |
|--------|----------------|-------|
| `customer_id` | Mã khách hàng duy nhất | PK, dùng join với orders, reviews |
| `zip` | Mã bưu chính nơi khách ở | FK → geography; khác với zip giao hàng trong orders |
| `city` | Tên thành phố của khách | Denormalized từ geography (tiện dùng) |
| `signup_date` | Ngày đăng ký tài khoản | Dùng tính customer tenure: `order_date - signup_date` |
| `gender` | Giới tính | Female/Male/Non-binary — không có null trong thực tế |
| `age_group` | Nhóm tuổi | 18-24, 25-34, 35-44, 45-54, 55+ |
| `acquisition_channel` | Kênh marketing khách đăng ký qua | organic_search là phổ biến nhất (30%) |

> ⚠️ `customers.zip` ≠ `orders.zip`
> - `customers.zip` = nơi khách sinh sống
> - `orders.zip` = địa chỉ giao hàng của đơn đó (có thể khác nhau)

---

### `orders.csv`

| Trường | Ý nghĩa thực tế | Lưu ý |
|--------|----------------|-------|
| `order_id` | Mã đơn hàng duy nhất | PK — join với mọi bảng transaction |
| `order_date` | Ngày khách đặt hàng | Dùng để tính features thời gian |
| `customer_id` | Khách hàng đặt đơn | FK → customers |
| `zip` | Địa chỉ giao hàng | FK → geography — dùng để phân tích địa lý |
| `order_status` | Trạng thái xử lý đơn | Xem vòng đời đơn hàng bên dưới |
| `payment_method` | Phương thức thanh toán ghi nhận lúc đặt | Lặp lại trong payments.csv (1:1) |
| `device_type` | Thiết bị đặt hàng | mobile > desktop > tablet |
| `order_source` | Kênh marketing dẫn đến đơn | Giống acquisition_channel nhưng cho từng đơn |

**Vòng đời đơn hàng (order_status):**
```
created → paid → shipped → delivered  (luồng thành công ~80%)
       └→ cancelled                    (hủy ~9.2%)
                  └→ returned          (trả hàng ~5.6%)
```

| Status | Số đơn | Có shipment? | Có returns? |
|--------|--------|-------------|------------|
| delivered | 516,716 | ✅ | ❌ |
| cancelled | 59,462 | ❌ | ❌ |
| returned | 36,142 | ✅ | ✅ |
| shipped | 13,773 | ✅ | ❌ |
| paid | 13,577 | ❌ | ❌ |
| created | 7,275 | ❌ | ❌ |

---

### `order_items.csv`

| Trường | Ý nghĩa thực tế | Công thức liên quan |
|--------|----------------|---------------------|
| `order_id` | Mã đơn hàng | FK → orders |
| `product_id` | Sản phẩm trong đơn | FK → products |
| `quantity` | Số lượng sản phẩm đặt | — |
| `unit_price` | Giá bán thực tế lúc mua | Có thể ≠ products.price (do sale/thời điểm) |
| `discount_amount` | Tổng tiền giảm cho dòng này | = f(quantity, unit_price, promo_type, discount_value) |
| `promo_id` | Khuyến mãi áp dụng | FK → promotions; null = không có KM |
| `promo_id_2` | Khuyến mãi thứ 2 (stackable) | Chỉ 206/714,669 dòng sử dụng |

> **Doanh thu thuần mỗi dòng:**
> ```python
> line_revenue = unit_price * quantity - discount_amount
> ```

---

### `payments.csv`

| Trường | Ý nghĩa | Lưu ý |
|--------|---------|-------|
| `order_id` | Mã đơn | 1:1 với orders — mỗi đơn đúng 1 payment |
| `payment_method` | Phương thức thanh toán | Giống orders.payment_method (redundant) |
| `payment_value` | Tổng tiền thanh toán | Bao gồm cả shipping_fee |
| `installments` | Số kỳ trả góp | 1 (trả 1 lần), 2, 3, 6, 12 kỳ |

> `payment_value` ≈ `sum(order_items.unit_price × quantity - discount_amount) + shipping_fee`

---

### `shipments.csv`

| Trường | Ý nghĩa | Lưu ý |
|--------|---------|-------|
| `order_id` | Mã đơn | FK → orders; chỉ có khi status = shipped/delivered/returned |
| `ship_date` | Ngày gửi hàng | Thường = order_date hoặc sau vài ngày |
| `delivery_date` | Ngày giao đến tay khách | Luôn ≥ ship_date |
| `shipping_fee` | Phí vận chuyển | 0 = miễn phí; được cộng vào payment_value |

> **Chỉ số quan trọng:**
> ```python
> delivery_time = delivery_date - ship_date  # số ngày giao hàng
> processing_time = ship_date - order_date   # số ngày xử lý trước khi giao
> ```

---

### `returns.csv`

| Trường | Ý nghĩa | Lưu ý |
|--------|---------|-------|
| `return_id` | Mã trả hàng | PK dạng chuỗi |
| `order_id` | Đơn hàng bị trả | FK → orders (status = returned) |
| `product_id` | Sản phẩm bị trả | FK → products; 1 đơn có thể trả nhiều sản phẩm khác nhau |
| `return_date` | Ngày khách gửi trả | Thường sau delivery_date vài ngày |
| `return_reason` | Lý do trả hàng | wrong_size, defective, changed_mind, not_as_described, late_delivery |
| `return_quantity` | Số lượng trả | ≤ quantity trong order_items |
| `refund_amount` | Tiền hoàn lại | ≤ payment_value của đơn |

---

### `reviews.csv`

| Trường | Ý nghĩa | Lưu ý |
|--------|---------|-------|
| `review_id` | Mã đánh giá | PK |
| `order_id` | Đơn được đánh giá | Chỉ đơn delivered mới có review |
| `product_id` | Sản phẩm được đánh giá | 1 đơn nhiều sản phẩm → nhiều reviews |
| `customer_id` | Khách đánh giá | FK → customers |
| `review_date` | Ngày đánh giá | Sau delivery_date |
| `rating` | Số sao | 1 (tệ) → 5 (tuyệt vời) |
| `review_title` | Tiêu đề đánh giá | 18 loại chuẩn hoá — dùng như sentiment label |

> **Mapping sentiment từ review_title:**
> - Tích cực (rating 4-5): "Excellent product!", "Great quality", "Highly recommend"...
> - Tiêu cực (rating 1-2): "Poor quality", "Very disappointed", "Would not recommend"...

---

### `inventory.csv`

| Trường | Ý nghĩa | Công thức / Lưu ý |
|--------|---------|-------------------|
| `snapshot_date` | Ngày cuối tháng | 1 dòng = 1 sản phẩm × 1 tháng |
| `product_id` | Mã sản phẩm | FK → products |
| `stock_on_hand` | Tồn kho cuối tháng | Số lượng thực tế còn trong kho |
| `units_received` | Hàng nhập trong tháng | Số lượng nhập từ nhà cung cấp |
| `units_sold` | Hàng bán trong tháng | Khác với order_items (đã trừ returns) |
| `stockout_days` | Số ngày hết hàng | 0 = không hết; max = số ngày trong tháng |
| `days_of_supply` | Số ngày tồn kho đủ dùng | = stock_on_hand / (units_sold / days_in_month) |
| `fill_rate` | Tỷ lệ đơn đủ hàng | 0-1; mean = 0.9613 |
| `stockout_flag` | Có hết hàng trong tháng? | 0/1; 67% tháng = 1 |
| `overstock_flag` | Tồn kho vượt mức? | 0/1; 76% tháng = 1 |
| `reorder_flag` | Cần tái đặt hàng? | 0/1 |
| `sell_through_rate` | Tỷ lệ đã bán | = units_sold / (stock_on_hand + units_sold) |

---

### `web_traffic.csv`

| Trường | Ý nghĩa | Lưu ý |
|--------|---------|-------|
| `date` | Ngày ghi nhận | 1 ngày có 6 dòng (1 per traffic_source) |
| `sessions` | Số phiên truy cập | Bao gồm cả bounce sessions |
| `unique_visitors` | Khách duy nhất | < sessions vì 1 người có thể nhiều phiên |
| `page_views` | Tổng lượt xem trang | page_views / sessions = pages per session |
| `bounce_rate` | Tỷ lệ thoát ngay | Thấp = tốt; email_campaign thấp nhất |
| `avg_session_duration_sec` | Thời gian TB mỗi phiên (giây) | Cao = người dùng quan tâm nhiều |
| `traffic_source` | Nguồn traffic | organic_search, paid_search, social_media, email_campaign, referral, direct |

---

## 2. Quan hệ chi tiết giữa các bảng

### Bảng quan hệ đầy đủ

| Bảng A | Bảng B | Trường nối | Cardinality | Điều kiện |
|--------|--------|-----------|-------------|-----------|
| `geography` | `customers` | `zip` | 1 : N | Mỗi mã zip có nhiều khách |
| `geography` | `orders` | `zip` | 1 : N | Mỗi zip có nhiều đơn giao hàng |
| `customers` | `orders` | `customer_id` | 1 : N | 1 khách nhiều đơn |
| `customers` | `reviews` | `customer_id` | 1 : N | 1 khách nhiều đánh giá |
| `orders` | `payments` | `order_id` | **1 : 1** | Mỗi đơn đúng 1 payment |
| `orders` | `shipments` | `order_id` | 1 : 0..1 | Chỉ đơn shipped/delivered/returned |
| `orders` | `returns` | `order_id` | 1 : 0..N | Chỉ đơn returned; có thể trả nhiều SP |
| `orders` | `reviews` | `order_id` | 1 : 0..N | Chỉ đơn delivered; ~17.5% có review |
| `orders` | `order_items` | `order_id` | 1 : N | 1 đơn nhiều dòng sản phẩm |
| `products` | `order_items` | `product_id` | 1 : N | 1 sản phẩm trong nhiều đơn |
| `products` | `returns` | `product_id` | 1 : N | 1 sản phẩm bị trả nhiều lần |
| `products` | `reviews` | `product_id` | 1 : N | 1 sản phẩm có nhiều đánh giá |
| `products` | `inventory` | `product_id` | 1 : N | 1 sản phẩm, 1 dòng/tháng |
| `promotions` | `order_items` | `promo_id` | 1 : 0..N | 1 promo dùng trong nhiều dòng |

---

### Chuỗi Join phổ biến

#### 🔗 Doanh thu theo vùng địa lý
```
orders ──(zip)──► geography ──(region)──► Tổng hợp
orders ──(order_id)──► order_items ──(net_revenue)
```
```python
revenue_by_region = (
    orders
    .merge(geography[['zip','region']], on='zip')
    .merge(order_items, on='order_id')
    .assign(net_revenue=lambda x: x.unit_price*x.quantity - x.discount_amount)
    .groupby('region')['net_revenue'].sum()
)
```

#### 🔗 Phân tích khách hàng theo độ tuổi + doanh thu
```
customers ──(customer_id)──► orders ──(order_id)──► order_items
                                    ──(age_group)──► Group by
```

#### 🔗 Hiệu quả khuyến mãi
```
order_items ──(promo_id)──► promotions ──(promo_type, discount_value)
            ──(discount_amount)──► So sánh với không có KM
```

#### 🔗 Chất lượng giao hàng → Đánh giá
```
orders ──(order_id)──► shipments ──(delivery_days)
orders ──(order_id)──► reviews ──(rating)
→ Tính tương quan delivery_days vs rating
```

#### 🔗 Tỷ lệ trả hàng theo sản phẩm
```
returns ──(product_id)──► products ──(category, segment, size)
order_items ──(product_id)──► products
→ return_rate = count(returns) / count(order_items) per group
```

#### 🔗 Tồn kho → Doanh thu (feature cho forecasting)
```
inventory ──(snapshot_date.month)──► sales ──(Date.month)
→ stockout tháng trước → Revenue tháng sau giảm?
```

---

### ⚠️ Những cạm bẫy khi Join

| Tình huống | Vấn đề | Cách xử lý |
|-----------|--------|-----------|
| `customers.zip` vs `orders.zip` | Hai cột zip khác nhau ý nghĩa | Dùng đúng zip theo mục đích: customers.zip = nơi ở, orders.zip = nơi giao |
| `web_traffic` không có 2012 | Merge với sales sẽ có NaN cho năm 2012 | `merge(..., how='left')` rồi `fillna(0)` |
| `order_items` nhiều hơn `orders` | Bình thường (1 đơn nhiều SP) | Đừng count order_items để đếm số đơn |
| `promotions.applicable_category` null | Null = áp dụng tất cả, không phải thiếu dữ liệu | Xử lý null riêng: null → áp dụng mọi danh mục |
| `reviews` chỉ cho đơn delivered | Inner join với shipments sẽ mất dữ liệu | Join với orders trước, lọc status='delivered' |
| `inventory` 1 dòng/tháng | Group by tháng trước khi join | `inventory.groupby(['product_id','month'])` |
