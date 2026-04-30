# 🤖 PHẦN 3 — HƯỚNG DẪN CHI TIẾT DỰ BÁO DOANH THU

---

## 1. Đề bài yêu cầu gì?

### Bài toán cốt lõi

> Dự báo **Revenue** (và COGS) cho mỗi ngày trong giai đoạn **01/01/2023 → 01/07/2024** (549 ngày).

```
INPUT:  Toàn bộ lịch sử (2012–2022) của 14 bảng dữ liệu
OUTPUT: Revenue và COGS cho 549 ngày trong tương lai
```

### Dữ liệu trực tiếp cho bài toán

| File | Vai trò | Nội dung |
|------|---------|---------|
| `sales.csv` | **Train set** | Date, Revenue, COGS — 3,833 ngày (2012–2022) |
| `sample_submission.csv` | **Template nộp bài** | 549 ngày cần dự báo (Revenue = placeholder) |

### Chỉ số đánh giá

| Metric | Công thức | Ý nghĩa | Mục tiêu |
|--------|-----------|---------|---------|
| **MAE** | `mean(|predict - actual|)` | Sai số tuyệt đối trung bình | Càng thấp càng tốt |
| **RMSE** | `sqrt(mean((predict-actual)²))` | Phạt nặng sai số lớn | Càng thấp càng tốt |
| **R²** | `1 - SS_res/SS_tot` | % phương sai được giải thích | Càng gần 1 càng tốt |

---

## 2. Tại sao không dùng thẳng sales.csv để train?

`sales.csv` chỉ có 3 cột: `Date, Revenue, COGS`. Mô hình cần **features** để học — không thể học từ 1 cột duy nhất.

```
Nếu chỉ dùng sales.csv:
  X_train = [Date]          ← vô nghĩa, model không học được gì
  y_train = [Revenue]

Cần tạo thêm:
  X_train = [dayofweek, month, lag_7, lag_365, roll_mean_30, ...]
  y_train = [Revenue]
```

---

## 3. Các nhóm Features và ý nghĩa

### Nhóm A — Time Features (từ cột Date)

```python
df['dayofweek']  = df['Date'].dt.dayofweek   # 0=Thứ Hai ... 6=Chủ Nhật
df['month']      = df['Date'].dt.month        # 1–12
df['quarter']    = df['Date'].dt.quarter      # 1–4
df['year']       = df['Date'].dt.year
df['dayofyear']  = df['Date'].dt.dayofyear    # 1–365
df['is_weekend'] = (df['Date'].dt.dayofweek >= 5).astype(int)
df['week']       = df['Date'].dt.isocalendar().week.astype(int)
```

**Vì sao cần?**
- Doanh thu thời trang có **tính mùa vụ rõ rệt**: tháng 11–12 (Black Friday, Giáng sinh) cao hơn tháng 2–3
- Cuối tuần thường cao hơn ngày thường (khách có thời gian mua sắm)
- Model cần biết "hôm nay là thứ mấy, tháng mấy" để dự báo đúng pattern

---

### Nhóm B — Lag Features (doanh thu lịch sử)

```python
# Doanh thu các ngày trước → dự báo hôm nay
df['lag_1']   = df['Revenue'].shift(1)    # hôm qua
df['lag_7']   = df['Revenue'].shift(7)    # tuần trước (cùng thứ)
df['lag_14']  = df['Revenue'].shift(14)   # 2 tuần trước
df['lag_30']  = df['Revenue'].shift(30)   # tháng trước
df['lag_90']  = df['Revenue'].shift(90)   # quý trước
df['lag_365'] = df['Revenue'].shift(365)  # cùng ngày năm ngoái ← QUAN TRỌNG NHẤT
df['lag_366'] = df['Revenue'].shift(366)  # buffer cho năm nhuận
```

**Vì sao cần?**
- Doanh thu có **autocorrelation**: hôm nay cao thường dẫn đến ngày mai cao
- `lag_365` cực kỳ quan trọng vì nắm bắt **pattern năm ngoái cùng thời điểm** — nếu 01/01/2022 doanh thu X thì 01/01/2023 cũng xấp xỉ X×(growth_rate)
- Model học được: "năm ngoái tháng 11 bùng nổ → năm nay tháng 11 cũng vậy"

**⚠️ Lưu ý khi dùng cho test set:**
- `lag_1` của ngày test đầu tiên (2023-01-01) = Revenue ngày 2022-12-31 ✅ (từ train)
- `lag_1` của ngày test thứ 2 (2023-01-02) = Revenue 2023-01-01 = chưa biết ❌
- **Giải pháp**: Dùng `lag_365` (luôn có từ train), hoặc dùng recursive prediction

```python
# Cách an toàn nhất: chỉ dùng lag >= 365 cho test set
safe_lags = [365, 366, 730]  # Luôn có từ train data
```

---

### Nhóm C — Rolling Statistics (xu hướng trung hạn)

```python
# Tính sau khi đã shift(1) để tránh data leakage
df['roll_mean_7']   = df['Revenue'].shift(1).rolling(7).mean()
df['roll_mean_14']  = df['Revenue'].shift(1).rolling(14).mean()
df['roll_mean_30']  = df['Revenue'].shift(1).rolling(30).mean()
df['roll_mean_90']  = df['Revenue'].shift(1).rolling(90).mean()
df['roll_std_7']    = df['Revenue'].shift(1).rolling(7).std()
df['roll_std_30']   = df['Revenue'].shift(1).rolling(30).std()
df['roll_max_30']   = df['Revenue'].shift(1).rolling(30).max()
df['roll_min_30']   = df['Revenue'].shift(1).rolling(30).min()

# Trend: so sánh rolling ngắn vs dài
df['trend_ratio']   = df['roll_mean_7'] / (df['roll_mean_90'] + 1e-8)
```

**Vì sao cần?**
- `roll_mean_7`: xu hướng ngắn hạn (tuần này tốt không?)
- `roll_mean_30`: xu hướng tháng (tháng này doanh thu đang lên hay xuống?)
- `roll_std_30`: độ biến động — ngày lễ thường có std cao
- `trend_ratio > 1`: doanh thu đang tăng so với trung bình dài hạn

---

### Nhóm D — Features từ Database khác (External)

#### D1. Từ `orders.csv` — Số đơn hàng theo ngày

```python
orders = pd.read_csv("orders.csv", parse_dates=['order_date'])

# Tổng đơn mỗi ngày
daily_orders = orders.groupby('order_date').agg(
    order_count     = ('order_id', 'count'),
    cancelled_count = ('order_status', lambda x: (x == 'cancelled').sum()),
    mobile_ratio    = ('device_type', lambda x: (x == 'mobile').mean()),
).reset_index().rename(columns={'order_date': 'Date'})

# Tỷ lệ hủy đơn → nếu cao → Revenue thực sẽ thấp hơn dự kiến
daily_orders['cancel_rate'] = daily_orders['cancelled_count'] / daily_orders['order_count']

sales = sales.merge(daily_orders, on='Date', how='left')
```

**Ý nghĩa:** Số đơn hàng là **leading indicator** cho Revenue — nhiều đơn → Revenue cao. Nhưng lưu ý:
- `orders.csv` chỉ có đến 2022 → dùng lag để tạo feature cho 2023–2024
- Dùng `lag_365` của order_count: "năm ngoái cùng ngày bao nhiêu đơn?"

---

#### D2. Từ `web_traffic.csv` — Lưu lượng website

```python
web = pd.read_csv("web_traffic.csv", parse_dates=['date'])

# Tổng traffic mỗi ngày (gộp tất cả nguồn)
daily_web = web.groupby('date').agg(
    total_sessions   = ('sessions', 'sum'),
    total_visitors   = ('unique_visitors', 'sum'),
    avg_bounce       = ('bounce_rate', 'mean'),
    avg_duration     = ('avg_session_duration_sec', 'mean'),
).reset_index().rename(columns={'date': 'Date'})

sales = sales.merge(daily_web, on='Date', how='left')

# Tạo lag 365 để dùng cho test period
sales['web_sessions_lag365'] = sales['total_sessions'].shift(365)
```

**Ý nghĩa:**
- `total_sessions` tăng → người ta đang quan tâm đến website → doanh thu có thể tăng
- `avg_bounce` thấp → traffic chất lượng cao → conversion rate tốt hơn
- `avg_duration` cao → khách hàng đang nghiêm túc xem hàng → dự báo Revenue cao hơn

⚠️ **web_traffic bắt đầu từ 2013** (không có 2012):
```python
sales = sales.merge(daily_web, on='Date', how='left')
# NaN cho năm 2012 → fillna với median hoặc 0
sales['total_sessions'] = sales['total_sessions'].fillna(sales['total_sessions'].median())
```

---

#### D3. Từ `promotions.csv` — Ngày có chương trình khuyến mãi

```python
promotions = pd.read_csv("promotions.csv", parse_dates=['start_date', 'end_date'])

# Tạo cờ: ngày hôm nay có đang chạy promotion không?
def has_active_promo(date, promos):
    return int(any((promos['start_date'] <= date) & (date <= promos['end_date'])))

sales['has_promo'] = sales['Date'].apply(lambda d: has_active_promo(d, promotions))

# Số lượng promo đang chạy đồng thời
def count_active_promos(date, promos):
    return ((promos['start_date'] <= date) & (date <= promos['end_date'])).sum()

sales['active_promo_count'] = sales['Date'].apply(lambda d: count_active_promos(d, promotions))
```

**Ý nghĩa:**
- Ngày có promotion → Revenue tăng rõ rệt (thường 20–50%)
- Ngày có nhiều promotion đồng thời → tác động còn mạnh hơn
- Model biết "hôm nay có KM" → dự báo cao hơn baseline

---

#### D4. Từ `inventory.csv` — Tình trạng tồn kho

```python
inventory = pd.read_csv("inventory.csv", parse_dates=['snapshot_date'])

# Tổng hợp theo tháng (inventory chỉ có cuối tháng)
monthly_inv = inventory.groupby('snapshot_date').agg(
    avg_fill_rate    = ('fill_rate', 'mean'),
    stockout_pct     = ('stockout_flag', 'mean'),
    avg_stock        = ('stock_on_hand', 'sum'),
).reset_index()

# Merge vào sales theo tháng
sales['month_start'] = sales['Date'].values.astype('datetime64[M]')
monthly_inv['month_start'] = monthly_inv['snapshot_date'].values.astype('datetime64[M]')

sales = sales.merge(monthly_inv[['month_start','avg_fill_rate','stockout_pct']],
                    on='month_start', how='left')
```

**Ý nghĩa:**
- `fill_rate` thấp tháng trước → nhiều đơn bị từ chối do hết hàng → Revenue thực thấp
- `stockout_pct` cao → nhu cầu tốt nhưng không đủ hàng → tháng sau nhập hàng về → Revenue tăng
- Tồn kho tốt (đủ hàng) → không bỏ lỡ đơn → Revenue đạt tiềm năng tối đa

---

#### D5. Ngày lễ Việt Nam (tạo thủ công)

```python
# Các ngày lễ quan trọng ảnh hưởng doanh thu thời trang VN
vn_important_dates = {
    # Doanh thu CAO (mua sắm nhiều)
    'tet_eve':      [(month == 1) & (day >= 20) & (day <= 31) for mỗi năm],
    'black_friday': [(month == 11) & (day >= 25) & (day <= 30)],
    '12_12':        [(month == 12) & (day == 12)],
    '11_11':        [(month == 11) & (day == 11)],
    '8_8':          [(month == 8) & (day == 8)],
    # Ngày nghỉ lễ (có thể thấp hơn)
    'april_30':     [(month == 4) & (day == 30)],
    'may_1':        [(month == 5) & (day == 1)],
}

# Cách đơn giản:
df['is_nov']   = (df['Date'].dt.month == 11).astype(int)  # Black Friday month
df['is_dec']   = (df['Date'].dt.month == 12).astype(int)  # Christmas/Year-end
df['is_jan']   = (df['Date'].dt.month == 1).astype(int)   # Tết
df['day']      = df['Date'].dt.day
df['is_sale_event'] = (
    ((df['Date'].dt.month == 11) & (df['Date'].dt.day >= 25)) |  # Black Friday
    ((df['Date'].dt.month == 12) & (df['Date'].dt.day == 12)) |  # 12.12
    ((df['Date'].dt.month == 11) & (df['Date'].dt.day == 11))    # 11.11
).astype(int)
```

---

## 4. Quy trình tạo features hoàn chỉnh

```python
import pandas as pd
import numpy as np

# ── Load data ─────────────────────────────────────────────────
sales    = pd.read_csv("sales.csv", parse_dates=["Date"])
orders   = pd.read_csv("orders.csv", parse_dates=["order_date"])
web      = pd.read_csv("web_traffic.csv", parse_dates=["date"])
promos   = pd.read_csv("promotions.csv", parse_dates=["start_date","end_date"])
inv      = pd.read_csv("inventory.csv", parse_dates=["snapshot_date"])
sub      = pd.read_csv("sample_submission.csv", parse_dates=["Date"])

# ── Tạo dataframe đầy đủ (train + test dates) ─────────────────
test_df = pd.DataFrame({'Date': sub['Date'], 'Revenue': np.nan, 'COGS': np.nan})
full = pd.concat([sales, test_df], ignore_index=True).sort_values('Date').reset_index(drop=True)

# ── Time features ──────────────────────────────────────────────
full['dayofweek']  = full['Date'].dt.dayofweek
full['month']      = full['Date'].dt.month
full['quarter']    = full['Date'].dt.quarter
full['year']       = full['Date'].dt.year
full['dayofyear']  = full['Date'].dt.dayofyear
full['is_weekend'] = (full['Date'].dt.dayofweek >= 5).astype(int)
full['is_nov']     = (full['Date'].dt.month == 11).astype(int)
full['is_dec']     = (full['Date'].dt.month == 12).astype(int)
full['is_jan']     = (full['Date'].dt.month == 1).astype(int)
full['is_sale_event'] = (
    ((full['Date'].dt.month == 11) & (full['Date'].dt.day >= 25)) |
    ((full['Date'].dt.month == 12) & (full['Date'].dt.day == 12)) |
    ((full['Date'].dt.month == 11) & (full['Date'].dt.day == 11))
).astype(int)

# ── Lag features (dùng lag >= 365 để an toàn cho test set) ────
for lag in [7, 14, 30, 60, 90, 180, 365, 366, 730]:
    full[f'rev_lag_{lag}'] = full['Revenue'].shift(lag)
    full[f'cogs_lag_{lag}'] = full['COGS'].shift(lag)

# ── Rolling features (shift trước để tránh leakage) ───────────
for w in [7, 14, 30, 90]:
    full[f'rev_roll_mean_{w}'] = full['Revenue'].shift(365).rolling(w).mean()
    full[f'rev_roll_std_{w}']  = full['Revenue'].shift(365).rolling(w).std()

# YoY growth rate
full['yoy_ratio'] = full['Revenue'] / (full['Revenue'].shift(365) + 1e-8)
full['rev_yoy_mean_30'] = full['yoy_ratio'].shift(365).rolling(30).mean()

# ── External: orders ───────────────────────────────────────────
daily_ord = orders.groupby('order_date').agg(
    order_count   = ('order_id','count'),
    cancel_rate   = ('order_status', lambda x: (x=='cancelled').mean()),
).reset_index().rename(columns={'order_date':'Date'})
full = full.merge(daily_ord, on='Date', how='left')
full['order_count_lag365'] = full['order_count'].shift(365)

# ── External: web traffic ──────────────────────────────────────
daily_web = web.groupby('date').agg(
    sessions = ('sessions','sum'),
    bounce   = ('bounce_rate','mean'),
).reset_index().rename(columns={'date':'Date'})
full = full.merge(daily_web, on='Date', how='left')
full['sessions_lag365'] = full['sessions'].shift(365)
full['sessions'] = full['sessions'].fillna(full['sessions'].median())

# ── External: promotions ───────────────────────────────────────
full['active_promo_count'] = full['Date'].apply(
    lambda d: int(((promos['start_date'] <= d) & (d <= promos['end_date'])).sum())
)

# ── External: inventory (monthly) ─────────────────────────────
monthly_inv = inv.groupby(inv['snapshot_date'].dt.to_period('M')).agg(
    fill_rate    = ('fill_rate','mean'),
    stockout_pct = ('stockout_flag','mean'),
).reset_index()
monthly_inv['month_period'] = monthly_inv['snapshot_date']
full['month_period'] = full['Date'].dt.to_period('M')
full = full.merge(monthly_inv[['month_period','fill_rate','stockout_pct']],
                  on='month_period', how='left')

# ── Tách train / test ──────────────────────────────────────────
FEATURE_COLS = [c for c in full.columns
                if c not in ['Date','Revenue','COGS','month_period']]

train = full[full['Date'] <= '2022-12-31'].dropna(subset=['Revenue'])
test  = full[full['Date'] >= '2023-01-01']

X_train = train[FEATURE_COLS]
y_train = train['Revenue']
X_test  = test[FEATURE_COLS].fillna(0)

print(f"Train: {len(X_train)} rows, {len(FEATURE_COLS)} features")
print(f"Test:  {len(X_test)} rows")
print(f"Features: {FEATURE_COLS}")
```

---

## 5. Tổng hợp — Feature nào quan trọng nhất?

| Nhóm | Feature quan trọng nhất | Lý do |
|------|------------------------|-------|
| Time | `month`, `dayofweek` | Mùa vụ và pattern tuần |
| Lag | `rev_lag_365` | Pattern năm ngoái = dự báo tốt nhất |
| Rolling | `rev_roll_mean_30` (lag365) | Xu hướng trung bình tháng năm ngoái |
| External | `active_promo_count` | Ngày có KM → doanh thu tăng rõ rệt |
| External | `sessions_lag365` | Traffic năm ngoái → proxy cho nhu cầu |
| Custom | `is_sale_event` | 11.11, Black Friday, 12.12 |

> **Quy tắc vàng:** Feature nào giúp model biết được **"hôm nay đặc biệt thế nào so với ngày bình thường"** đều có giá trị.
