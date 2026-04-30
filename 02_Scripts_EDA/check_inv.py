import pandas as pd

inv = pd.read_csv('../datathon-2026-round-1/inventory.csv', parse_dates=['snapshot_date'])
inv['Month_Period'] = inv['snapshot_date'].dt.to_period('M')

monthly_inv = inv.groupby('Month_Period').agg(
    stock_on_hand=('stock_on_hand', 'sum'),
    units_sold=('units_sold', 'sum'),
    units_received=('units_received', 'sum')
).reset_index()

for year in [2013, 2015, 2017, 2019]:
    print(f"--- Năm {year} ---")
    data = monthly_inv[(monthly_inv['Month_Period'].dt.year == year) & (monthly_inv['Month_Period'].dt.month.isin([6,7,8,9,10]))]
    print(data)
