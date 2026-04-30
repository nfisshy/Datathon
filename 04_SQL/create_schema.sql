-- ============================================================
-- DDL — DATATHON 2026: THE GRIDBREAKERS
-- Tạo toàn bộ schema cho bộ dữ liệu thời trang TMĐT Việt Nam
-- ============================================================

-- ============================================================
-- LỚP 1: MASTER — Dữ liệu tham chiếu
-- ============================================================

CREATE TABLE geography (
    zip      INTEGER      NOT NULL,
    city     VARCHAR(100) NOT NULL,
    region   VARCHAR(20)  NOT NULL CHECK (region IN ('East', 'Central', 'West')),
    district VARCHAR(100) NOT NULL,

    CONSTRAINT pk_geography PRIMARY KEY (zip)
);

-- -------------------------------------------------------

CREATE TABLE products (
    product_id   INTEGER       NOT NULL,
    product_name VARCHAR(200)  NOT NULL,
    category     VARCHAR(50)   NOT NULL CHECK (category IN ('Streetwear','Outdoor','Casual','GenZ')),
    segment      VARCHAR(50)   NOT NULL CHECK (segment IN ('Premium','Standard','Activewear',
                                               'Performance','All-weather','Balanced','Trendy','Everyday')),
    size         CHAR(2)       NOT NULL CHECK (size IN ('S','M','L','XL')),
    color        VARCHAR(20)   NOT NULL,
    price        DECIMAL(10,2) NOT NULL CHECK (price > 0),
    cogs         DECIMAL(10,2) NOT NULL CHECK (cogs > 0),

    CONSTRAINT pk_products    PRIMARY KEY (product_id),
    CONSTRAINT chk_margin     CHECK (cogs < price)   -- cogs luôn < price
);

-- -------------------------------------------------------

CREATE TABLE promotions (
    promo_id             VARCHAR(20)   NOT NULL,
    promo_name           VARCHAR(100)  NOT NULL,
    promo_type           VARCHAR(20)   NOT NULL CHECK (promo_type IN ('percentage','fixed')),
    discount_value       DECIMAL(10,2) NOT NULL CHECK (discount_value > 0),
    start_date           DATE          NOT NULL,
    end_date             DATE          NOT NULL,
    applicable_category  VARCHAR(50)   NULL,     -- NULL = áp dụng tất cả danh mục
    promo_channel        VARCHAR(30)   NULL CHECK (promo_channel IN
                             ('all_channels','email','in_store','online','social_media')),
    stackable_flag       SMALLINT      NOT NULL DEFAULT 0 CHECK (stackable_flag IN (0,1)),
    min_order_value      DECIMAL(10,2) NULL,     -- NULL = không yêu cầu giá trị tối thiểu

    CONSTRAINT pk_promotions  PRIMARY KEY (promo_id),
    CONSTRAINT chk_promo_date CHECK (end_date >= start_date)
);

-- -------------------------------------------------------

CREATE TABLE customers (
    customer_id          INTEGER      NOT NULL,
    zip                  INTEGER      NOT NULL,
    city                 VARCHAR(100) NOT NULL,
    signup_date          DATE         NOT NULL,
    gender               VARCHAR(20)  NULL CHECK (gender IN ('Female','Male','Non-binary')),
    age_group            VARCHAR(10)  NULL CHECK (age_group IN ('18-24','25-34','35-44','45-54','55+')),
    acquisition_channel  VARCHAR(30)  NULL CHECK (acquisition_channel IN
                             ('organic_search','social_media','paid_search',
                              'email_campaign','referral','direct')),

    CONSTRAINT pk_customers  PRIMARY KEY (customer_id),
    CONSTRAINT fk_cust_geo   FOREIGN KEY (zip) REFERENCES geography(zip)
);

-- ============================================================
-- LỚP 2: TRANSACTION — Dữ liệu giao dịch
-- ============================================================

CREATE TABLE orders (
    order_id        INTEGER     NOT NULL,
    order_date      DATE        NOT NULL,
    customer_id     INTEGER     NOT NULL,
    zip             INTEGER     NOT NULL,    -- địa chỉ giao hàng (≠ customers.zip)
    order_status    VARCHAR(20) NOT NULL CHECK (order_status IN
                        ('created','paid','shipped','delivered','cancelled','returned')),
    payment_method  VARCHAR(20) NOT NULL CHECK (payment_method IN
                        ('credit_card','paypal','cod','apple_pay','bank_transfer')),
    device_type     VARCHAR(10) NOT NULL CHECK (device_type IN ('mobile','desktop','tablet')),
    order_source    VARCHAR(30) NOT NULL CHECK (order_source IN
                        ('direct','email_campaign','organic_search',
                         'paid_search','referral','social_media')),

    CONSTRAINT pk_orders      PRIMARY KEY (order_id),
    CONSTRAINT fk_ord_cust    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_ord_geo     FOREIGN KEY (zip)         REFERENCES geography(zip)
);

-- -------------------------------------------------------

CREATE TABLE order_items (
    order_id        INTEGER       NOT NULL,
    product_id      INTEGER       NOT NULL,
    quantity        INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    promo_id        VARCHAR(20)   NULL,     -- NULL = không có khuyến mãi
    promo_id_2      VARCHAR(20)   NULL,     -- NULL = không có KM thứ 2 (stackable)

    CONSTRAINT pk_order_items   PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_oi_order      FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_oi_product    FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_oi_promo      FOREIGN KEY (promo_id)   REFERENCES promotions(promo_id),
    CONSTRAINT fk_oi_promo2     FOREIGN KEY (promo_id_2) REFERENCES promotions(promo_id)
);

-- -------------------------------------------------------

CREATE TABLE payments (
    order_id        INTEGER       NOT NULL,
    payment_method  VARCHAR(20)   NOT NULL CHECK (payment_method IN
                        ('credit_card','paypal','cod','apple_pay','bank_transfer')),
    payment_value   DECIMAL(12,2) NOT NULL CHECK (payment_value > 0),
    installments    SMALLINT      NOT NULL CHECK (installments IN (1,2,3,6,12)),

    CONSTRAINT pk_payments   PRIMARY KEY (order_id),  -- 1:1 với orders
    CONSTRAINT fk_pay_order  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- -------------------------------------------------------

CREATE TABLE shipments (
    order_id      INTEGER       NOT NULL,
    ship_date     DATE          NOT NULL,
    delivery_date DATE          NOT NULL,
    shipping_fee  DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (shipping_fee >= 0),

    CONSTRAINT pk_shipments    PRIMARY KEY (order_id),
    CONSTRAINT fk_ship_order   FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT chk_ship_dates  CHECK (delivery_date >= ship_date)
    -- Chỉ tồn tại cho đơn có status IN ('shipped','delivered','returned')
);

-- -------------------------------------------------------

CREATE TABLE returns (
    return_id       VARCHAR(30)   NOT NULL,
    order_id        INTEGER       NOT NULL,
    product_id      INTEGER       NOT NULL,
    return_date     DATE          NOT NULL,
    return_reason   VARCHAR(30)   NOT NULL CHECK (return_reason IN
                        ('wrong_size','defective','changed_mind',
                         'not_as_described','late_delivery')),
    return_quantity INTEGER       NOT NULL CHECK (return_quantity > 0),
    refund_amount   DECIMAL(10,2) NOT NULL CHECK (refund_amount >= 0),

    CONSTRAINT pk_returns      PRIMARY KEY (return_id),
    CONSTRAINT fk_ret_order    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_ret_product  FOREIGN KEY (product_id) REFERENCES products(product_id)
    -- order_id phải có order_status = 'returned'
);

-- -------------------------------------------------------

CREATE TABLE reviews (
    review_id    VARCHAR(30)  NOT NULL,
    order_id     INTEGER      NOT NULL,
    product_id   INTEGER      NOT NULL,
    customer_id  INTEGER      NOT NULL,
    review_date  DATE         NOT NULL,
    rating       SMALLINT     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_title VARCHAR(100) NOT NULL,

    CONSTRAINT pk_reviews       PRIMARY KEY (review_id),
    CONSTRAINT fk_rev_order     FOREIGN KEY (order_id)    REFERENCES orders(order_id),
    CONSTRAINT fk_rev_product   FOREIGN KEY (product_id)  REFERENCES products(product_id),
    CONSTRAINT fk_rev_customer  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    -- Chỉ tồn tại cho đơn có order_status = 'delivered' (~17.5%)
);

-- ============================================================
-- LỚP 3: ANALYTICAL — Dữ liệu phân tích
-- ============================================================

CREATE TABLE sales (
    sale_date  DATE          NOT NULL,
    revenue    DECIMAL(14,2) NOT NULL CHECK (revenue > 0),
    cogs       DECIMAL(14,2) NOT NULL CHECK (cogs > 0),

    CONSTRAINT pk_sales     PRIMARY KEY (sale_date),
    CONSTRAINT chk_sal_gp   CHECK (revenue > cogs)
    -- Tổng hợp doanh thu toàn bộ giao dịch trong ngày
    -- Train: 2012-07-04 → 2022-12-31
    -- Test (cần dự báo): 2023-01-01 → 2024-07-01
);

-- -------------------------------------------------------

CREATE TABLE sample_submission (
    sale_date  DATE          NOT NULL,
    revenue    DECIMAL(14,2) NULL,   -- NULL = cần dự báo
    cogs       DECIMAL(14,2) NULL,   -- NULL = cần dự báo

    CONSTRAINT pk_submission PRIMARY KEY (sale_date)
    -- 549 ngày: 2023-01-01 → 2024-07-01
);

-- ============================================================
-- LỚP 4: OPERATIONAL — Dữ liệu vận hành
-- ============================================================

CREATE TABLE inventory (
    snapshot_date     DATE          NOT NULL,   -- ngày cuối tháng
    product_id        INTEGER       NOT NULL,
    stock_on_hand     INTEGER       NOT NULL CHECK (stock_on_hand >= 0),
    units_received    INTEGER       NOT NULL CHECK (units_received >= 0),
    units_sold        INTEGER       NOT NULL CHECK (units_sold >= 0),
    stockout_days     INTEGER       NOT NULL CHECK (stockout_days >= 0),
    days_of_supply    DECIMAL(8,2)  NOT NULL CHECK (days_of_supply >= 0),
    fill_rate         DECIMAL(5,4)  NOT NULL CHECK (fill_rate BETWEEN 0 AND 1),
    stockout_flag     SMALLINT      NOT NULL CHECK (stockout_flag IN (0,1)),
    overstock_flag    SMALLINT      NOT NULL CHECK (overstock_flag IN (0,1)),
    reorder_flag      SMALLINT      NOT NULL CHECK (reorder_flag IN (0,1)),
    sell_through_rate DECIMAL(5,4)  NOT NULL CHECK (sell_through_rate BETWEEN 0 AND 1),
    -- Denormalized từ products (để tiện truy vấn không cần JOIN):
    product_name      VARCHAR(200)  NOT NULL,
    category          VARCHAR(50)   NOT NULL,
    segment           VARCHAR(50)   NOT NULL,
    year              SMALLINT      NOT NULL,
    month             SMALLINT      NOT NULL CHECK (month BETWEEN 1 AND 12),

    CONSTRAINT pk_inventory    PRIMARY KEY (snapshot_date, product_id),
    CONSTRAINT fk_inv_product  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- -------------------------------------------------------

CREATE TABLE web_traffic (
    traffic_date              DATE         NOT NULL,
    sessions                  INTEGER      NOT NULL CHECK (sessions > 0),
    unique_visitors           INTEGER      NOT NULL CHECK (unique_visitors > 0),
    page_views                INTEGER      NOT NULL CHECK (page_views > 0),
    bounce_rate               DECIMAL(6,4) NOT NULL CHECK (bounce_rate BETWEEN 0 AND 1),
    avg_session_duration_sec  DECIMAL(8,2) NOT NULL CHECK (avg_session_duration_sec > 0),
    traffic_source            VARCHAR(30)  NOT NULL CHECK (traffic_source IN
                                  ('organic_search','paid_search','social_media',
                                   'email_campaign','referral','direct')),

    CONSTRAINT pk_web_traffic PRIMARY KEY (traffic_date, traffic_source)
    -- 1 ngày có 6 dòng (1 per traffic_source)
    -- Bắt đầu từ 2013-01-01 (không có năm 2012)
);

-- ============================================================
-- INDEX — Tối ưu truy vấn thường gặp
-- ============================================================

-- Tra cứu đơn hàng theo khách hàng
CREATE INDEX idx_orders_customer    ON orders(customer_id);
CREATE INDEX idx_orders_date        ON orders(order_date);
CREATE INDEX idx_orders_status      ON orders(order_status);
CREATE INDEX idx_orders_zip         ON orders(zip);

-- Tra cứu chi tiết đơn hàng
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Tra cứu trả hàng / đánh giá theo sản phẩm
CREATE INDEX idx_returns_product    ON returns(product_id);
CREATE INDEX idx_reviews_product    ON reviews(product_id);
CREATE INDEX idx_reviews_customer   ON reviews(customer_id);

-- Tra cứu tồn kho theo tháng
CREATE INDEX idx_inventory_date     ON inventory(snapshot_date);
CREATE INDEX idx_inventory_product  ON inventory(product_id);

-- Tra cứu web traffic theo ngày
CREATE INDEX idx_web_date           ON web_traffic(traffic_date);

-- ============================================================
-- LOAD DATA từ CSV (PostgreSQL syntax — dùng \copy hoặc COPY)
-- ============================================================

/*
\copy geography        FROM 'geography.csv'        CSV HEADER;
\copy products         FROM 'products.csv'          CSV HEADER;
\copy promotions       FROM 'promotions.csv'        CSV HEADER;
\copy customers        FROM 'customers.csv'         CSV HEADER;
\copy orders           FROM 'orders.csv'            CSV HEADER;
\copy order_items      FROM 'order_items.csv'       CSV HEADER;
\copy payments         FROM 'payments.csv'          CSV HEADER;
\copy shipments        FROM 'shipments.csv'         CSV HEADER;
\copy returns          FROM 'returns.csv'           CSV HEADER;
\copy reviews          FROM 'reviews.csv'           CSV HEADER;
\copy sales            FROM 'sales.csv'             CSV HEADER;
\copy inventory        FROM 'inventory.csv'         CSV HEADER;
\copy web_traffic      FROM 'web_traffic.csv'       CSV HEADER;
\copy sample_submission FROM 'sample_submission.csv' CSV HEADER;
*/

-- ============================================================
-- LOAD DATA bằng Python (nếu dùng SQLite hoặc pandas)
-- ============================================================

/*
import pandas as pd
import sqlite3

conn = sqlite3.connect("datathon2026.db")

tables = [
    ("geography",         "geography.csv"),
    ("products",          "products.csv"),
    ("promotions",        "promotions.csv"),
    ("customers",         "customers.csv"),
    ("orders",            "orders.csv"),
    ("order_items",       "order_items.csv"),
    ("payments",          "payments.csv"),
    ("shipments",         "shipments.csv"),
    ("returns",           "returns.csv"),
    ("reviews",           "reviews.csv"),
    ("sales",             "sales.csv"),
    ("inventory",         "inventory.csv"),
    ("web_traffic",       "web_traffic.csv"),
    ("sample_submission", "sample_submission.csv"),
]

for table_name, file_name in tables:
    df = pd.read_csv(file_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✅ Loaded {len(df):,} rows → {table_name}")

conn.close()
*/
