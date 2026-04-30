# 📊 Báo Cáo Phân Tích Chuyên Sâu: Giải Mã Biến Động Doanh Thu & Lợi Nhuận

Dựa trên những quan sát từ biểu đồ của bạn và đối chiếu chéo với cơ sở dữ liệu (`promotions.csv`), dưới đây là biên bản tổng kết các nguyên nhân gốc rễ và đề xuất trích xuất đặc trưng (Feature Engineering) cho mô hình Học máy.

---

## 1. Mùa Bùng Nổ: Tháng 4, 5, 6

### 🔍 Hiện tượng
Đây là chuỗi 3 tháng duy trì mức Doanh thu (Revenue) và Lợi nhuận (Profit) cao nhất và ổn định nhất trong năm.

### 💡 Nguyên nhân (Từ Database & Thực tế kinh doanh)
1. **Yếu tố tự nhiên (Natural Demand):** Đây là thời điểm giao mùa (Xuân - Hè). Thời tiết thay đổi khiến nhu cầu mua sắm quần áo mới (đặc biệt là đồ Outdoor và Streetwear) tăng vọt.
2. **Cú huých Marketing (Mid-Year Sale):** Cơ sở dữ liệu ghi nhận vào cuối tháng 6 (từ 23/06 đến 22/07) hàng năm, công ty luôn tung ra chiến dịch **Mid-Year Sale** với mức giảm giá `18%`. Mức giảm này "vừa đủ ngoạn mục" để kích cầu khủng khiếp, nhưng không chạm vào giá vốn (COGS) nên vẫn giữ được lợi nhuận khổng lồ.

### ⚙️ Đặc trưng cần xử lý (Features to Extract)
Thay vì chỉ dùng cột `Month`, hãy tạo thêm:
*   `is_summer_peak` (Biến cờ): Bằng `1` nếu là tháng 4, 5, 6. Bằng `0` cho các tháng khác.
*   `is_mid_year_sale` (Biến cờ): Bằng `1` nếu ngày đó rơi vào khoảng 23/06 đến 22/07 (Tra cứu từ `promotions.csv`).

---

## 2. Bí Ẩn Tháng 8: Lời - Lỗ Xen Kẽ (Quy Luật Chẵn Lẻ)

### 🔍 Hiện tượng
Riêng tháng 8 có sự phân cực kỳ lạ: Các năm lẻ (2013, 2015, 2017...) bị LỖ NẶNG (COGS > Revenue). Các năm chẵn (2012, 2014, 2016...) lại có LỢI NHUẬN RẤT CAO và ổn định.

### 💡 Nguyên nhân

#### Vì sao năm LẺ lại LỖ?
*   Vào cuối tháng 7 đến đầu tháng 9 của các năm lẻ, công ty kích hoạt chiến dịch **Urban Blowout** (Xả kho đường phố). 
*   Mức giảm giá của chiến dịch này là `Fixed 50.0` (rất lớn so với đơn giá trung bình). Đây là một chiến dịch "chảy máu" (Clearance Sale) cốt để dọn sạch kho mùa hè, bán dưới giá vốn chấp nhận lỗ.

#### Vì sao năm CHẴN lại LỜI CAO?
*   Vào các năm chẵn, công ty **KHÔNG chạy xả kho Urban Blowout**.
*   Thay vào đó, trong suốt gần 30 ngày của tháng 8, họ bán hàng với **nguyên giá (Full Price)**, không có đợt giảm giá sâu nào.
*   Đến tận ngày `30/08`, họ mới tung chiến dịch **Fall Launch** (Ra mắt bộ sưu tập Mùa Thu) với mức giảm giá rất nhẹ nhàng: `10%`. 
*   **Kết luận:** Bán hàng nguyên giá và bán hàng bộ sưu tập mới (Mùa thu) giúp biên lợi nhuận (Profit Margin) của tháng 8 năm chẵn neo ở mức vô cùng khỏe mạnh (khoảng 20%). Lợi nhuận cao ở đây đến từ "Chất" (Biên lãi cao) chứ không phải từ "Lượng" (Xả hàng ồ ạt).

### ⚙️ Đặc trưng cần xử lý (Features to Extract)
Đây là "mỏ vàng" cho mô hình dự báo. Phải tạo các biến sau:
*   `is_urban_blowout_active`: Cờ báo hiệu đang xả kho. (Nếu = 1, mô hình sẽ biết đường dự báo lợi nhuận âm).
*   `is_fall_launch_active`: Cờ báo hiệu bán bộ sưu tập mới.
*   `daily_max_discount`: Mức giảm giá cao nhất đang được áp dụng trong ngày hôm đó. (Nếu mức này lên tới 50, chắc chắn lợi nhuận sẽ giảm mạnh).

---

## 3. Gợi ý Nghiên cứu thêm (Các Đặc trưng Nâng cao)

Từ tư duy phân tích cực kỳ sắc bén của bạn, tôi gợi ý bạn có thể xử lý thêm các nhóm đặc trưng (Features) sau để nâng cao độ chính xác tuyệt đối cho mô hình:

1. **Đặc trưng Tương tác (Interaction Features): Tồn kho $\times$ Khuyến mãi**
   *   Tại sao công ty chỉ xả kho vào năm lẻ? Rất có thể do năm lẻ họ bị tồn đọng hàng quá nhiều.
   *   *Ý tưởng feature:* `stockout_lag_1` (Tình trạng tồn kho của tháng trước). Nếu tồn kho tháng trước quá cao (Overstock), kết hợp với tháng này là Tháng 8, mô hình tự động dự báo một đợt doanh thu xả hàng.

2. **Đặc trưng Sức khỏe Đơn hàng (Order Quality):**
   *   Từ bảng `orders.csv`, hãy tính biến `daily_cancel_rate` (Tỉ lệ hủy đơn mỗi ngày).
   *   Vào những ngày siêu sale (Mid-Year Sale), lượng đơn đặt rất nhiều nhưng tỷ lệ hủy cũng thường tăng vọt. Tính trung bình `cancel_rate_lag_365` (tỷ lệ hủy của ngày này năm ngoái) để trừ hao vào doanh thu thực tế.

3. **Đặc trưng Sự chú ý (Attention Features):**
   *   Sử dụng bảng `web_traffic.csv` để tính `web_sessions_lag_7` (Lượng truy cập web 7 ngày trước). 
   *   Trước khi Fall Launch diễn ra vào 30/08, người dùng thường lên web xem trước mẫu mã. Traffic tăng là chỉ báo sớm (Leading Indicator) cho doanh thu tăng trong những ngày kế tiếp.
