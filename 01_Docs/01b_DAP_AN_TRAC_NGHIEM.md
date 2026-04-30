# ✅ ĐÁP ÁN & LỜI GIẢI — PHẦN 1 TRẮC NGHIỆM

> **DATATHON 2026 — The Gridbreakers | Vòng 1**  
> Tổng: 10 câu × 2 điểm = 20 điểm | Không trừ điểm sai

---

## 📋 Bảng đáp án nhanh

| Câu | A | B | C | D | **ĐÁP ÁN** | Điểm |
|-----|---|---|---|---|-----------|------|
| Q1 | 30 ngày | 90 ngày | **144 ngày** | 365 ngày | **C** | 2đ |
| Q2 | Premium | Performance | Activewear | **Standard** | **D** | 2đ |
| Q3 | defective | **wrong_size** | changed_mind | not_as_described | **B** | 2đ |
| Q4 | organic_search | paid_search | **email_campaign** | social_media | **C** | 2đ |
| Q5 | 12% | 25% | **39%** | 54% | **C** | 2đ |
| Q6 | **55+** | 25–34 | 35–44 | 45–54 | **A** | 2đ |
| Q7 | West | Central | **East** | Cả ba bằng nhau | **C** | 2đ |
| Q8 | **credit_card** | cod | paypal | bank_transfer | **A** | 2đ |
| Q9 | **S** | M | L | XL | **A** | 2đ |
| Q10 | 1 kỳ | 3 kỳ | **6 kỳ** | 12 kỳ | **C** | 2đ |

---

## Q1 — Trung vị khoảng cách đơn hàng

**Đáp án: C) 144 ngày** ✅

### Kết quả tính toán từ dữ liệu thực

```
Median inter-order gap: 144.0 ngày
```

### Lời giải chi tiết

**Phương pháp:**
1. Sort `orders.csv` theo `(customer_id, order_date)` tăng dần
2. Dùng `groupby('customer_id')['order_date'].shift(1)` để lấy ngày đơn liền trước
3. Tính hiệu số ngày: `gap = order_date - prev_date`
4. Lọc chỉ lấy khách hàng có **hơn 1 đơn** (khách mua 1 lần không có gap)
5. Tính `median()` của toàn bộ gap

**Giải thích kết quả:**
- 144 ngày ≈ **~5 tháng** giữa 2 lần mua
- Điều này cho thấy khách hàng mua thời trang online không phải mua liên tục; thường theo mùa hoặc sự kiện đặc biệt
- Phân phối gap thường lệch phải (có một số khách mua rất thưa), nên median nhỏ hơn mean

**Tại sao không chọn các đáp án khác?**
| Đáp án | Lý do loại |
|--------|-----------|
| A) 30 ngày | Quá thấp — chỉ 1 tháng; thực tế khách mua ít thường xuyên hơn |
| B) 90 ngày | ~3 tháng — gần nhưng thấp hơn thực tế |
| D) 365 ngày | 1 năm — quá cao, đây là median không phải maximum |

---

## Q2 — Phân khúc có tỷ suất lợi nhuận gộp cao nhất

**Đáp án: D) Standard** ✅

### Kết quả tính toán từ dữ liệu thực

```
Gross Margin trung bình theo phân khúc:
segment
Standard       0.3134  (31.3%)  ← CAO NHẤT
Premium        0.2854  (28.5%)
All-weather    0.2842  (28.4%)
Activewear     0.2656  (26.6%)
Performance    0.2637  (26.4%)
Balanced       0.2580  (25.8%)
Trendy         0.2408  (24.1%)
Everyday       0.2363  (23.6%)
```

### Lời giải chi tiết

**Công thức:** `Gross Margin = (price - cogs) / price`

**Giải thích kết quả:**
- **Standard** có margin cao nhất (~31.3%) — điều này phản ánh thực tế:
  - Sản phẩm Standard có giá vốn thấp (sản xuất đơn giản, số lượng lớn)
  - Giá bán vẫn đủ cao để tạo biên tốt
- **Premium** đứng thứ 2 (~28.5%) — giá bán cao nhưng giá vốn cũng rất cao (nguyên liệu cao cấp, thủ công)
- **Trendy/Everyday** thấp nhất — thường là sản phẩm phổ thông, cạnh tranh nhiều → margin mỏng

**Tại sao không chọn Premium?**
- Nhiều người trực giác nghĩ "Premium = lợi nhuận cao nhất" nhưng đây là **tỷ suất %**, không phải giá trị tuyệt đối
- Premium cogs cao → margin % thấp hơn Standard

---

## Q3 — Lý do trả hàng phổ biến nhất cho Streetwear

**Đáp án: B) wrong_size** ✅

### Kết quả tính toán từ dữ liệu thực

```
Lý do trả hàng (Streetwear):
wrong_size          7,626  ← PHỔ BIẾN NHẤT
defective           4,330
not_as_described    3,854
changed_mind        3,830
late_delivery       2,159
```

### Lời giải chi tiết

**Phương pháp:**
```python
returns_with_cat = returns.merge(products[['product_id', 'category']], on='product_id')
streetwear = returns_with_cat[returns_with_cat['category'] == 'Streetwear']
print(streetwear['return_reason'].value_counts())
```

**Giải thích kết quả:**
- `wrong_size` chiếm **34.4%** trong các lý do trả hàng Streetwear
- **Thời trang Streetwear** có đặc thù:
  - Thường có phom áo/quần oversized, sizing không chuẩn như thời trang thông thường
  - Khách hàng trẻ tuổi hay order nhiều size để thử → trả hàng không vừa
  - Thiếu hướng dẫn size chart chuẩn hóa

**Business Insight:** Cần đầu tư vào:
1. Size guide chi tiết với số đo cụ thể (cm, inch)
2. Virtual try-on hoặc AR fitting
3. Chính sách đổi size miễn phí để giảm rào cản

---

## Q4 — Nguồn traffic có bounce rate thấp nhất

**Đáp án: C) email_campaign** ✅

### Kết quả tính toán từ dữ liệu thực

```
Bounce rate trung bình theo nguồn traffic:
traffic_source
email_campaign    0.004458  ← THẤP NHẤT
social_media      0.004476
paid_search       0.004478
referral          0.004499
organic_search    0.004504
direct            0.004511
```

### Lời giải chi tiết

**Giải thích kết quả:**
- **email_campaign** có bounce rate thấp nhất (~0.0045 ≈ 0.45%)
- **Lý do:** Khách nhận email thường là:
  - Người đã đăng ký (có intent mua hàng)
  - Được target theo hành vi mua trước đó
  - Email thường có CTA rõ ràng → click thẳng vào sản phẩm mong muốn
- **organic_search/direct** có bounce cao hơn vì nhiều người tìm kiếm chung chung, chỉ browse

**Lưu ý:** Sự chênh lệch nhỏ (0.0004) nhưng email_campaign nhất quán thấp nhất

---

## Q5 — Tỷ lệ order_items có khuyến mãi

**Đáp án: C) 39%** ✅

### Kết quả tính toán từ dữ liệu thực

```
Tỷ lệ dòng có promo_id không null: 38.7% ≈ 39%
```

### Lời giải chi tiết

**Phương pháp:**
```python
pct = order_items['promo_id'].notna().mean() * 100
# = (số dòng có promo_id) / (tổng dòng) × 100
```

**Giải thích kết quả:**
- ~39% dòng sản phẩm được áp dụng ít nhất 1 khuyến mãi
- Nếu tính cả `promo_id_2` (khuyến mãi thứ 2 — stackable), tỷ lệ sẽ cao hơn
- Con số này cao → công ty rất tích cực trong chiến lược promotion

**Tại sao không chọn 54%?**
- 54% quá cao — nếu quá nửa đơn đều có promo, sẽ ảnh hưởng margin nghiêm trọng
- 39% là mức hợp lý và phù hợp dữ liệu thực

---

## Q6 — Nhóm tuổi mua hàng nhiều nhất

**Đáp án: A) 55+** ✅

### Kết quả tính toán từ dữ liệu thực

```
Số đơn hàng trung bình theo nhóm tuổi:
age_group
55+      5.41  ← CAO NHẤT
45-54    5.36
35-44    5.34
25-34    5.25
18-24    5.23
```

### Lời giải chi tiết

**Phương pháp:**
```python
# Tổng đơn mỗi nhóm / Số khách trong nhóm đó
(total_orders_by_age_group) / (total_customers_by_age_group)
```

**Giải thích kết quả:**
- Nhóm **55+** trung bình ~5.41 đơn/khách — cao nhất dù nhiều người không nghĩ vậy
- Điều này phản ánh **customer lifetime value cao** hơn ở khách lớn tuổi:
  - Thu nhập ổn định, sẵn sàng chi tiêu nhiều hơn
  - Ít nhạy cảm với giá → ít bị distract bởi deals
  - Brand loyalty cao hơn → quay lại mua nhiều lần
- Sự chênh lệch nhỏ (5.23–5.41) cho thấy tất cả nhóm đều mua khá đều đặn

---

## Q7 — Vùng có tổng doanh thu cao nhất

**Đáp án: C) East** ✅

### Kết quả tính toán từ dữ liệu thực

```
Tổng doanh thu theo vùng:
region
East       7,291,151,xxx  (~7.3 tỷ)  ← CAO NHẤT
Central    4,719,491,xxx  (~4.7 tỷ)
West       3,670,227,xxx  (~3.7 tỷ)
```

### Lời giải chi tiết

**Phương pháp (cần join nhiều bảng):**
```
orders → (join geography via zip) → lấy region
orders → (join order_items) → tính doanh thu thuần mỗi dòng
         net_revenue = unit_price × quantity - discount_amount
→ group by region → sum
```

**Giải thích kết quả:**
- **East** chiếm ~46% tổng doanh thu — phù hợp với thực tế Việt Nam:
  - Miền Đông Nam Bộ (TP.HCM, Đồng Nai, Bình Dương) là trung tâm kinh tế lớn nhất
  - Mật độ dân số cao, thu nhập bình quân cao hơn
  - Hạ tầng logistics tốt → giao hàng nhanh → ít cancellation
- Central (~30%) và West (~24%) thấp hơn

---

## Q8 — Phương thức thanh toán phổ biến nhất trong đơn bị huỷ

**Đáp án: A) credit_card** ✅

### Kết quả tính toán từ dữ liệu thực

```
Số đơn cancelled theo phương thức thanh toán:
payment_method
credit_card      28,452  ← NHIỀU NHẤT (47.6%)
cod              15,468  (25.9%)
paypal            7,817  (13.1%)
apple_pay         5,190   (8.7%)
bank_transfer     2,535   (4.2%)
```

### Lời giải chi tiết

**Giải thích kết quả:**
- **credit_card** dẫn đầu vì nó là phương thức thanh toán phổ biến nhất trong dataset
- Đây là **tỷ lệ tuyệt đối**, không phải **tỷ lệ cancellation rate**
- Để phân tích chính xác hơn, cần tính:
  ```python
  cancelled_rate = (cancelled_by_method / total_by_method) × 100
  ```
- **Insight phân tích sâu:** credit_card có cancellation rate có thể *thấp hơn* COD (COD thường bị từ chối khi giao hàng)

---

## Q9 — Kích thước có tỷ lệ trả hàng cao nhất

**Đáp án: A) S** ✅

### Kết quả tính toán từ dữ liệu thực

```
Tỷ lệ trả hàng theo kích thước (returns/order_items):
size
S     0.05652  (5.65%)  ← CAO NHẤT
L     0.05625  (5.63%)
M     0.05566  (5.57%)
XL    0.05520  (5.52%)
```

### Lời giải chi tiết

**Công thức:**
```
Return Rate (size X) = Số bản ghi returns có size X / Số dòng order_items có size X
```

**Giải thích kết quả:**
- Size **S** có return rate cao nhất (5.65%) dù chênh lệch rất nhỏ
- Các lý do khả năng:
  1. Khách hàng nhỏ người thường khó tìm đúng size — nhiều thương hiệu sizing S không đồng nhất
  2. Size S hay sold out → khách order size khác rồi trả lại khi hàng về
  3. Độ tuổi mặc size S (trẻ) hay thay đổi sở thích → đổi ý trả hàng
- **Note:** Chênh lệch rất nhỏ (0.13pp) → cần thống kê kiểm định để xác nhận ý nghĩa

---

## Q10 — Kế hoạch trả góp có giá trị trung bình cao nhất

**Đáp án: C) 6 kỳ** ✅

### Kết quả tính toán từ dữ liệu thực

```
Giá trị thanh toán trung bình theo số kỳ:
installments
6     24,447  ← CAO NHẤT
3     24,400
12    24,246
1     24,113
2        708  ← Bất thường (ít đơn, có thể là đơn đặc biệt)
```

### Lời giải chi tiết

**Giải thích kết quả:**
- **6 kỳ** có giá trị đơn trung bình cao nhất (~24,447)
- Điều này phản ánh hành vi mua sắm:
  - Đơn giá trị **trung bình-cao** → chọn 6 kỳ để cân bằng giữa số tiền/tháng và tổng thời gian cam kết
  - Đơn giá trị **rất cao** → có thể chọn 12 kỳ để giảm tiền/tháng → avg thấp hơn vì có nhiều đơn nhỏ cũng chọn 12 kỳ
  - Đơn nhỏ → trả 1 lần (installment = 1) → avg thấp hơn
- Installment = 2 chỉ có ít đơn, giá trị bất thường thấp → outlier

**Tại sao không chọn 12 kỳ?**
- 12 kỳ trung bình ~24,246 < 6 kỳ ~24,447
- Đơn 12 kỳ có thể bao gồm cả khách mua đơn nhỏ nhưng muốn trả dài → kéo average xuống

---

## 🎯 Tổng hợp điểm mạnh & bẫy của đề

### ⚠️ Các câu có bẫy phổ biến

| Câu | Bẫy phổ biến | Đáp án đúng |
|-----|-------------|-------------|
| Q2 | Nghĩ "Premium = lợi nhuận cao nhất" | **Standard** — tỷ suất %, không phải giá trị tuyệt đối |
| Q7 | Dùng `sales.csv` thay vì join orders+geography | **East** — sales.csv không có cột region |
| Q8 | Tính tỷ lệ huỷ thay vì số lượng tuyệt đối | **credit_card** — câu hỏi hỏi "được dùng nhiều nhất" |
| Q10 | Chọn 12 kỳ vì "đơn lớn nhất" | **6 kỳ** — trung bình cao nhất, không phải tổng lớn nhất |

### 🏆 Chiến lược làm bài tối ưu

```python
# Template code nhanh cho mọi câu
# 1. Load data (1 lần đầu)
# 2. Mỗi câu: ~5-10 dòng pandas code
# 3. Verify: luôn print top 5 results để đối chiếu
# 4. Thời gian ước tính: 30-60 phút cho cả 10 câu
```

---

> 📄 Hướng dẫn code đầy đủ từng câu: **[01_HUONG_DAN_TRAC_NGHIEM.md](./01_HUONG_DAN_TRAC_NGHIEM.md)**
