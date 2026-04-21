WITH last_year AS (
    SELECT DATE('now', '-1 year') AS start_date
)
SELECT
    pl.id AS price_list_id,
    pc.name AS category_name,
    COUNT(DISTINCT o.id) AS total_orders,
    COUNT(DISTINCT CASE WHEN pd.id IS NOT NULL THEN o.id END) AS paid_orders,
    COUNT(DISTINCT o.buyer_id) AS distinct_buyers_used,
    (SELECT COUNT(*) FROM purchaser WHERE price_category_id = pl.category_id) AS eligible_buyers,
    ROUND(100.0 * COUNT(DISTINCT o.buyer_id) / NULLIF((SELECT COUNT(*) FROM purchaser WHERE price_category_id = pl.category_id), 0), 2) AS usage_percent
FROM price_list pl
JOIN price_category pc ON pc.id = pl.category_id
LEFT JOIN "order" o ON o.price_list_id = pl.id AND o.issue_date >= (SELECT start_date FROM last_year)
LEFT JOIN payment_doc pd ON pd.order_id = o.id
GROUP BY pl.id, pc.name
HAVING COUNT(DISTINCT o.id) > 0
ORDER BY usage_percent DESC, total_orders DESC;