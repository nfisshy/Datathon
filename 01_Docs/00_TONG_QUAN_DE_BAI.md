# 📊 TỔNG QUAN ĐỀ BÀI — DATATHON 2026: THE GRIDBREAKERS

> **Được tổ chức bởi:** VinTelligence — VinUniversity Data Science & AI Club  
> **Vòng:** 1 | **Chủ đề:** Breaking Business Boundaries  
> **Kaggle:** https://www.kaggle.com/competitions/datathon-2026-round-1

---

## 🎯 Bối cảnh tổng quát

Bộ dữ liệu mô phỏng hoạt động của một **doanh nghiệp thời trang thương mại điện tử tại Việt Nam** trong giai đoạn **04/07/2012 – 31/12/2022**, gồm 15 file CSV chia thành 4 lớp:

| Lớp | Mô tả |
|-----|-------|
| **Master** | Dữ liệu tham chiếu (sản phẩm, khách hàng, khuyến mãi, địa lý) |
| **Transaction** | Giao dịch thực tế (đơn hàng, chi tiết, thanh toán, vận chuyển, trả hàng, đánh giá) |
| **Analytical** | Dữ liệu doanh thu tổng hợp theo ngày |
| **Operational** | Tồn kho và lưu lượng web |

---

## 📁 Cấu trúc Dataset

```
datathon-2026-round-1/
├── products.csv          # Danh mục sản phẩm (price, cogs, category, segment, size, color)
├── customers.csv         # Thông tin khách hàng (zip, gender, age_group, acquisition_channel)
├── promotions.csv        # Chiến dịch khuyến mãi (type, discount, start/end date)
├── geography.csv         # Mã bưu chính → city, region, district
│
├── orders.csv            # Đơn hàng (order_date, status, payment_method, device_type)
├── order_items.csv       # Chi tiết đơn (product_id, quantity, unit_price, discount, promo)
├── payments.csv          # Thanh toán (payment_method, payment_value, installments)
├── shipments.csv         # Vận chuyển (ship_date, delivery_date, shipping_fee)
├── returns.csv           # Trả hàng (return_reason, return_quantity, refund_amount)
├── reviews.csv           # Đánh giá (rating 1-5, review_title)
│
├── sales.csv             # Doanh thu train: 04/07/2012 – 31/12/2022
├── sample_submission.csv # Định dạng nộp bài mẫu
│
├── inventory.csv         # Tồn kho cuối tháng (stock, fill_rate, stockout_flag...)
├── web_traffic.csv       # Lưu lượng web theo ngày (sessions, bounce_rate, traffic_source)
│
└── baseline.ipynb        # Notebook baseline của BTC
```

### Quan hệ giữa các bảng

```
geography.zip ←── customers.zip ←── orders.customer_id
                                         │
                              ┌──────────┼──────────────┐
                              ▼          ▼              ▼
                        payments    shipments       order_items
                                                        │
                                          ┌─────────────┼──────────────┐
                                          ▼             ▼              ▼
                                      products     promotions       returns
                                          │
                                          └──── inventory
```

---

## 📋 Cấu trúc Đề Bài — 3 Phần

### PHẦN 1 — Câu hỏi Trắc nghiệm
- **Điểm:** 20/100 (20%)
- **Số câu:** 10 câu × 2 điểm/câu
- **Quy tắc:** Không trừ điểm sai; chọn 1 đáp án đúng nhất
- **Yêu cầu:** Tính toán trực tiếp từ dữ liệu (SQL/Python queries)
- 📄 Xem hướng dẫn: [01_HUONG_DAN_TRAC_NGHIEM.md](./01_HUONG_DAN_TRAC_NGHIEM.md)
- 📄 Đáp án & lời giải: [01b_DAP_AN_TRAC_NGHIEM.md](./01b_DAP_AN_TRAC_NGHIEM.md)

### PHẦN 2 — Trực quan hoá & Phân tích EDA
- **Điểm:** 60/100 (60%) ← *Phần quan trọng nhất!*
- **Yêu cầu:** Khám phá tự do, tìm insight có giá trị kinh doanh
- **Tiêu chí đánh giá** (4 cấp độ phân tích):

| Cấp độ | Câu hỏi | Điểm tối đa |
|--------|---------|-------------|
| Descriptive | What happened? | (cơ bản) |
| Diagnostic | Why did it happen? | (trung bình) |
| Predictive | What is likely to happen? | (tốt) |
| **Prescriptive** | **What should we do?** | **(cao nhất)** |

- **Rubric chi tiết:**

| Tiêu chí | Điểm tối đa |
|----------|-------------|
| Chất lượng trực quan hoá | 15đ |
| Chiều sâu phân tích | 25đ |
| Insight kinh doanh | 15đ |
| Tính sáng tạo & kể chuyện | 5đ |
| **Tổng** | **60đ** |

- 📄 Xem hướng dẫn: [02_HUONG_DAN_EDA.md](./02_HUONG_DAN_EDA.md)

### PHẦN 3 — Mô hình Dự báo Doanh thu (Sales Forecasting)
- **Điểm:** 20/100 (20%)
- **Bài toán:** Dự báo cột `Revenue` cho giai đoạn 01/01/2023 – 01/07/2024
- **Metric:** MAE, RMSE, R² (đánh giá qua Kaggle leaderboard)
- **Nộp bài:** File `submission.csv` lên Kaggle

| Thành phần | Điểm tối đa |
|-----------|-------------|
| Hiệu suất mô hình (Kaggle leaderboard) | 12đ |
| Báo cáo kỹ thuật (pipeline, SHAP, cross-val) | 8đ |

- 📄 Xem hướng dẫn: [03_HUONG_DAN_FORECASTING.md](./03_HUONG_DAN_FORECASTING.md)

---

## 📤 Hướng dẫn Nộp bài

Mỗi đội cần nộp **4 thành phần**:

| # | Nộp ở đâu | Nội dung |
|---|-----------|----------|
| 1 | **Kaggle** | `submission.csv` — kết quả dự báo |
| 2 | **Form nộp bài** | Chọn đáp án trắc nghiệm (A/B/C/D) |
| 3 | **Form nộp bài** | Báo cáo PDF (NeurIPS LaTeX template, tối đa 4 trang) |
| 4 | **Form nộp bài** | Link GitHub repo (public, có README.md) |

### ⚠️ Điều kiện loại bài (Phần 3)
1. Sử dụng `Revenue`/`COGS` từ tập test làm đặc trưng → **bị loại toàn bộ Phần 3**
2. Dùng dữ liệu ngoài bộ được cung cấp
3. Không đính kèm mã nguồn hoặc kết quả không thể tái lập

### ⚠️ Điều kiện tham gia Vòng Chung kết
- Ít nhất **1 thành viên** có thể tham gia trực tiếp ngày **23/05/2026** tại VinUni, Hà Nội
- Cung cấp đầy đủ ảnh thẻ sinh viên của **tất cả thành viên**

---

## 🏆 Bảng điểm tổng hợp

| Phần | Nội dung | Điểm | Tỷ trọng |
|------|----------|------|----------|
| 1 | Câu hỏi Trắc nghiệm (MCQ) | 20 | 20% |
| 2 | Trực quan hoá & Phân tích EDA | 60 | 60% |
| 3 | Mô hình Dự báo Doanh thu | 20 | 20% |
| | **Tổng** | **100** | **100%** |

---

## 🔑 Chiến lược tối ưu điểm

```
Ưu tiên thời gian:
├── Phần 2 (EDA) — 60 điểm → Đầu tư NHIỀU NHẤT thời gian
│   └── Đạt cấp Prescriptive = phân tích + đề xuất hành động kinh doanh cụ thể
├── Phần 1 (MCQ) — 20 điểm → Dùng Python/pandas tính nhanh ~1-2 giờ
└── Phần 3 (Forecasting) — 20 điểm → Baseline + feature engineering thông minh
```

---

## 📚 File hướng dẫn chi tiết

| File | Nội dung |
|------|----------|
| [01_HUONG_DAN_TRAC_NGHIEM.md](./01_HUONG_DAN_TRAC_NGHIEM.md) | Cách giải 10 câu trắc nghiệm bằng Python/pandas |
| [01b_DAP_AN_TRAC_NGHIEM.md](./01b_DAP_AN_TRAC_NGHIEM.md) | Đáp án, lời giải và giải thích từng câu |
| [02_HUONG_DAN_EDA.md](./02_HUONG_DAN_EDA.md) | Framework EDA 4 cấp độ, ý tưởng biểu đồ & insight |
| [03_HUONG_DAN_FORECASTING.md](./03_HUONG_DAN_FORECASTING.md) | Pipeline ML dự báo doanh thu từng bước |
