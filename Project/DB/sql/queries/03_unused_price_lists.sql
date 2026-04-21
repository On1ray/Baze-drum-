WITH half_year AS (
    SELECT DATE('now', '-6 months') AS start_date
)
SELECT
    pl.id AS price_list_id,
    pc.name AS category,
    pl.date AS price_list_date,
    e.full_name AS created_by,
    (SELECT COUNT(*) FROM product) AS total_products_in_price_list,
    COALESCE(usage_stats.distinct_sold_products, 0) AS distinct_sold_products,
    COALESCE(usage_stats.clients_used, 0) AS clients_used,
    usage_stats.last_used_date
FROM price_list pl
JOIN price_category pc ON pc.id = pl.category_id
JOIN employee e ON e.id = pl.employee_id
LEFT JOIN (
    SELECT 
        o.price_list_id,
        COUNT(DISTINCT oi.product_id) AS distinct_sold_products,
        COUNT(DISTINCT o.buyer_id) AS clients_used,
        MAX(o.issue_date) AS last_used_date
    FROM "order" o
    JOIN order_item oi ON oi.order_id = o.id
    GROUP BY o.price_list_id
) usage_stats ON usage_stats.price_list_id = pl.id
WHERE pl.date >= (SELECT start_date FROM half_year)
  AND NOT EXISTS (
    SELECT 1 
    FROM "order" o2 
    WHERE o2.price_list_id = pl.id 
      AND o2.issue_date >= (SELECT start_date FROM half_year)
  )
ORDER BY pl.date DESC;