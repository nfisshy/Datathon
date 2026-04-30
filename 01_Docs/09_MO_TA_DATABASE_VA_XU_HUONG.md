# BÁO CÁO PHÂN TÍCH TỔNG QUAN DỮ LIỆU & XU HƯỚNG KINH DOANH (2012 - 2022)

Tài liệu này cung cấp bức tranh toàn cảnh về bộ dữ liệu của doanh nghiệp E-commerce (Thời trang Outdoor/Streetwear) và phân tách rõ ràng giữa các CÁC SỰ THẬT TỪ DỮ LIỆU (Facts) và CÁC GIẢ THUYẾT DỰ BÁO (Hypotheses) để thuận tiện cho việc trình bày với Ban giám khảo.

---

## PHẦN 1: TỔNG QUAN 15 BẢNG DỮ LIỆU (DATABASE OVERVIEW)

Bộ dữ liệu trải dài từ **04/07/2012 đến 31/12/2022**, được chia thành 4 lớp (Layers):

1.  **Master (Dữ liệu nền tảng):** Bao gồm `products` (danh mục), `customers` (thông tin người dùng), `geography` (địa lý) và `promotions` (các chiến dịch khuyến mãi cố định). 
2.  **Transaction (Dữ liệu giao dịch):** `orders` (trạng thái đơn), `order_items` (chi tiết sản phẩm trong đơn), `payments` (phương thức thanh toán), `shipments` (vận chuyển), `returns` (lý do trả hàng), `reviews` (đánh giá). Điểm đáng chú ý là tỷ lệ hoàn hàng chỉ ~6% và tỷ lệ hủy đơn ổn định ở mức ~9%.
3.  **Analytical (Dữ liệu tổng hợp):** Bảng `sales` chứa Doanh thu (Revenue) và Giá vốn (COGS) tổng hợp theo từng ngày. Đây là mục tiêu dự báo chính cho các năm tương lai.
4.  **Operational (Dữ liệu vận hành):** Bảng `inventory` (chụp ảnh tồn kho cuối tháng) và `web_traffic` (lượng truy cập hàng ngày). 

**⚠️ Điểm mù Dữ liệu (Data Blindspot):** Toàn bộ dữ liệu kết thúc vào 31/12/2022. Tuy nhiên, bài toán yêu cầu dự báo doanh thu cho tập test từ **2023 - 2024**. Do đó, mọi mô hình không được phép sử dụng dữ liệu giao dịch trực tiếp từ tương lai (như web traffic của 2023) mà phải thông qua ngoại suy.

---

## PHẦN 2: CÁC XU HƯỚNG CHÍNH XÁC TỪ DỮ LIỆU (FACTS)
*(Đây là những diễn biến đo lường được bằng những con số 100% có thực trong lịch sử doanh nghiệp)*

### 2.1. "Mùa Gặt" Mùa Hè
*   Tháng 4, 5, và 6 hàng năm là đỉnh cao của doanh nghiệp. Doanh thu, lợi nhuận, lượng truy cập web và lượng hàng nhập kho đều đồng loạt đạt đỉnh trong 3 tháng này. Nó thường gắn liền với sự kiện `Mid-Year Sale`.

### 2.2. Chu Kỳ Xả Lỗ 2 Năm (Sự kiện tháng 8 năm lẻ)
*   Trong suốt 11 năm, cứ vào **Tháng 8 của các Năm Lẻ** (2013, 2015, 2017, 2019, 2021), lợi nhuận của doanh nghiệp luôn bị **âm sâu**.
*   Nguyên nhân được đối chiếu từ bảng `promotions` là do chiến dịch `Urban Blowout` (giảm giá 50%). Công ty bán hàng dưới giá vốn để dọn sạch kho, chuẩn bị không gian cho dòng sản phẩm thu đông mới (`Fall Launch`). Ở các năm chẵn, họ không chạy chiến dịch này và bán nguyên giá.

### 2.3. Khủng Hoảng Chuyển Đổi (2019 - 2022)
*   Giai đoạn 2013 - 2018: Số lượng đơn hàng ổn định ở mức ~80,000 đơn/năm.
*   Giai đoạn 2019 - 2022: Số lượng đơn hàng **rơi tự do xuống còn ~35,000 đơn/năm**. Doanh thu và lợi nhuận giảm gần một nửa.
*   **Điểm nghịch lý:** Lượng truy cập Web (`web_traffic`) trong giai đoạn này **không hề giảm**, ngược lại còn **tăng kỷ lục** từ 8 triệu lên 11 triệu lượt. Điều này khẳng định "Tỷ lệ chuyển đổi" (Conversion Rate) đã sụp đổ. Khách hàng vào website rất nhiều nhưng từ chối mua hàng.

### 2.4. Bão Hòa Lượng Khách Hàng (S-Curve)
*   Số lượng khách hàng tạo tài khoản mới bùng nổ ở giai đoạn đầu (2012-2015) nhưng **giảm tốc dần đều** ở giai đoạn sau (2018-2022). Biểu đồ lượng người dùng lũy kế tạo thành một đường cong thoải dần, chứng tỏ thị trường khách hàng tiềm năng đã dần cạn kiệt.

---

## PHẦN 3: CÁC GIẢ THUYẾT & DỰ BÁO VĨ MÔ (HYPOTHESES & PREDICTIONS)
*(Đây là phần suy luận logic từ người làm Data Science để xây dựng mô hình dự báo tương lai)*

### 3.1. Giả thuyết "Cú Sốc COVID-19" giải thích cho sự suy thoái
*   Sự đứt gãy cấu trúc dữ liệu từ năm 2019 đến 2022 (Traffic tăng nhưng Đơn hàng giảm) khớp hoàn toàn với khoảng thời gian đại dịch COVID-19 và suy thoái kinh tế.
*   **Giải thích:** Do bị giãn cách xã hội, người dân có nhiều thời gian lướt web (hiệu ứng Window Shopping). Nhưng do thắt chặt hầu bao và không có nhu cầu ra đường (hàng Outdoor/Streetwear), họ không chốt đơn.
*   **Ứng dụng vào Mô hình:** Nhóm Data Science quyết định mã hóa giai đoạn này thành một biến cờ `is_covid_era`. Biến này báo cho mô hình AI biết thị trường đang trong trạng thái "bất thường" để không bị nhầm lẫn với giai đoạn vàng son trước đó.

### 3.2. Dự báo "Mua Sắm Trả Thù" (Revenge Shopping) cho 2023 - 2024
*   Nếu giả định năm 2023 dịch bệnh kết thúc và kinh tế mở cửa, nhu cầu bị dồn nén suốt 3 năm sẽ bùng nổ trở lại.
*   **Nguy cơ Mô hình (Concept Drift):** Nếu mô hình Machine Learning (XGBoost) chỉ học từ dữ liệu nghèo nàn của 2020-2022, nó sẽ quen với "bình thường mới" và dự báo doanh thu của 2024 rất thấp (Under-forecasting). Mô hình gốc không biết cách ngoại suy sự tăng trưởng chưa từng thấy.
*   **Giải pháp Đề xuất:** Áp dụng Kiến trúc Mô hình Lai (Hybrid Modeling). Sử dụng Hồi quy tuyến tính (Linear Regression) kết hợp tập khách hàng lũy kế để vẽ đường Xu hướng vĩ mô (Trend) hướng lên cho năm 2024; sau đó dùng XGBoost để vẽ Tính mùa vụ (Seasonality) đè lên trên đường Trend đó.
