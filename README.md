# Retail Sales Analysis

An end-to-end retail sales analysis project demonstrating data cleaning, SQL analysis, exploratory data analysis (EDA), and customer segmentation — built with **Python** and **SQL**.

## 📁 Project Structure

```
retail-sales-analysis/
├── data/
│   ├── generate_data.py          # Generates the synthetic (intentionally messy) dataset
│   ├── retail_sales.csv          # Raw dataset (6,060 orders, 2024–2025)
│   ├── sales.db                  # SQLite database (raw_sales table)
│   └── rfm_customer_segments.csv # Output: per-customer RFM scores & segments
├── sql/
│   └── analysis_queries.sql      # 9 SQL queries: cleaning view + business analysis
├── notebooks/
│   ├── analysis.py               # Full analysis pipeline as a runnable script
│   ├── retail_sales_analysis.ipynb  # Same analysis as a Jupyter notebook
│   └── figures/                  # Saved chart images (.png)
└── README.md
```

## 🎯 Objective

Analyze two years of retail transactions to answer:
- How is revenue and profit trending over time?
- Which products, categories, and regions drive the most value?
- Who are our most valuable customers, and who's at risk of churning?
- Is discounting actually helping the business, or hurting margin?

## 🧹 Data Cleaning

The raw dataset intentionally includes realistic messiness to demonstrate cleaning skills:
- Inconsistent region text (`"north"`, `"NORTH "`, `"North"` all refer to the same region)
- Missing values in `customer_segment` and `discount`
- ~1% duplicate order rows

Cleaning is handled two ways in this project:
- **SQL**: a `clean_sales` view in `sql/analysis_queries.sql` normalizes text, deduplicates, and fills nulls
- **Python**: equivalent logic in `notebooks/analysis.py` / the notebook

## 🛠️ Tools & Skills Used

| Area | Tools/Techniques |
|---|---|
| Data cleaning | pandas, SQL views, deduplication, null handling, text normalization |
| SQL analysis | Views, CTEs, window-style aggregation, `julianday()` date math |
| EDA & visualization | pandas, matplotlib, seaborn |
| Customer segmentation | RFM (Recency, Frequency, Monetary) quartile scoring |
| Business analysis | Revenue/profit trends, product & regional performance, discount impact |

## 📊 Key Findings

- **Total revenue:** $962,857.90 · **Total profit:** $415,047.75 · **Overall margin:** 43.1%
- **Top product:** Bluetooth Speaker (~$111.7K in revenue)
- **Best-performing region:** Central (~$200K in revenue)
- **Highest-margin category:** Beauty (43.4%)
- **Discounting hurts margin:** no-discount orders average a **44.9%** margin vs **33.3%** for orders discounted more than 10%
- **Customer segments (RFM):** Champions (485) · At Risk (447) · Potential (423) · Loyal (382) — the "At Risk" group is a meaningful re-engagement target

### Recommendations
1. Cap standard discounts around 10% — deeper discounts erode margin faster than they add volume.
2. Prioritize marketing spend on the Central region and Beauty category, the strongest performers.
3. Launch a win-back campaign targeted at the "At Risk" customer segment before they churn.

## ▶️ How to Run

```bash
# 1. Regenerate the dataset (optional — retail_sales.csv is already included)
python3 data/generate_data.py

# 2. Run the SQL analysis (requires sqlite3 CLI, or use any SQLite client on data/sales.db)
sqlite3 data/sales.db < sql/analysis_queries.sql

# 3. Run the full Python analysis (regenerates all charts in notebooks/figures/)
python3 notebooks/analysis.py

# Or open notebooks/retail_sales_analysis.ipynb in Jupyter to explore interactively
```

### Requirements
```
pandas
numpy
matplotlib
seaborn
```
Install with: `pip install -r requirements.txt`

## 📈 Sample Charts

See `notebooks/figures/` for all charts:
- `01_monthly_trend.png` — Revenue & profit over time
- `02_top_products.png` — Top 10 products by revenue
- `03_regional_performance.png` — Revenue & margin by region
- `04_category_margin.png` — Profit margin by category
- `05_rfm_segments.png` — Customer segment breakdown
- `06_discount_impact.png` — Discount band vs. profit margin

---
*This is a portfolio project built on synthetic data generated for demonstration purposes.*
