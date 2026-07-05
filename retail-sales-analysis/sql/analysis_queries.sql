-- ============================================================
-- Retail Sales Analysis — SQL Queries
-- Database: data/sales.db  (table: raw_sales)
-- Run with: sqlite3 data/sales.db < sql/analysis_queries.sql
-- ============================================================

-- --------------------------------------------------------
-- 0. DATA CLEANING: build a clean view to use in later queries
--    - normalizes inconsistent region casing/whitespace
--    - removes exact duplicate rows
--    - fills missing discount with 0
-- --------------------------------------------------------
DROP VIEW IF EXISTS clean_sales;
CREATE VIEW clean_sales AS
SELECT DISTINCT
    order_id,
    order_date,
    customer_id,
    COALESCE(customer_segment, 'Unknown')                  AS customer_segment,
    UPPER(TRIM(region))                                     AS region,   -- normalize e.g. 'north', 'NORTH ' -> 'NORTH'
    category,
    product,
    quantity,
    unit_price,
    COALESCE(discount, 0)                                   AS discount,
    total_sales,
    cost,
    profit
FROM raw_sales;

-- --------------------------------------------------------
-- 1. DATA QUALITY CHECK: rows removed by cleaning
-- --------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM raw_sales)   AS raw_row_count,
    (SELECT COUNT(*) FROM clean_sales) AS clean_row_count,
    (SELECT COUNT(*) FROM raw_sales) - (SELECT COUNT(*) FROM clean_sales) AS duplicates_removed;

-- --------------------------------------------------------
-- 2. MONTHLY REVENUE & PROFIT TREND
-- --------------------------------------------------------
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(total_sales), 2)    AS revenue,
    ROUND(SUM(profit), 2)         AS profit,
    COUNT(DISTINCT order_id)      AS orders
FROM clean_sales
GROUP BY month
ORDER BY month;

-- --------------------------------------------------------
-- 3. TOP 10 PRODUCTS BY REVENUE
-- --------------------------------------------------------
SELECT
    product,
    category,
    ROUND(SUM(total_sales), 2) AS revenue,
    SUM(quantity)               AS units_sold,
    ROUND(SUM(profit), 2)       AS profit
FROM clean_sales
GROUP BY product, category
ORDER BY revenue DESC
LIMIT 10;

-- --------------------------------------------------------
-- 4. REGIONAL PERFORMANCE
-- --------------------------------------------------------
SELECT
    region,
    ROUND(SUM(total_sales), 2)                       AS revenue,
    ROUND(SUM(profit), 2)                             AS profit,
    ROUND(100.0 * SUM(profit) / SUM(total_sales), 1)  AS profit_margin_pct,
    COUNT(DISTINCT order_id)                          AS orders
FROM clean_sales
GROUP BY region
ORDER BY revenue DESC;

-- --------------------------------------------------------
-- 5. CATEGORY PROFIT MARGIN COMPARISON
-- --------------------------------------------------------
SELECT
    category,
    ROUND(SUM(total_sales), 2)                        AS revenue,
    ROUND(SUM(profit), 2)                              AS profit,
    ROUND(100.0 * SUM(profit) / SUM(total_sales), 1)   AS profit_margin_pct
FROM clean_sales
GROUP BY category
ORDER BY profit_margin_pct DESC;

-- --------------------------------------------------------
-- 6. CUSTOMER SEGMENT VALUE
-- --------------------------------------------------------
SELECT
    customer_segment,
    COUNT(DISTINCT customer_id)               AS customers,
    ROUND(SUM(total_sales), 2)                AS revenue,
    ROUND(SUM(total_sales) / COUNT(DISTINCT customer_id), 2) AS revenue_per_customer
FROM clean_sales
GROUP BY customer_segment
ORDER BY revenue DESC;

-- --------------------------------------------------------
-- 7. RFM INPUTS (Recency, Frequency, Monetary) PER CUSTOMER
--    Recency = days since last order, relative to most recent order date in dataset
-- --------------------------------------------------------
WITH last_date AS (
    SELECT MAX(order_date) AS max_date FROM clean_sales
)
SELECT
    customer_id,
    CAST(julianday((SELECT max_date FROM last_date)) - julianday(MAX(order_date)) AS INTEGER) AS recency_days,
    COUNT(DISTINCT order_id)          AS frequency,
    ROUND(SUM(total_sales), 2)        AS monetary
FROM clean_sales
GROUP BY customer_id
ORDER BY monetary DESC
LIMIT 20;

-- --------------------------------------------------------
-- 8. TOP CUSTOMERS BY LIFETIME VALUE
-- --------------------------------------------------------
SELECT
    customer_id,
    customer_segment,
    ROUND(SUM(total_sales), 2)  AS lifetime_value,
    COUNT(DISTINCT order_id)    AS orders
FROM clean_sales
GROUP BY customer_id, customer_segment
ORDER BY lifetime_value DESC
LIMIT 10;

-- --------------------------------------------------------
-- 9. DISCOUNT IMPACT ON PROFIT MARGIN
-- --------------------------------------------------------
SELECT
    CASE
        WHEN discount = 0 THEN 'No Discount'
        WHEN discount <= 0.1 THEN 'Low (<=10%)'
        ELSE 'High (>10%)'
    END AS discount_band,
    ROUND(AVG(100.0 * profit / total_sales), 1) AS avg_profit_margin_pct,
    COUNT(*) AS orders
FROM clean_sales
WHERE total_sales > 0
GROUP BY discount_band
ORDER BY avg_profit_margin_pct DESC;
