# TỔNG HỢP INSIGHTS & ĐỀ XUẤT FEATURE ENGINEERING CHO MÔ HÌNH DỰ BÁO

Tài liệu này đúc kết lại toàn bộ hành trình Khám phá Dữ liệu (EDA) về doanh thu và tồn kho, từ đó ánh xạ các phát hiện kinh doanh thành các biến số (Features) cụ thể để đưa vào huấn luyện mô hình Machine Learning (LightGBM/XGBoost).

---

## PHẦN 1: TỔNG HỢP INSIGHTS KINH DOANH (BUSINESS LOGIC)

Qua quá trình bóc tách dữ liệu đa chiều, chúng ta đã phát hiện ra 3 quy luật ngầm chi phối toàn bộ bức tranh tài chính của công ty:

### 1.1. "Mùa Gặt" Mùa Hè (Tháng 4, 5, 6)
*   **Hiện tượng:** Doanh thu, lợi nhuận và khối lượng nhập hàng đều đạt đỉnh trong năm.
*   **Bản chất:** Đây là mùa cao điểm mua sắm kết hợp với chiến dịch `Mid-Year Sale` (giảm nhẹ 18%). Công ty vận hành trơn tru nhất: Nhập số lượng lớn $\rightarrow$ Bán sạch ở giá tốt $\rightarrow$ Lợi nhuận biên cao nhất.

### 1.2. Chu Kỳ Xả Lỗ 2 Năm (Bí Ẩn Tháng 8 Năm Lẻ)
*   **Hiện tượng:** Cứ vào tháng 8 của các năm lẻ (2013, 2015, 2017, 2019, 2021), lợi nhuận công ty bị âm nặng nề (giảm 30% - 40%).
*   **Bản chất:** Tồn tại một "Chu kỳ bộ sưu tập thiết kế" kéo dài 2 năm. Vào cuối năm lẻ, để dọn đường cho chu kỳ thiết kế mới, công ty bắt buộc phải chạy chiến dịch `Urban Blowout` (giảm giá 50% dưới giá vốn) để dọn dẹp lượng hàng tồn dư thừa tích tụ suốt 2 năm qua.

### 1.3. Nghịch Lý Tồn Kho Tháng 8 (Hiệu ứng Bullwhip)
*   **Hiện tượng:** Tháng 8 xả kho mạnh tay nhưng tổng tồn kho (đường màu xám trên biểu đồ) không hề giảm.
*   **Bản chất:** Sự chồng chéo chiến lược. Mặc dù bộ phận Sales đang đẩy hàng cũ đi (Urban Blowout), bộ phận Thu mua lại ồ ạt nhập lượng lớn hàng thu đông mới về kho để chuẩn bị cho sự kiện `Fall Launch` (30/08).
*   **Hệ quả cho Data:** Cột Tổng tồn kho (`stock_on_hand`) chứa quá nhiều biến nhiễu. Việc dự đoán giảm giá không thể dùng cột này.

### 1.4. Quy Luật Lưu Lượng Web (Web Traffic Patterns)
*   **Hiện tượng:** Lưu lượng truy cập (Sessions) lặp lại một đường cong hình quả chuông lệch qua tất cả các năm. Đáy ở mùa Đông (Tháng 1-3, 10-12), đỉnh khổng lồ vào mùa Hè (Tháng 4-6) và một đỉnh phụ đứt gãy vào tháng 8.
*   **Bản chất:** Phản ánh nhu cầu mua sắm thực tế của khách hàng (Customer Demand). Lượng traffic tăng vọt đồng pha hoàn toàn với doanh thu mùa hè và các chiến dịch xả kho.
*   **Hệ quả cho Data:** Đây là một chỉ báo cực mạnh. Nó đóng vai trò làm điểm neo (baseline) chuẩn xác để dự báo các đợt bùng nổ doanh thu.

---

## PHẦN 2: ĐỀ XUẤT ĐẶC TRƯNG (FEATURE ENGINEERING)

Mô hình ML không hiểu "Mùa hè" hay "Hiệu ứng Bullwhip". Chúng ta phải mã hóa (encode) các quy luật trên thành các cột số. Dưới đây là bộ đặc trưng tối thượng cần tạo:

### Nhóm 1: Đặc Trưng Sự Kiện & Thời Gian (Binary Flags)
*Giải quyết bài toán Chu kỳ Mùa Hè và Chu kỳ Xả Lỗ.*

*   **`is_odd_year`** (1/0): `1` nếu là năm lẻ, `0` nếu là năm chẵn. Đây là "chìa khóa vàng" giúp mô hình bắt được quy luật xả kho 2 năm.
*   **`is_summer_peak`** (1/0): `1` nếu thuộc Tháng 4, 5, 6. Giúp mô hình tự tin dự báo doanh thu và lợi nhuận tăng vọt.
*   **`is_urban_blowout_active`** (1/0): Trích xuất từ bảng `promotions.csv`. Cờ này bật sáng ở tháng 7 và 8 năm lẻ. Báo hiệu cho mô hình chuẩn bị hạ dự báo lợi nhuận xuống mức âm.
*   **`is_fall_launch`** (1/0): Đánh dấu tháng 8, 9. Giúp mô hình bắt được nhịp độ nhập hàng.

### Nhóm 2: Đặc Trưng Độ Trễ Tồn Kho (Inventory Lags)
*Giải quyết bài toán Nghịch lý Tồn kho.*

*   **`overstock_pct_lag_1`**: Tỷ lệ tồn kho vượt mức của **1 tháng trước**. (VD: Báo cáo tháng 7 tồn kho ế 80%, giúp mô hình dự báo tháng 8 chắc chắn sẽ giảm giá xả hàng).
*   **`overstock_pct_lag_3`**: Độ trễ 3 tháng để mô hình thấy được "đà" tích tụ hàng ế.
*   *Lưu ý quan trọng:* **LOẠI BỎ hoặc HẠ TRỌNG SỐ** đặc trưng `stock_on_hand` hiện tại do nó bị nhiễu bởi hàng hóa của mùa vụ mới nhập về.

### Nhóm 3: Đặc Trưng Tỷ Lệ Cung Cầu (Ratio Features)
*Đo lường sức khỏe vận hành.*

*   **`receive_to_sold_ratio`** = `units_received / units_sold`. 
    *   Tỷ lệ này thường xấp xỉ 1.17 ở trạng thái bình thường. Nếu tỷ lệ này vượt quá cao liên tục, mô hình sẽ ngầm hiểu hàng đang ế, chuẩn bị có rủi ro về lợi nhuận.
*   **`fill_rate_lag_1`**: Tỷ lệ đáp ứng đơn hàng của tháng trước. Đo lường rủi ro bị mất doanh thu do Stockout (cháy hàng).

### Nhóm 4: Đặc Trưng Nhu Cầu Tương Tác (Web Traffic Features)
*Dự báo dựa trên ý định mua sắm của khách hàng.*

*   **`daily_sessions`** hoặc **`monthly_sessions`**: Chỉ báo đồng thời (Concurrent Indicator) cho thấy mức độ quan tâm hiện tại. Cột này có sức mạnh dự báo cực lớn cho doanh thu cùng kỳ.
*   **`sessions_lag_1`**, **`sessions_lag_3`**: Chỉ báo sớm (Leading Indicator). Lượt truy cập tăng ngày hôm nay thường báo hiệu doanh thu sẽ bùng nổ vào 1-3 ngày sau (khách hàng ngắm nghía trước, chờ sale để chốt đơn sau).
*   **`page_views_per_session`**: Đo lường mức độ tương tác sâu (khách hàng có đang săm soi nhiều sản phẩm không, hay chỉ vào rồi thoát ra - Bounce). Loại bỏ hẳn cột Cancel Rate vì đó chỉ là hằng số ngẫu nhiên.

### Nhóm 5: Đặc Trưng Xu Hướng Vĩ Mô (Macro Trend Features)
*Giải quyết bài toán Ngoại suy Tương lai (Data Leakage) và Bão hòa thị trường.*

*   **`cumulative_customers` (Tập khách hàng lũy kế):** Tính tổng số lượng khách hàng đã đăng ký tính đến ngày hiện tại bằng hàm `cumsum()`. Đặc trưng này tạo "nền móng" cho doanh thu (Baseline Revenue).
*   **`log_cumulative_customers` (Ngoại suy Logarit):** Vì tốc độ người đăng ký mới ngày càng giảm (Bão hòa thị trường), tuyệt đối **KHÔNG** dùng Hồi quy Tuyến tính (Linear) để dự phóng (extrapolate) số lượng khách hàng cho tập Test (2023-2024) vì sẽ làm mô hình bị Over-forecasting (Dự báo doanh thu ảo tưởng). Bạn phải biến đổi cột này bằng hàm Logarit (`np.log(cumulative_customers)`) hoặc dùng Hồi quy Logarit (Logarithmic Trend). Điều này sẽ uốn cong đường dự phóng đi ngang dần ở những năm cuối, phản ánh đúng thực trạng cạn kiệt tập khách hàng mới của công ty.

### Nhóm 6: Đặc Trưng Cú Sốc Vĩ Mô (Macroeconomic Shocks & Concept Drift)
*Xử lý sự đứt gãy cấu trúc thị trường (COVID-19 và Suy thoái) theo đúng luật Datathon.*

*   **`is_covid_era` (Cờ Đại Dịch):** Gán giá trị `1` cho các ngày thuộc năm 2020-2022, và `0` cho các năm còn lại. Mặc dù luật cấm dùng External Data, nhưng việc phân loại giai đoạn từ cột `Date` có sẵn là hoàn toàn hợp lệ. Cờ này giúp mô hình hiểu được "điểm đứt gãy" khi mà Web Traffic tăng cao nhưng Tỷ lệ chuyển đổi (Conversion Rate) lại rớt thảm hại do tâm lý "Window Shopping" lúc dịch bệnh.
*   **`is_post_covid_recovery` (Cờ Phục Hồi):** Gán giá trị `1` cho tập Test (2023-2024). Kết hợp cờ này với mô hình lai (Hybrid Model: Linear Regression + XGBoost) để báo hiệu cho phần Regression biết cần từ từ nâng đáy (Baseline) doanh thu lên, mô phỏng hiệu ứng mua sắm dồn nén (Revenge Shopping) khi dịch kết thúc.
*   **`holiday_flags` (Lễ hội Gom Nhóm - Clustering):** Tuyệt đối không xóa các ngày lễ doanh thu thấp, vì sự sụt giảm cũng là một tín hiệu (Negative Signal). Tự tạo 2 cờ phân loại dựa trên lịch cố định:
    *   `is_peak_holiday` (Cờ Lễ Đỉnh Cao): Gán = 1 cho các ngày 30/4, 1/5. Báo hiệu cho mô hình chuẩn bị đẩy doanh thu lên kịch trần.
    *   `is_flat_holiday` (Cờ Lễ Trầm Lắng): Gán = 1 cho Giáng sinh (25/12), Black Friday, Valentine (14/2)... Báo hiệu cho mô hình biết khách hàng đang bận đi chơi, cần ghìm doanh thu xuống để không bị ảo tưởng dù trùng với ngày nhận lương hay giữa tuần.

### Nhóm 7: Đặc Trưng Chu Kỳ Ngắn Hạn (Micro-Seasonality Features)
*Bắt nhịp độ mua sắm theo từng ngày của người tiêu dùng (Dựa trên phân tích Payday và Mid-week).*

*   **`is_midweek` (Cờ Giữa Tuần):** Gán `1` cho Thứ 4 và Thứ 5. Giúp mô hình bắt được hành vi "chốt đơn lén" trong giờ làm việc để kịp nhận hàng vào dịp cuối tuần.
*   **`is_payday` (Cờ Nhận Lương):** Gán `1` cho các ngày `28, 29, 30, 31` và `01, 02` hàng tháng. Báo hiệu "Hiệu ứng nhận lương" (Payday Effect) kích thích sức mua bùng nổ lúc đầu/cuối tháng.
*   **`is_summer_payday` (Cờ Siêu Bùng Nổ):** Một đặc trưng tương tác (Interaction Feature) được tạo ra bằng phép nhân: `is_summer_peak` * `is_payday`. Cờ này sẽ kích hoạt hệ số nhân dự báo lên mức kịch trần (Spike) cho các ngày chốt sổ của những tháng mùa hè vàng son (Ví dụ: 30/04, 31/05).

### Nhóm 8: Đặc Trưng Lịch sử Đồng dạng (Year-over-Year Lags)
*Giải quyết triệt để lỗi Data Leakage khi dự báo dài hạn (Long-term Forecasting) cho 18 tháng tương lai.*

*   **`revenue_lag_365` (Doanh thu cùng ngày năm ngoái):** Sử dụng hàm `shift()` kết hợp xử lý năm nhuận để lấy doanh thu của đúng ngày đó 1 năm trước. Cột này đóng vai trò là "Mỏ neo" (Baseline Anchor) vững chắc nhất cho dự báo mùa vụ.
*   **`revenue_lag_730` (Doanh thu cùng ngày 2 năm trước):** Vô cùng quan trọng để giải mã Chu kỳ xả lỗ 2 năm. Dự báo tháng 8 năm lẻ (vd: 2023) bắt buộc phải dùng mốc tham chiếu từ tháng 8 năm lẻ trước đó (2021) thay vì năm chẵn.
*   **`historical_month_avg` (Chỉ báo Trung bình lịch sử):** Thay vì dùng `daily_sessions` hay `units_received` của ngày hôm qua (dẫn tới việc không có data để dự đoán xa), ta sẽ tính trung bình của các chỉ báo đó trong cùng tháng của toàn bộ các năm quá khứ. Đặc trưng này hoàn toàn "vượt thời gian" và không bao giờ bị lỗi NaN trên tập Test.

---

## BƯỚC TIẾP THEO (NEXT STEPS)
1. Viết Script Python hợp nhất 3 bảng (Sales, Inventory, Promotions) lại theo `Year-Month` và `Product_ID`.
2. Lập trình sinh ra các Feature Lag và Feature Ratio bằng các hàm `shift()` của Pandas.
3. Chia tập Train/Test theo thời gian (Time-series split) và đưa vào huấn luyện bằng LightGBM.
