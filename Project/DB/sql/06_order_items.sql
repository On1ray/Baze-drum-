SELECT 
    oi.order_id,
    oi.product_id,
    pr.name as product_name,
    oi.quantity,
    oi.price,
    oi.discount,
    CASE WHEN oi.is_missing = 1 THEN 'Да' ELSE 'Нет' END as is_missing,
    ROUND(oi.quantity * oi.price * (100 - oi.discount) / 100, 2) as total
FROM order_item oi
LEFT JOIN product pr ON pr.id = oi.product_id
ORDER BY oi.order_id, oi.product_id;