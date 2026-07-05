"""
Generates a synthetic retail sales dataset for the portfolio project.
Includes realistic messiness (duplicates, nulls, inconsistent casing)
so the project can demonstrate data cleaning skills, not just analysis.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_ORDERS = 6000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)
DAY_RANGE = (END_DATE - START_DATE).days

regions = ["North", "South", "East", "West", "Central"]
region_variants = {  # to simulate messy/inconsistent entries
    "North": ["North", "north", "NORTH", "North "],
    "South": ["South", "south", "SOUTH"],
    "East": ["East", "east", "EAST"],
    "West": ["West", "west", "WEST"],
    "Central": ["Central", "central", "CENTRAL"],
}

categories = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Smartwatch", "Laptop Stand", "Power Bank"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Cookware Set", "Vacuum Cleaner"],
    "Apparel": ["Running Shoes", "Denim Jacket", "Winter Coat", "T-Shirt Pack", "Yoga Pants"],
    "Beauty": ["Face Serum", "Hair Dryer", "Makeup Kit", "Shampoo Set", "Perfume"],
    "Sports & Outdoors": ["Yoga Mat", "Camping Tent", "Dumbbell Set", "Bike Helmet", "Water Bottle"],
}

# base price per product (unit_price will vary slightly around this)
base_prices = {}
for cat, prods in categories.items():
    for p in prods:
        base_prices[p] = np.round(np.random.uniform(8, 250), 2)

customer_segments = ["New", "Returning", "VIP"]

rows = []
customer_pool = [f"CUST{str(i).zfill(5)}" for i in range(1, 1801)]

for i in range(1, N_ORDERS + 1):
    order_id = f"ORD{str(i).zfill(6)}"
    order_date = START_DATE + timedelta(days=int(np.random.exponential(scale=DAY_RANGE / 2.2) % DAY_RANGE))
    category = np.random.choice(list(categories.keys()), p=[0.28, 0.22, 0.22, 0.16, 0.12])
    product = np.random.choice(categories[category])
    region_clean = np.random.choice(regions)
    region = np.random.choice(region_variants[region_clean])  # inject messiness
    customer_id = np.random.choice(customer_pool)
    segment = np.random.choice(customer_segments, p=[0.35, 0.45, 0.20])
    quantity = int(np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.15, 0.08, 0.05, 0.02]))
    unit_price = np.round(base_prices[product] * np.random.uniform(0.9, 1.1), 2)
    discount = np.random.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2], p=[0.5, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05])
    cost_ratio = np.random.uniform(0.45, 0.65)  # cost as fraction of unit price

    total_sales = np.round(quantity * unit_price * (1 - discount), 2)
    cost = np.round(quantity * unit_price * cost_ratio, 2)
    profit = np.round(total_sales - cost, 2)

    rows.append([
        order_id, order_date.strftime("%Y-%m-%d"), customer_id, segment,
        region, category, product, quantity, unit_price, discount,
        total_sales, cost, profit
    ])

df = pd.DataFrame(rows, columns=[
    "order_id", "order_date", "customer_id", "customer_segment",
    "region", "category", "product", "quantity", "unit_price", "discount",
    "total_sales", "cost", "profit"
])

# --- inject realistic messiness for cleaning practice ---
# 1. Some missing customer_segment values
mask_null_segment = df.sample(frac=0.03, random_state=1).index
df.loc[mask_null_segment, "customer_segment"] = np.nan

# 2. Some missing discount values
mask_null_discount = df.sample(frac=0.02, random_state=2).index
df.loc[mask_null_discount, "discount"] = np.nan

# 3. Duplicate a handful of rows
dupes = df.sample(frac=0.01, random_state=3)
df = pd.concat([df, dupes], ignore_index=True)

# 4. Shuffle rows so duplicates aren't obviously at the bottom
df = df.sample(frac=1, random_state=4).reset_index(drop=True)

df.to_csv("/home/claude/retail-sales-analysis/data/retail_sales.csv", index=False)
print(f"Generated {len(df)} rows -> data/retail_sales.csv")
print(df.head())
