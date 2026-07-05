"""
Retail Sales Analysis
======================
End-to-end analysis of a synthetic retail sales dataset:
1. Load & clean data
2. Exploratory Data Analysis (EDA)
3. Business insights: revenue trends, top products, regional performance
4. Customer segmentation via RFM (Recency, Frequency, Monetary)
5. Save all charts to notebooks/figures/

Run with: python3 notebooks/analysis.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "retail_sales.csv")
FIG_DIR = os.path.join(BASE_DIR, "notebooks", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ----------------------------------------------------------------
# 1. LOAD & CLEAN
# ----------------------------------------------------------------
df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])
print(f"Raw rows: {len(df)}")

# Normalize region casing/whitespace
df["region"] = df["region"].str.strip().str.title()

# Fill missing values
df["customer_segment"] = df["customer_segment"].fillna("Unknown")
df["discount"] = df["discount"].fillna(0)

# Drop exact duplicate rows
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows -> {len(df)} clean rows")

df["month"] = df["order_date"].dt.to_period("M").astype(str)
df["profit_margin"] = df["profit"] / df["total_sales"]

# ----------------------------------------------------------------
# 2. MONTHLY REVENUE & PROFIT TREND
# ----------------------------------------------------------------
monthly = df.groupby("month").agg(
    revenue=("total_sales", "sum"),
    profit=("profit", "sum"),
    orders=("order_id", "nunique")
).reset_index()

plt.figure(figsize=(11, 5))
plt.plot(monthly["month"], monthly["revenue"], marker="o", label="Revenue")
plt.plot(monthly["month"], monthly["profit"], marker="o", label="Profit")
plt.xticks(rotation=45, ha="right")
plt.title("Monthly Revenue & Profit Trend")
plt.ylabel("USD")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "01_monthly_trend.png"))
plt.close()

# ----------------------------------------------------------------
# 3. TOP PRODUCTS BY REVENUE
# ----------------------------------------------------------------
top_products = (
    df.groupby("product")["total_sales"].sum().sort_values(ascending=False).head(10)
)

plt.figure(figsize=(9, 6))
sns.barplot(x=top_products.values, y=top_products.index, hue=top_products.index,
            palette="viridis", legend=False)
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue (USD)")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "02_top_products.png"))
plt.close()

# ----------------------------------------------------------------
# 4. REGIONAL PERFORMANCE
# ----------------------------------------------------------------
region_perf = df.groupby("region").agg(
    revenue=("total_sales", "sum"),
    profit=("profit", "sum")
).reset_index()
region_perf["profit_margin_pct"] = (region_perf["profit"] / region_perf["revenue"] * 100).round(1)
region_perf = region_perf.sort_values("revenue", ascending=False)

fig, ax1 = plt.subplots(figsize=(9, 5))
sns.barplot(data=region_perf, x="region", y="revenue", hue="region", palette="crest",
            legend=False, ax=ax1)
ax1.set_ylabel("Revenue (USD)")
ax1.set_title("Revenue by Region (bars) & Profit Margin % (line)")
ax2 = ax1.twinx()
ax2.plot(region_perf["region"], region_perf["profit_margin_pct"], color="darkorange",
         marker="o", linewidth=2)
ax2.set_ylabel("Profit Margin %")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "03_regional_performance.png"))
plt.close()

# ----------------------------------------------------------------
# 5. CATEGORY PROFIT MARGIN
# ----------------------------------------------------------------
cat_perf = df.groupby("category").agg(
    revenue=("total_sales", "sum"),
    profit=("profit", "sum")
).reset_index()
cat_perf["profit_margin_pct"] = (cat_perf["profit"] / cat_perf["revenue"] * 100).round(1)
cat_perf = cat_perf.sort_values("profit_margin_pct", ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(data=cat_perf, x="profit_margin_pct", y="category", hue="category",
            palette="mako", legend=False)
plt.title("Profit Margin % by Category")
plt.xlabel("Profit Margin (%)")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "04_category_margin.png"))
plt.close()

# ----------------------------------------------------------------
# 6. RFM CUSTOMER SEGMENTATION
# ----------------------------------------------------------------
snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)
rfm = df.groupby("customer_id").agg(
    recency=("order_date", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("total_sales", "sum")
).reset_index()

# Score 1-4 (4 = best) using quartiles
rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]


def segment_customer(score):
    if score >= 10:
        return "Champions"
    elif score >= 8:
        return "Loyal"
    elif score >= 6:
        return "Potential"
    else:
        return "At Risk"


rfm["segment"] = rfm["rfm_score"].apply(segment_customer)

seg_counts = rfm["segment"].value_counts()
plt.figure(figsize=(7, 5))
seg_order = ["Champions", "Loyal", "Potential", "At Risk"]
sns.barplot(x=seg_counts.reindex(seg_order).values, y=seg_order, hue=seg_order,
            palette="rocket", legend=False)
plt.title("Customer Segments (RFM Analysis)")
plt.xlabel("Number of Customers")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "05_rfm_segments.png"))
plt.close()

rfm.to_csv(os.path.join(BASE_DIR, "data", "rfm_customer_segments.csv"), index=False)

# ----------------------------------------------------------------
# 7. DISCOUNT vs PROFIT MARGIN
# ----------------------------------------------------------------
def discount_band(d):
    if d == 0:
        return "No Discount"
    elif d <= 0.1:
        return "Low (<=10%)"
    else:
        return "High (>10%)"


df["discount_band"] = df["discount"].apply(discount_band)
disc_margin = df.groupby("discount_band")["profit_margin"].mean().reindex(
    ["No Discount", "Low (<=10%)", "High (>10%)"]
) * 100

plt.figure(figsize=(7, 5))
sns.barplot(x=disc_margin.index, y=disc_margin.values, hue=disc_margin.index,
            palette="flare", legend=False)
plt.title("Average Profit Margin by Discount Band")
plt.ylabel("Avg Profit Margin (%)")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "06_discount_impact.png"))
plt.close()

# ----------------------------------------------------------------
# 8. PRINT KEY INSIGHTS
# ----------------------------------------------------------------
total_revenue = df["total_sales"].sum()
total_profit = df["profit"].sum()
overall_margin = total_profit / total_revenue * 100

print("\n================ KEY INSIGHTS ================")
print(f"Total Revenue:      ${total_revenue:,.2f}")
print(f"Total Profit:       ${total_profit:,.2f}")
print(f"Overall Margin:     {overall_margin:.1f}%")
print(f"Top Product:        {top_products.index[0]} (${top_products.iloc[0]:,.2f})")
print(f"Best Region:        {region_perf.iloc[0]['region']} (${region_perf.iloc[0]['revenue']:,.2f})")
print(f"Best Category Margin: {cat_perf.iloc[0]['category']} ({cat_perf.iloc[0]['profit_margin_pct']}%)")
print(f"Customer segments:  {dict(seg_counts)}")
print(f"No-discount margin vs high-discount margin: {disc_margin['No Discount']:.1f}% vs {disc_margin['High (>10%)']:.1f}%")
print("================================================")
print(f"\nCharts saved to: {FIG_DIR}")
print(f"RFM segments saved to: data/rfm_customer_segments.csv")
