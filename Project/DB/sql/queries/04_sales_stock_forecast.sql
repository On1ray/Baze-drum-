--EXPLAIN QUERY PLAN
WITH params AS (
    --нужные даты в формате 'YYYY-MM-DD'
    SELECT 
        DATE('now', '-180 days') AS start_date,
        DATE('now') AS end_date
),
daily_sales AS (
    SELECT
        p.id,
        p.name,
        p.stock_quantity,
        COALESCE(SUM(oi.quantity), 0) AS sold_qty,
        COALESCE(SUM(oi.quantity * oi.price * (100 - oi.discount) / 100), 0) AS sales_amount,
        COUNT(DISTINCT o.id) AS transaction_count,
        MIN(o.issue_date) AS first_sale,
        MAX(o.issue_date) AS last_sale
    FROM product p
    LEFT JOIN order_item oi ON oi.product_id = p.id
    LEFT JOIN "order" o ON o.id = oi.order_id
        AND o.issue_date BETWEEN (SELECT start_date FROM params) AND (SELECT end_date FROM params)
    GROUP BY p.id, p.name, p.stock_quantity
),
period_days AS (
    SELECT JULIANDAY((SELECT end_date FROM params)) - JULIANDAY((SELECT start_date FROM params)) AS days
)
SELECT
    name,
    stock_quantity AS current_stock,
    sold_qty AS sold_last_period,
    ROUND(sales_amount, 2) AS sales_amount,
    CASE 
        WHEN transaction_count <= 1 THEN NULL
        ELSE ROUND((JULIANDAY(last_sale) - JULIANDAY(first_sale)) / (transaction_count - 1), 1)
    END AS avg_days_between_sales,
    CASE 
        WHEN sold_qty = 0 OR sold_qty IS NULL THEN NULL
        ELSE ROUND(stock_quantity / (sold_qty * 1.0 / (SELECT days FROM period_days)), 0)
    END AS forecast_days
FROM daily_sales
ORDER BY forecast_days NULLS LAST, name;