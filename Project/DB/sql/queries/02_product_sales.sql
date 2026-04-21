WITH half_year AS (
    SELECT DATE('now', '-6 months') AS start_date, DATE('now') AS end_date
),
product_sales AS (
    SELECT
        p.id,
        p.name,
        p.purchase_price,
        COUNT(DISTINCT o.price_list_id) AS distinct_price_lists,
        AVG(oi.price) AS avg_price,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.quantity * oi.price * (100 - oi.discount) / 100) AS total_revenue,
        MAX(o.issue_date) AS last_sale_date
    FROM product p
    JOIN order_item oi ON oi.product_id = p.id
    JOIN "order" o ON o.id = oi.order_id
    WHERE o.issue_date BETWEEN (SELECT start_date FROM half_year) AND (SELECT end_date FROM half_year)
    GROUP BY p.id, p.name, p.purchase_price
)
SELECT
    name,
    distinct_price_lists,
    ROUND(avg_price, 2) AS avg_sale_price,
    total_quantity,
    ROUND(total_revenue, 2) AS revenue,
    ROUND(total_revenue - (total_quantity * purchase_price), 2) AS profit,
    DATE(last_sale_date) AS last_sale_date
FROM product_sales
ORDER BY revenue DESC;