# CHIẾN LƯỢC TẠO ĐẶC TRƯNG NÂNG CAO VÀ XỬ LÝ DATA LEAKAGE

Tài liệu này ghi chú lại các mối quan hệ đa bảng phức tạp và đặc biệt là giải quyết vấn đề rò rỉ dữ liệu (Data Leakage) khi phải dự báo doanh thu cho tập Test ở thì tương lai. Bạn có thể dựa vào đây để từ từ phân tích và xây dựng từng nhóm Feature một.

---

## 1. VẤN ĐỀ CHÍ MẠNG: DATA LEAKAGE (Rò rỉ dữ liệu tương lai)

**Bối cảnh:**
Mục tiêu của Datathon là dự đoán Doanh thu (Revenue) và Giá vốn (COGS) cho tập Test từ **01/01/2023 đến 01/07/2024** (18 tháng tương lai).
Tuy nhiên, tất cả các bảng lịch sử như `orders`, `web_traffic`, `inventory`, `shipments`, `reviews` đều **kết thúc vào ngày 31/12/2022**.

**Hệ quả:**
Bạn **KHÔNG THỂ** dùng Lượt truy cập (Sessions) hay Số lượng đơn hàng (Total Orders) của ngày hiện tại để dự đoán Doanh thu của ngày hôm đó trong tập Test (vì ở năm 2023, bạn chưa hề có dữ liệu của những bảng này). Nếu cố tình đưa vào tập Train, mô hình sẽ bị ngộ nhận, dẫn đến lỗi khi submit.

**Chiến lược giải quyết:**
Các mối quan hệ từ các bảng phụ chỉ có giá trị khi bạn biến chúng thành:
1.  **Đặc trưng mang tính quy luật (Deterministic / Time-based):** Biết trước tương lai dựa vào lịch.
2.  **Đường xu hướng (Trend):** Ngoại suy (Extrapolate) từ quá khứ.
3.  **Đặc trưng độ trễ (Lag Features):** Dùng dữ liệu quá khứ gần nhất (Chỉ tốt cho dự báo ngắn hạn).

---

## 2. CÁC MỐI QUAN HỆ CẦN PHÂN TÍCH VÀ CÁCH RÚT TRÍCH (EXTRACTION)

### 2.1. Mối quan hệ: `promotions.csv` $\rightarrow$ `sales.csv` (Mỏ Vàng Chu Kỳ)
Dù bảng promotions kết thúc năm 2022, phân tích dữ liệu cho thấy công ty này có lịch trình khuyến mãi **lặp lại cố định từng ngày** qua mọi năm:
*   *Spring Sale:* 18/03 - 17/04
*   *Mid-Year Sale:* 23/06 - 22/07
*   *Urban Blowout:* 30/07 - 02/09 (Chỉ năm Lẻ)
*   *Fall Launch:* 30/08 - 01/10
*   *Year-End Sale:* 18/11 - 02/01
*   *Rural Special:* 31/01 - 01/03

👉 **Việc cần làm:** Viết code để tạo ra một "Bộ Lịch Khuyến Mãi" cho các năm 2023 và 2024. Cứ đến ngày đó thì bật cờ `1`, ngày thường thì `0`. Tính chất lặp lại này khắc phục hoàn toàn việc thiếu data cho tương lai.

### 2.2. Mối quan hệ: `customers.csv` $\rightarrow$ `sales.csv` (Đường Xu Hướng - Trend)
*   **Bản chất:** Bảng khách hàng có cột `signup_date`. Nếu tính tổng số lượng khách hàng lũy kế (cumulative count) từ 2012 đến nay, ta sẽ có quy mô tập khách hàng. Tập khách hàng càng lớn $\rightarrow$ Doanh thu "đáy" (baseline) càng cao dần theo từng năm.
*   **Việc cần làm:** Vẽ biểu đồ tích lũy khách hàng. Sau đó dùng Hồi quy Tuyến tính (Linear Trend) để vẽ nối tiếp đường này cho 18 tháng của năm 2023-2024. Đây là biến Trend vĩ mô cực kỳ quan trọng.

### 2.3. Mối quan hệ: `payments.csv` & Ngày tháng $\rightarrow$ `sales.csv` (Chu Kỳ Ngắn Hạn)
*   **Bản chất:** Tâm lý mua sắm của người tiêu dùng phụ thuộc mạnh vào ngày nhận lương và ngày nghỉ.
*   **Việc cần làm:** Phân tích xem có sự gia tăng đột biến doanh thu vào các ngày:
    *   **Payday (Ngày nhận lương):** Đầu tháng (Mùng 1-3), giữa tháng (Ngày 15-17) hoặc cuối tháng.
    *   **Weekend (Cuối tuần):** Thứ 7 và Chủ Nhật.
    *   Sau khi xác nhận được có quy luật, hãy tạo các cột `is_payday`, `is_weekend` cho mọi ngày trong chuỗi thời gian.

### 2.4. Mối quan hệ: `reviews.csv`, `returns.csv` $\rightarrow$ `sales.csv` (Chỉ Báo Trễ - Lagging Indicators)
*   **Bản chất:** Một đơn hàng có trải nghiệm tồi (1 sao) hoặc trả hàng do sai size sẽ làm giảm uy tín, dẫn đến việc mất khách và sụt giảm doanh thu trong những tháng tiếp theo.
*   **Việc cần làm:** Nhóm bảng review/return theo tháng và tính ra điểm trung bình (Average Rating) hoặc Tỷ lệ hoàn trả (Return Rate). Tạo các biến trễ (Lag 1 tháng, 3 tháng). 
*   *Lưu ý:* Đặc trưng này khá yếu và rất khó dùng cho việc dự báo xa (năm 2024) vì ta sẽ bị cạn kiệt dữ liệu trễ sau khi vượt qua tháng 1/2023. Nên cân nhắc hạ mức độ ưu tiên.

---

## 3. TÓM TẮT THỨ TỰ ƯU TIÊN CHO MODEL
Để tiết kiệm thời gian và tối đa hóa điểm số, hãy phân tích và tạo tính năng theo mức độ ưu tiên sau:

1.  ⭐⭐⭐⭐⭐ **Lịch sự kiện (Event-based Calendar):** Khởi tạo cờ cho các chiến dịch Sale (Cố định ngày).
2.  ⭐⭐⭐⭐⭐ **Cờ chu kỳ (Time-based Seasonality):** Ngày trong tuần, Tháng trong năm, Ngày chẵn/lẻ, Cuối tuần/Ngày lương.
3.  ⭐⭐⭐⭐ **Xu hướng vĩ mô (Macro Trend):** Ngoại suy sự tăng trưởng của lượng khách hàng.
4.  ⭐⭐ **Chỉ báo trễ (Lag Indicators):** Tồn kho, Review, Return của quá khứ gần. (Cẩn thận khi dùng do thiếu data tương lai xa).
