"""
ERD Generator for DATATHON 2026 Dataset
Sinh biểu đồ ERD (Entity Relationship Diagram) cho bộ dữ liệu
Chạy: python erd_generator.py
Output: erd_datathon2026.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ── Cấu hình bảng và cột ──────────────────────────────────────────────────────

TABLES = {
    "geography": {
        "pos": (0.5, 8.5),
        "color": "#4A90D9",
        "layer": "MASTER",
        "cols": [
            ("zip", "int", "PK"),
            ("city", "str", ""),
            ("region", "str", ""),
            ("district", "str", ""),
        ],
    },
    "products": {
        "pos": (8.5, 8.5),
        "color": "#4A90D9",
        "layer": "MASTER",
        "cols": [
            ("product_id", "int", "PK"),
            ("product_name", "str", ""),
            ("category", "str", ""),
            ("segment", "str", ""),
            ("size", "str", ""),
            ("color", "str", ""),
            ("price", "float", ""),
            ("cogs", "float", ""),
        ],
    },
    "customers": {
        "pos": (0.5, 4.5),
        "color": "#4A90D9",
        "layer": "MASTER",
        "cols": [
            ("customer_id", "int", "PK"),
            ("zip", "int", "FK"),
            ("city", "str", ""),
            ("signup_date", "date", ""),
            ("gender", "str", ""),
            ("age_group", "str", ""),
            ("acquisition_channel", "str", ""),
        ],
    },
    "promotions": {
        "pos": (8.5, 4.5),
        "color": "#4A90D9",
        "layer": "MASTER",
        "cols": [
            ("promo_id", "str", "PK"),
            ("promo_name", "str", ""),
            ("promo_type", "str", ""),
            ("discount_value", "float", ""),
            ("start_date", "date", ""),
            ("end_date", "date", ""),
            ("applicable_category", "str", ""),
            ("promo_channel", "str", ""),
            ("stackable_flag", "int", ""),
            ("min_order_value", "float", ""),
        ],
    },
    "orders": {
        "pos": (4.0, 6.0),
        "color": "#E67E22",
        "layer": "TRANSACTION",
        "cols": [
            ("order_id", "int", "PK"),
            ("order_date", "date", ""),
            ("customer_id", "int", "FK"),
            ("zip", "int", "FK"),
            ("order_status", "str", ""),
            ("payment_method", "str", ""),
            ("device_type", "str", ""),
            ("order_source", "str", ""),
        ],
    },
    "order_items": {
        "pos": (6.5, 2.5),
        "color": "#E67E22",
        "layer": "TRANSACTION",
        "cols": [
            ("order_id", "int", "FK"),
            ("product_id", "int", "FK"),
            ("quantity", "int", ""),
            ("unit_price", "float", ""),
            ("discount_amount", "float", ""),
            ("promo_id", "str", "FK"),
            ("promo_id_2", "str", "FK"),
        ],
    },
    "payments": {
        "pos": (1.5, 2.0),
        "color": "#E67E22",
        "layer": "TRANSACTION",
        "cols": [
            ("order_id", "int", "FK"),
            ("payment_method", "str", ""),
            ("payment_value", "float", ""),
            ("installments", "int", ""),
        ],
    },
    "shipments": {
        "pos": (4.0, 2.0),
        "color": "#E67E22",
        "layer": "TRANSACTION",
        "cols": [
            ("order_id", "int", "FK"),
            ("ship_date", "date", ""),
            ("delivery_date", "date", ""),
            ("shipping_fee", "float", ""),
        ],
    },
    "returns": {
        "pos": (1.5, 9.5),
        "color": "#E67E22",
        "layer": "TRANSACTION",
        "cols": [
            ("return_id", "str", "PK"),
            ("order_id", "int", "FK"),
            ("product_id", "int", "FK"),
            ("return_date", "date", ""),
            ("return_reason", "str", ""),
            ("return_quantity", "int", ""),
            ("refund_amount", "float", ""),
        ],
    },
    "reviews": {
        "pos": (6.5, 9.5),
        "color": "#E67E22",
        "layer": "TRANSACTION",
        "cols": [
            ("review_id", "str", "PK"),
            ("order_id", "int", "FK"),
            ("product_id", "int", "FK"),
            ("customer_id", "int", "FK"),
            ("review_date", "date", ""),
            ("rating", "int", ""),
            ("review_title", "str", ""),
        ],
    },
    "sales": {
        "pos": (0.0, 0.5),
        "color": "#27AE60",
        "layer": "ANALYTICAL",
        "cols": [
            ("Date", "date", ""),
            ("Revenue", "float", "TARGET"),
            ("COGS", "float", "TARGET"),
        ],
    },
    "inventory": {
        "pos": (8.0, 1.0),
        "color": "#8E44AD",
        "layer": "OPERATIONAL",
        "cols": [
            ("snapshot_date", "date", ""),
            ("product_id", "int", "FK"),
            ("stock_on_hand", "int", ""),
            ("units_received", "int", ""),
            ("units_sold", "int", ""),
            ("stockout_days", "int", ""),
            ("fill_rate", "float", ""),
            ("stockout_flag", "int", ""),
            ("overstock_flag", "int", ""),
        ],
    },
    "web_traffic": {
        "pos": (8.0, 0.0),
        "color": "#8E44AD",
        "layer": "OPERATIONAL",
        "cols": [
            ("date", "date", ""),
            ("sessions", "int", ""),
            ("unique_visitors", "int", ""),
            ("page_views", "int", ""),
            ("bounce_rate", "float", ""),
            ("avg_session_duration_sec", "float", ""),
            ("traffic_source", "str", ""),
        ],
    },
}

# ── Quan hệ (from_table, to_table, label, style) ─────────────────────────────
RELATIONSHIPS = [
    # geography
    ("geography", "customers",   "1:N\n(zip)",        "solid"),
    ("geography", "orders",      "1:N\n(zip)",        "solid"),
    # customers
    ("customers", "orders",      "1:N",               "solid"),
    # orders
    ("orders", "payments",       "1:1",               "solid"),
    ("orders", "shipments",      "1:0..1",            "solid"),
    ("orders", "returns",        "1:0..N",            "solid"),
    ("orders", "reviews",        "1:0..N",            "solid"),
    ("orders", "order_items",    "1:N",               "solid"),
    # order_items
    ("order_items", "products",  "N:1",               "solid"),
    ("order_items", "promotions","N:0..1\n(promo)",   "dashed"),
    # products
    ("products", "inventory",    "1:N\n(monthly)",    "solid"),
    ("products", "returns",      "1:N",               "solid"),
    ("products", "reviews",      "1:N",               "solid"),
    ("customers","reviews",      "1:N",               "dashed"),
]

# ── Hàm vẽ bảng ───────────────────────────────────────────────────────────────
def draw_table(ax, name, config, col_h=0.28, header_h=0.38, pad=0.15, width=2.2):
    x, y = config["pos"]
    cols = config["cols"]
    color = config["color"]
    n = len(cols)
    total_h = header_h + n * col_h + pad

    # Header box
    header = FancyBboxPatch(
        (x, y), width, header_h,
        boxstyle="round,pad=0.02",
        linewidth=1.5, edgecolor="white",
        facecolor=color, zorder=3
    )
    ax.add_patch(header)
    ax.text(x + width / 2, y + header_h / 2, name,
            ha="center", va="center", fontsize=7.5, fontweight="bold",
            color="white", zorder=4)

    # Body box
    body_y = y - n * col_h - pad
    body = FancyBboxPatch(
        (x, body_y), width, n * col_h + pad,
        boxstyle="round,pad=0.02",
        linewidth=1, edgecolor="#CCCCCC",
        facecolor="#F8F9FA", zorder=3
    )
    ax.add_patch(body)

    # Layer badge
    layer_colors = {
        "MASTER": "#4A90D9", "TRANSACTION": "#E67E22",
        "ANALYTICAL": "#27AE60", "OPERATIONAL": "#8E44AD"
    }
    lc = layer_colors.get(config["layer"], "#888")
    ax.text(x + width - 0.05, y + header_h - 0.07,
            config["layer"], ha="right", va="top",
            fontsize=4.5, color="white", alpha=0.85, zorder=5)

    # Columns
    for i, (col_name, dtype, role) in enumerate(cols):
        cy = y - (i + 0.5) * col_h - pad / 2
        # Alternating row
        row_bg = "#EEF2FF" if i % 2 == 0 else "#F8F9FA"
        row = FancyBboxPatch(
            (x + 0.01, cy - col_h / 2 + 0.01), width - 0.02, col_h - 0.02,
            boxstyle="round,pad=0.01",
            linewidth=0, facecolor=row_bg, zorder=3
        )
        ax.add_patch(row)

        # Role badge (PK / FK / TARGET)
        role_color = {"PK": "#E74C3C", "FK": "#3498DB", "TARGET": "#F39C12"}.get(role, None)
        if role_color:
            badge = FancyBboxPatch(
                (x + 0.04, cy - 0.085), 0.28, 0.16,
                boxstyle="round,pad=0.02",
                linewidth=0, facecolor=role_color, zorder=4
            )
            ax.add_patch(badge)
            ax.text(x + 0.18, cy, role,
                    ha="center", va="center", fontsize=4.5,
                    fontweight="bold", color="white", zorder=5)
            ax.text(x + 0.36, cy, col_name,
                    ha="left", va="center", fontsize=5.5,
                    color="#2C3E50", zorder=4)
        else:
            ax.text(x + 0.08, cy, col_name,
                    ha="left", va="center", fontsize=5.5,
                    color="#2C3E50", zorder=4)

        ax.text(x + width - 0.06, cy, dtype,
                ha="right", va="center", fontsize=4.8,
                color="#7F8C8D", style="italic", zorder=4)

    return (x, y, x + width, y + header_h, total_h)


def get_table_center(name):
    cfg = TABLES[name]
    x, y = cfg["pos"]
    w = 2.2
    n_cols = len(cfg["cols"])
    col_h, header_h, pad = 0.28, 0.38, 0.15
    total_h = header_h + n_cols * col_h + pad
    return x + w / 2, y + header_h / 2, x, y, x + w, y - (n_cols * col_h + pad)


def get_edge_points(src, dst):
    sx, sy, slx, sty, srx, sby = get_table_center(src)
    dx, dy, dlx, dty, drx, dby = get_table_center(dst)

    # Choose closest sides
    if srx <= dlx:  # src is left of dst
        return (srx, sy), (dlx, dy)
    elif slx >= drx:  # src is right of dst
        return (slx, sy), (drx, dy)
    elif sty >= dby:  # src is below dst
        return (sx, sty), (dx, dby)
    else:
        return (sx, sby), (dx, dty)


# ── Main plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(20, 14))
ax.set_xlim(-0.5, 11.5)
ax.set_ylim(-0.8, 11.2)
ax.set_aspect("equal")
ax.axis("off")

# Background gradient
ax.add_patch(plt.Rectangle((-0.5, -0.8), 12, 12, color="#1A1A2E", zorder=0))

# Grid lines
for x in np.arange(0, 12, 1):
    ax.axvline(x, color="#ffffff08", linewidth=0.5, zorder=1)
for y in np.arange(0, 12, 1):
    ax.axhline(y, color="#ffffff08", linewidth=0.5, zorder=1)

# Draw relationships first (behind tables)
for src, dst, label, style in RELATIONSHIPS:
    try:
        p1, p2 = get_edge_points(src, dst)
        ls = "--" if style == "dashed" else "-"
        ax.annotate("",
            xy=p2, xytext=p1,
            arrowprops=dict(
                arrowstyle="-|>",
                color="#88AABB" if style == "dashed" else "#AACCDD",
                lw=1.0 if style == "solid" else 0.7,
                linestyle=ls,
                connectionstyle="arc3,rad=0.05",
                mutation_scale=8,
            ),
            zorder=2
        )
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=4.5, color="#BBDDEE",
                bbox=dict(boxstyle="round,pad=0.1", facecolor="#1A1A2E",
                          edgecolor="none", alpha=0.7),
                zorder=2)
    except Exception:
        pass

# Draw tables
for name, config in TABLES.items():
    draw_table(ax, name, config)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_x, legend_y = -0.4, 10.8
ax.text(legend_x, legend_y, "LAYER", fontsize=6, color="white",
        fontweight="bold")
layer_info = [
    ("MASTER", "#4A90D9"),
    ("TRANSACTION", "#E67E22"),
    ("ANALYTICAL", "#27AE60"),
    ("OPERATIONAL", "#8E44AD"),
]
for i, (lbl, lc) in enumerate(layer_info):
    px = legend_x + i * 1.6
    ax.add_patch(FancyBboxPatch((px, legend_y - 0.35), 1.5, 0.28,
                                boxstyle="round,pad=0.02",
                                facecolor=lc, edgecolor="none", zorder=5))
    ax.text(px + 0.75, legend_y - 0.21, lbl,
            ha="center", va="center", fontsize=5.5,
            fontweight="bold", color="white", zorder=6)

role_info = [("PK", "#E74C3C"), ("FK", "#3498DB"), ("TARGET", "#F39C12")]
for i, (lbl, lc) in enumerate(role_info):
    px = legend_x + i * 1.0
    ax.add_patch(FancyBboxPatch((px, legend_y - 0.75), 0.35, 0.25,
                                boxstyle="round,pad=0.02",
                                facecolor=lc, edgecolor="none", zorder=5))
    ax.text(px + 0.18, legend_y - 0.625, lbl,
            ha="center", va="center", fontsize=4.5,
            fontweight="bold", color="white", zorder=6)
    ax.text(px + 0.45, legend_y - 0.625, "= " + {
        "PK": "Primary Key", "FK": "Foreign Key", "TARGET": "Dự báo"
    }[lbl], ha="left", va="center", fontsize=4.5, color="#CCDDEE", zorder=6)

# Title
ax.text(5.5, 11.0,
        "DATATHON 2026 — The Gridbreakers\nEntity Relationship Diagram",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color="white",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#0D1B2A",
                  edgecolor="#4A90D9", linewidth=1.5))

plt.tight_layout(pad=0)
plt.savefig("erd_datathon2026.png", dpi=180, bbox_inches="tight",
            facecolor="#1A1A2E")
print("✅ Saved: erd_datathon2026.png")
plt.show()
