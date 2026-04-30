# 🤖 PHẦN 3 — MÔ HÌNH DỰ BÁO DOANH THU (SALES FORECASTING)

> **Điểm:** 20/100 | **Metric:** MAE ↓, RMSE ↓, R² ↑  
> **Kaggle:** https://www.kaggle.com/competitions/datathon-2026-round-1  
> **Train:** 04/07/2012 – 31/12/2022 | **Test:** 01/01/2023 – 01/07/2024

---

## ⚠️ Điều Kiện Loại Bài (Đọc Kỹ Trước!)

| Vi phạm | Hậu quả |
|---------|---------|
| Dùng `Revenue`/`COGS` từ tập test làm feature | **Loại toàn bộ Phần 3** |
| Dùng dữ liệu ngoài bộ được cung cấp | **Loại toàn bộ Phần 3** |
| Không đính kèm code hoặc không reproducible | **Loại toàn bộ Phần 3** |

---

## 📊 Hiểu Dữ Liệu Target

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sales = pd.read_csv("sales.csv", parse_dates=["Date"])
sample_sub = pd.read_csv("sample_submission.csv", parse_dates=["Date"])

print(sales.head())
print(f"Train: {sales['Date'].min()} → {sales['Date'].max()}")
print(f"Test rows: {len(sample_sub)}")
print(f"Revenue stats:\n{sales['Revenue'].describe()}")

# Kiểm tra missing dates
date_range = pd.date_range(sales['Date'].min(), sales['Date'].max())
missing = date_range.difference(sales['Date'])
print(f"Missing dates: {len(missing)}")
```

**Cấu trúc file nộp:**
```
Date,Revenue,COGS
2023-01-01,26607.2,2585.15
2023-01-02,1007.89,163.0
...
```

---

## 🛠️ Pipeline Đề Xuất (Từng Bước)

### Bước 1: Feature Engineering từ `sales.csv`

```python
def create_time_features(df):
    df = df.copy()
    df['dayofweek']  = df['Date'].dt.dayofweek       # 0=Mon ... 6=Sun
    df['dayofmonth'] = df['Date'].dt.day
    df['dayofyear']  = df['Date'].dt.dayofyear
    df['weekofyear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['month']      = df['Date'].dt.month
    df['quarter']    = df['Date'].dt.quarter
    df['year']       = df['Date'].dt.year
    df['is_weekend'] = (df['Date'].dt.dayofweek >= 5).astype(int)
    # Ngày lễ Việt Nam
    vn_holidays = ['01-01','04-30','05-01','09-02','12-25']
    df['is_holiday'] = df['Date'].dt.strftime('%m-%d').isin(vn_holidays).astype(int)
    return df

sales = create_time_features(sales)
```

### Bước 2: Lag Features & Rolling Statistics

```python
def create_lag_features(df, target='Revenue'):
    df = df.sort_values('Date').copy()
    # Lag features
    for lag in [1, 7, 14, 28, 30, 90, 365]:
        df[f'lag_{lag}'] = df[target].shift(lag)
    # Rolling statistics
    for window in [7, 14, 30, 90]:
        df[f'rolling_mean_{window}'] = df[target].shift(1).rolling(window).mean()
        df[f'rolling_std_{window}']  = df[target].shift(1).rolling(window).std()
        df[f'rolling_max_{window}']  = df[target].shift(1).rolling(window).max()
        df[f'rolling_min_{window}']  = df[target].shift(1).rolling(window).min()
    # Year-over-year growth
    df['lag_365_yoy'] = df[target] / df[target].shift(365) - 1
    return df

sales = create_lag_features(sales)
```

### Bước 3: External Features (từ các bảng khác)

```python
orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
web    = pd.read_csv("web_traffic.csv", parse_dates=["date"])

# Đơn hàng theo ngày (leading indicator)
daily_orders = orders.groupby('order_date').agg(
    order_count=('order_id','count'),
    cancelled_rate=('order_status', lambda x: (x=='cancelled').mean())
).reset_index().rename(columns={'order_date':'Date'})

# Web traffic theo ngày
daily_web = web.groupby('date').agg(
    total_sessions=('sessions','sum'),
    avg_bounce=('bounce_rate','mean')
).reset_index().rename(columns={'date':'Date'})

# Merge vào sales
sales = sales.merge(daily_orders, on='Date', how='left')
sales = sales.merge(daily_web, on='Date', how='left')
```

### Bước 4: Thêm COGS Lag Features (COGS là target phụ)

```python
# COGS cũng cần dự báo, dùng chung feature set
sales = create_lag_features(sales, target='COGS')
```

### Bước 5: Phân chia Train/Validation đúng chiều thời gian

```python
# ⚠️ KHÔNG dùng random split — phải dùng time-based split
CUTOFF_DATE = pd.Timestamp('2022-07-01')

train_df = sales[sales['Date'] < CUTOFF_DATE].dropna()
val_df   = sales[(sales['Date'] >= CUTOFF_DATE)].dropna()

feature_cols = [c for c in train_df.columns 
                if c not in ['Date','Revenue','COGS']]

X_train, y_train_rev  = train_df[feature_cols], train_df['Revenue']
X_val,   y_val_rev    = val_df[feature_cols],   val_df['Revenue']
```

---

## 🧠 Các Mô Hình Gợi Ý

### Mô hình 1: LightGBM (Baseline mạnh nhất)

```python
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

SEED = 42

lgb_params = {
    'objective': 'regression',
    'metric': 'mae',
    'n_estimators': 2000,
    'learning_rate': 0.03,
    'num_leaves': 63,
    'min_child_samples': 20,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'random_state': SEED,
    'verbose': -1,
}

model_rev = lgb.LGBMRegressor(**lgb_params)
model_rev.fit(
    X_train, y_train_rev,
    eval_set=[(X_val, y_val_rev)],
    callbacks=[lgb.early_stopping(100), lgb.log_evaluation(200)]
)

pred_val = model_rev.predict(X_val)
print(f"MAE : {mean_absolute_error(y_val_rev, pred_val):,.2f}")
print(f"RMSE: {mean_squared_error(y_val_rev, pred_val, squared=False):,.2f}")
print(f"R²  : {r2_score(y_val_rev, pred_val):.4f}")
```

### Mô hình 2: Prophet (tốt cho seasonality)

```python
from prophet import Prophet

prophet_df = sales[['Date','Revenue']].rename(columns={'Date':'ds','Revenue':'y'})
train_prophet = prophet_df[prophet_df['ds'] < CUTOFF_DATE]

m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.05
)
# Thêm holidays Việt Nam
m.add_country_holidays(country_name='VN')
m.fit(train_prophet)

# Predict
future = m.make_future_dataframe(periods=len(val_df))
forecast = m.predict(future)
```

### Mô hình 3: XGBoost (Ensemble với LightGBM)

```python
from xgboost import XGBRegressor

xgb_model = XGBRegressor(
    n_estimators=1500,
    learning_rate=0.03,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=0.1,
    random_state=SEED,
    early_stopping_rounds=100,
    eval_metric='mae'
)
xgb_model.fit(X_train, y_train_rev, eval_set=[(X_val, y_val_rev)], verbose=200)
```

### Ensemble (Trung bình có trọng số)

```python
# Blend dựa theo validation performance
w_lgb = 0.5
w_xgb = 0.3
w_prophet = 0.2

pred_ensemble = (
    w_lgb * lgb_pred +
    w_xgb * xgb_pred +
    w_prophet * prophet_pred
)
```

---

## 📅 Time-Series Cross-Validation (Bắt buộc trong báo cáo)

```python
from sklearn.model_selection import TimeSeriesSplit

# Walk-forward validation với 5 folds
tscv = TimeSeriesSplit(n_splits=5, gap=30)  # gap=30 ngày để tránh leakage

cv_scores = []
for fold, (train_idx, val_idx) in enumerate(tscv.split(train_df)):
    X_tr = train_df.iloc[train_idx][feature_cols]
    y_tr = train_df.iloc[train_idx]['Revenue']
    X_vl = train_df.iloc[val_idx][feature_cols]
    y_vl = train_df.iloc[val_idx]['Revenue']
    
    m = lgb.LGBMRegressor(**lgb_params, n_estimators=500)
    m.fit(X_tr, y_tr)
    pred = m.predict(X_vl)
    
    mae = mean_absolute_error(y_vl, pred)
    cv_scores.append(mae)
    print(f"Fold {fold+1}: MAE = {mae:,.2f}")

print(f"\nCV MAE: {np.mean(cv_scores):,.2f} ± {np.std(cv_scores):,.2f}")
```

---

## 🔍 Model Explainability (8 điểm báo cáo kỹ thuật)

### SHAP Values

```python
import shap

explainer = shap.TreeExplainer(model_rev)
shap_values = explainer.shap_values(X_val)

# Summary plot - feature importance
shap.summary_plot(shap_values, X_val, plot_type="bar", 
                  max_display=20, show=False)
plt.title("SHAP Feature Importance — Revenue Forecasting")
plt.tight_layout()
plt.savefig("shap_importance.png", dpi=150, bbox_inches='tight')

# Dependence plot cho feature quan trọng nhất
top_feature = X_val.columns[np.abs(shap_values).mean(0).argmax()]
shap.dependence_plot(top_feature, shap_values, X_val, show=False)
plt.savefig("shap_dependence.png", dpi=150, bbox_inches='tight')
```

### Feature Importance từ LightGBM

```python
import lightgbm as lgb

fig, ax = plt.subplots(figsize=(10, 8))
lgb.plot_importance(model_rev, ax=ax, max_num_features=20,
                    importance_type='gain', title='Feature Importance (Gain)')
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150, bbox_inches='tight')
```

---

## 📤 Tạo File Submission

```python
# Load sample submission để lấy đúng thứ tự date
sample_sub = pd.read_csv("sample_submission.csv", parse_dates=["Date"])

# Chuẩn bị test features
test_df = create_time_features(sample_sub.copy())
# NOTE: Với lag features, cần nối train + test để tính lag
full_df = pd.concat([sales[['Date','Revenue','COGS']], sample_sub[['Date']]], ignore_index=True)
full_df = create_time_features(full_df)
full_df = create_lag_features(full_df)

test_features = full_df[full_df['Date'].isin(sample_sub['Date'])][feature_cols]

# Predict Revenue và COGS
pred_revenue = model_rev.predict(test_features)
pred_cogs    = model_cogs.predict(test_features)

# Đảm bảo COGS < Revenue (constraint kinh doanh)
pred_cogs = np.minimum(pred_cogs, pred_revenue * 0.95)

# Tạo submission
submission = sample_sub.copy()
submission['Revenue'] = pred_revenue
submission['COGS']    = pred_cogs

# ⚠️ Giữ nguyên thứ tự, không sort lại
submission.to_csv("submission.csv", index=False)
print(submission.head())
print(f"Submission rows: {len(submission)}")
```

---

## 📑 Cấu Trúc Báo Cáo Kỹ Thuật (8 điểm)

Dùng **NeurIPS LaTeX template** (tối đa 4 trang):

```
Section 1: Introduction (0.25 trang)
  - Mô tả bài toán, bối cảnh kinh doanh
  - Challenges: non-stationarity, seasonality, outliers

Section 2: Data & Feature Engineering (0.75 trang)
  - Mô tả features đã tạo (time, lag, rolling, external)
  - Xử lý missing values, outliers
  - Data leakage prevention strategy

Section 3: Methodology (1 trang)
  - Kiến trúc pipeline
  - Các mô hình đã thử và lý do chọn
  - Time-series CV với walk-forward validation
  - Hyperparameter tuning strategy

Section 4: Results & Model Explanation (1.5 trang)
  - Bảng metrics: MAE, RMSE, R² (CV + leaderboard)
  - SHAP summary plot
  - Top-5 features với giải thích kinh doanh
  - Residual analysis plot

Section 5: Conclusion (0.5 trang)
  - Kết luận, limitations, hướng cải thiện
```

---

## 📋 Checklist Trước Khi Nộp

### Code & Reproducibility
- [ ] Đặt `random_state=SEED` ở tất cả mô hình
- [ ] Tất cả package có version cố định (`requirements.txt` hoặc `pip freeze`)
- [ ] GitHub repo có `README.md` với hướng dẫn chạy lại
- [ ] Notebook chạy từ đầu đến cuối không lỗi

### Tránh Data Leakage
- [ ] **KHÔNG** dùng `Revenue`/`COGS` từ tập test
- [ ] Lag features được tính từ train set, sau đó mở rộng sang test
- [ ] Cross-validation dùng `TimeSeriesSplit` (không phải KFold ngẫu nhiên)
- [ ] `validation_cutoff` nằm trong khoảng train, không dùng test để tune

### Submission
- [ ] `submission.csv` có đúng số dòng như `sample_submission.csv`
- [ ] Giữ nguyên thứ tự ngày, không sort lại
- [ ] Cột: `Date`, `Revenue`, `COGS` (đúng tên, đúng kiểu)
- [ ] Revenue > 0 cho tất cả dòng
- [ ] COGS < Revenue cho tất cả dòng

---

## 🏆 Chiến Lược Tối Ưu Điểm

```
Mức điểm 10–12đ (top leaderboard):
├── Ensemble LightGBM + XGBoost + Prophet
├── Feature engineering phong phú (50+ features)
├── Hyperparameter tuning với Optuna/BayesOpt
└── SHAP analysis đầy đủ trong báo cáo

Mức điểm 5–9đ (trung bình):
├── LightGBM hoặc XGBoost đơn lẻ
├── Features cơ bản (lag 7, 30, 365 + time features)
└── CV đơn giản

Mức điểm sàn 3–4đ (baseline):
├── Linear regression hoặc simple model
└── Submission hợp lệ về định dạng
```

> **Tip quan trọng:** Nộp baseline sớm lên Kaggle để thấy điểm số, sau đó cải thiện dần. Submission hợp lệ = ít nhất 3–4 điểm đảm bảo.
