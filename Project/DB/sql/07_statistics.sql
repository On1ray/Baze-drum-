SELECT 
    (SELECT COUNT(*) FROM purchaser) as total_clients,
    (SELECT COUNT(*) FROM employee) as total_employees,
    (SELECT COUNT(*) FROM product) as total_products,
    (SELECT COUNT(*) FROM "order") as total_orders,
    (SELECT SUM(oi.quantity * oi.price * (100 - oi.discount) / 100) FROM order_item oi) as total_sales;