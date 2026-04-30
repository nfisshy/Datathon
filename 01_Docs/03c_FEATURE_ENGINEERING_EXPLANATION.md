# 🧠 Hướng Dẫn Chi Tiết: Feature Engineering Dự Báo Doanh Thu (Datathon 2026)

Tài liệu này được biên soạn dưới góc độ của một Chuyên gia Khoa học Dữ liệu (Data Scientist), nhằm giải thích cặn kẽ quá trình **Feature Engineering (Tạo Đặc Trưng)** từ database thô phục vụ cho mô hình dự báo doanh thu.

---

## 1. Cơ sở lý luận: Làm sao biết cần trích xuất đặc trưng nào?

Trong bài toán dự báo chuỗi thời gian (Time-Series Forecasting) nói chung và dự báo doanh thu nói riêng, một đặc trưng (feature) tốt phải giúp mô hình học được và trả lời được câu hỏi cốt lõi: **"Ngày hôm nay có gì đặc biệt so với những ngày khác khiến doanh thu tăng hay giảm?"**

Để xác định các đặc trưng cần trích xuất, chúng ta dựa vào 4 giả thuyết chính về các yếu tố chi phối doanh thu:

1.  **Tính mùa vụ và chu kỳ (Seasonality & Cyclicality):** Doanh thu thời trang phụ thuộc mạnh vào thời điểm trong năm (mùa đông bán áo khoác giá cao, cuối năm nhu cầu mua sắm tăng) và thời điểm trong tuần (cuối tuần mua nhiều hơn). $\rightarrow$ *Cần các Time Features.*
2.  **Quán tính và xu hướng (Autocorrelation & Trend):** Doanh thu có tính kế thừa. Nếu tuần trước bán tốt, khả năng cao tuần này cũng tốt (xu hướng). Doanh thu ngày hôm nay thường tương đồng với ngày này năm ngoái. $\rightarrow$ *Cần các Lag và Rolling Features.*
3.  **Hành vi và sự quan tâm của khách hàng (Leading Indicators):** Trước khi mua hàng (tạo Revenue), khách hàng phải truy cập web (Traffic) và đặt đơn (Orders). Lượng truy cập và số đơn đặt trước đó là tín hiệu sớm báo hiệu doanh thu. $\rightarrow$ *Cần External Features từ Web Traffic và Orders.*
4.  **Tác động từ vận hành và marketing (Operational & Marketing Impact):** Khuyến mãi (Promotions) thúc đẩy doanh thu ngay lập tức. Tình trạng hết hàng (Stockouts) kìm hãm doanh thu. $\rightarrow$ *Cần External Features từ Promotions và Inventory.*

Từ 4 định hướng này, chúng ta sẽ rà soát 14 bảng trong database để "chế tác" các features tương ứng.

---

## 2. Các nhóm đặc trưng tổng hợp từ Database

### Nhóm A: Time Features (Đặc trưng thời gian)

**Nguồn trích xuất:** Cột `Date` của bảng `sales.csv` (dữ liệu đích). Không cần join với bảng nào khác.

**Cách trích xuất:** Sử dụng các phép toán lịch (Calendar Math) trên cột Date.

```python
# Trích xuất các thành phần thời gian cơ bản
df['dayofweek'] = df['Date'].dt.dayofweek   # 0=Thứ 2 ... 6=Chủ nhật
df['month']     = df['Date'].dt.month       # Tháng 1-12
df['quarter']   = df['Date'].dt.quarter     # Quý 1-4
df['year']      = df['Date'].dt.year        # Năm

# Tạo cờ nhị phân (Binary Flags) cho các sự kiện/thời điểm đặc biệt
df['is_weekend'] = (df['Date'].dt.dayofweek >= 5).astype(int) # Cuối tuần
df['is_nov']     = (df['Date'].dt.month == 11).astype(int)    # Tháng 11 (Mùa sale)

# Xác định ngày siêu sale (Mega Sale Days)
df['is_sale_event'] = (
    ((df['Date'].dt.month == 11) & (df['Date'].dt.day >= 25)) | # Black Friday
    ((df['Date'].dt.month == 12) & (df['Date'].dt.day == 12)) | # 12.12
    ((df['Date'].dt.month == 11) & (df['Date'].dt.day == 11))   # 11.11
).astype(int)
```

**Ý nghĩa cho mô hình:**
*   Mô hình học được "pattern" của thời gian. Ví dụ: Nó sẽ tự động cộng thêm trọng số vào dự báo nếu `dayofweek = 5` (Thứ 7) hoặc `is_sale_event = 1`.
*   Giúp mô hình thiết lập "đường cơ sở" (baseline) chính xác cho từng thời điểm trong năm.

---

### Nhóm B: Lag Features (Đặc trưng trễ - Lịch sử doanh thu)

**Nguồn trích xuất:** Cột `Revenue` (và `COGS`) của bảng `sales.csv`.

**Cách trích xuất:** Sử dụng phép dịch chuyển (shift) để lấy giá trị của quá khứ.

```python
# Tạo biến trễ các ngày trước
df['rev_lag_7']   = df['Revenue'].shift(7)    # Doanh thu 1 tuần trước
df['rev_lag_30']  = df['Revenue'].shift(30)   # Doanh thu 1 tháng trước

# QUAN TRỌNG NHẤT: Lag của năm ngoái
df['rev_lag_365'] = df['Revenue'].shift(365)  # Cùng ngày năm ngoái
df['rev_lag_366'] = df['Revenue'].shift(366)  # Bù trừ cho năm nhuận
```

**⚠️ Lưu ý sống còn (Data Leakage):**
Do bài toán yêu cầu dự báo một khoảng thời gian dài (549 ngày từ 01/01/2023 đến 01/07/2024), ta không thể dùng `lag_1` (ngày hôm qua) hay `lag_7` cho tập test. Vì sao? Vì để dự báo cho ngày `2023-01-10`, ta cần `lag_7` tức là doanh thu của ngày `2023-01-03`, nhưng đây lại là ngày nằm trong khoảng tương lai ta chưa biết (chưa có dữ liệu thực tế).
**Giải pháp:** Chỉ sử dụng các lag có độ trễ lớn hơn khoảng test (vd: `lag >= 365`). Với `lag_365`, toàn bộ 549 ngày trong tập test đều có thể map về dữ liệu thực tế của giai đoạn train (2012-2022).

**Ý nghĩa cho mô hình:**
*   `rev_lag_365` đóng vai trò như một **"Anchor" (Mỏ neo)** hoàn hảo. Nếu ngày này năm ngoái doanh thu là 1 tỷ, khả năng cao năm nay doanh thu quanh mốc 1 tỷ (cộng trừ hệ số tăng trưởng). Nó bao hàm sẵn toàn bộ tính mùa vụ.

---

### Nhóm C: Rolling Statistics (Đặc trưng trượt - Xu hướng trung hạn)

**Nguồn trích xuất:** Cột `Revenue` của `sales.csv`, kết hợp `shift(365)` để chống rò rỉ dữ liệu.

**Cách trích xuất:** Tính trung bình (mean), độ lệch chuẩn (std) trên một cửa sổ thời gian (window).

```python
# BẮT BUỘC shift(365) TRƯỚC khi tính rolling để đảm bảo chỉ dùng dữ liệu lịch sử an toàn
df['roll_mean_30'] = df['Revenue'].shift(365).rolling(30).mean() # TB 30 ngày của năm ngoái
df['roll_std_30']  = df['Revenue'].shift(365).rolling(30).std()  # Độ biến động 30 ngày năm ngoái

# Tính toán xu hướng (Trend Ratio)
df['roll_mean_7']  = df['Revenue'].shift(365).rolling(7).mean()
df['roll_mean_90'] = df['Revenue'].shift(365).rolling(90).mean()
df['trend_ratio']  = df['roll_mean_7'] / (df['roll_mean_90'] + 1e-8)
```

**Ý nghĩa cho mô hình:**
*   Lag đơn lẻ (`lag_365`) có thể bị nhiễu do outlier (ví dụ ngày đó năm ngoái tự nhiên có bão, hoặc trúng ngày thứ 2). `roll_mean_30` làm "mượt" dữ liệu, cung cấp xu hướng nền tảng vững chắc hơn.
*   `trend_ratio` giúp mô hình nhận biết "gia tốc": Nếu `trend_ratio > 1`, nghĩa là doanh thu 1 tuần gần đây đang bùng nổ mạnh hơn trung bình 3 tháng qua, mô hình nên dự báo tích cực hơn.

---

### Nhóm D: External Features (Đặc trưng ngoại lai từ database)

Đây là nơi kiến thức về database ERD và kỹ năng SQL/Pandas phát huy tác dụng.

#### D1. Đơn hàng (`orders.csv`) $\rightarrow$ Sức mua tiềm năng
*   **Trích xuất:** `GROUP BY order_date` để tính tổng số đơn (`order_count`) và tỷ lệ hủy đơn (`cancel_rate`).
*   **Áp dụng:** Phải dùng `shift(365)` khi merge vào data tổng vì `orders` chỉ có đến 2022.
*   **Ý nghĩa:** `order_count_lag365` là Leading Indicator. Nếu lượng đặt hàng ngày này năm ngoái cao, doanh thu dự báo năm nay cũng sẽ cao. `cancel_rate` cho biết chất lượng của lượng đơn đó.

#### D2. Lưu lượng Web (`web_traffic.csv`) $\rightarrow$ Phễu khách hàng
*   **Trích xuất:** Dữ liệu web có 6 dòng/ngày (theo nguồn traffic). Cần `GROUP BY date` $\rightarrow$ `SUM(sessions)` và `MEAN(bounce_rate)`.
*   **Áp dụng:** Tương tự orders, cần `shift(365)` để dùng cho tập test. Chú ý: web data bắt đầu từ 2013, khi merge sẽ sinh ra NaN cho năm 2012, cần xử lý (ví dụ: điền bằng median).
*   **Ý nghĩa:** Traffic là đầu phễu. Nhiều người vào xem web (sessions cao) + quan tâm thật sự (bounce_rate thấp) sẽ chuyển hóa thành doanh thu.

#### D3. Khuyến mãi (`promotions.csv`) $\rightarrow$ Cú huých Marketing
*   **Trích xuất:** Với mỗi ngày `d` trong sales, đếm số lượng chiến dịch khuyến mãi mà `start_date <= d <= end_date`.
*   **Áp dụng:** **KHÔNG CẦN LAG**. Vì lịch khuyến mãi đã được lên kế hoạch từ trước, ta biết chính xác năm 2023-2024 có những ngày nào chạy sale.
*   **Ý nghĩa:** Rất mạnh. Giúp mô hình bật tăng dự báo trong những ngày được flag là có nhiều `active_promo_count`.

#### D4. Tồn kho (`inventory.csv`) $\rightarrow$ Sức khỏe vận hành
*   **Trích xuất:** Bảng này theo tháng (snapshot). `GROUP BY month` $\rightarrow$ tính `MEAN(fill_rate)` và `MEAN(stockout_flag)`.
*   **Áp dụng:** Merge vào data tổng dựa trên Khóa là `Tháng (YYYY-MM)`.
*   **Ý nghĩa:** Nếu `fill_rate` tháng trước thấp (không đủ hàng giao), doanh thu bị nghẽn. Nếu `stockout_pct` cao, tháng sau nhập nhiều hàng $\rightarrow$ doanh thu có thể phục hồi. Đây là tín hiệu ràng buộc từ phía nguồn cung (Supply-side).

---

## 3. Tổng kết Quy trình 10 Bước

1.  **Nạp dữ liệu:** Đọc các file `sales`, `orders`, `web`, `promotions`, `inventory`.
2.  **Khung dữ liệu (Skeleton):** Nối (concat) `sales.csv` (train) và `sample_submission.csv` (test) thành 1 bảng `full_df` theo cột `Date`.
3.  **Time Features:** Áp dụng datetime functions trực tiếp trên `full_df['Date']`.
4.  **Lag Features:** Tính `shift(365)`, `shift(730)` trên `Revenue`.
5.  **Rolling Features:** Tính `rolling().mean()` dựa trên cột `Revenue.shift(365)`.
6.  **Xử lý Orders:** Aggregate theo ngày, `shift(365)`, merge vào `full_df`.
7.  **Xử lý Web Traffic:** Aggregate theo ngày, xử lý NaN (cho 2012), `shift(365)`, merge vào `full_df`.
8.  **Xử lý Promotions:** Kiểm tra ngày nằm trong khoảng chiến dịch, tạo cột đếm số promo active.
9.  **Xử lý Inventory:** Aggregate theo tháng, merge vào `full_df` thông qua key là Năm-Tháng.
10. **Tách tập:** Cắt `full_df` trả lại `X_train` (2012-2022) và `X_test` (2023-2024) dựa trên ngày cắt. Bỏ đi các cột thô (`Date`, `Revenue` gốc), chỉ giữ lại mảng Features vừa tạo để đưa vào mô hình LightGBM/XGBoost.
