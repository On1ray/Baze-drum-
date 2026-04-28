-- ============================================================
-- 05_manager_monthly_rating.sql
-- Рейтинг менеджеров по продажам по месяцам выбранного года
-- Год: 2025 (можно изменить)
-- ============================================================

--EXPLAIN QUERY PLAN
WITH RECURSIVE
-- Генерируем 12 месяцев
months(month_num, month_name) AS (
    SELECT 1, 'Январь'
    UNION ALL
    SELECT month_num+1,
        CASE month_num+1
            WHEN 1 THEN 'Январь' WHEN 2 THEN 'Февраль' WHEN 3 THEN 'Март'
            WHEN 4 THEN 'Апрель' WHEN 5 THEN 'Май' WHEN 6 THEN 'Июнь'
            WHEN 7 THEN 'Июль' WHEN 8 THEN 'Август' WHEN 9 THEN 'Сентябрь'
            WHEN 10 THEN 'Октябрь' WHEN 11 THEN 'Ноябрь' WHEN 12 THEN 'Декабрь'
        END
    FROM months WHERE month_num < 12
),
-- Все менеджеры (сотрудники с должностью 'manager')
managers AS (
    SELECT DISTINCT e.id, e.full_name
    FROM employee e
    JOIN employee_position ep ON ep.employee_id = e.id
    JOIN position p ON p.id = ep.position_id
    WHERE p.code = 'manager'
),
-- Продажи по менеджерам и месяцам
monthly_sales AS (
    SELECT
        o.employee_id,
        strftime('%m', o.issue_date) AS month_num,
        COUNT(DISTINCT o.id) AS orders_count,
        SUM(oi.quantity) AS total_items,
        SUM(oi.quantity * oi.price * (100 - oi.discount) / 100) AS total_sales
    FROM "order" o
    JOIN order_item oi ON oi.order_id = o.id
    WHERE strftime('%Y', o.issue_date) = '2025'
    GROUP BY o.employee_id, month_num
),
-- Самый популярный товар (по количеству) для каждого менеджера и месяца
top_by_qty AS (
    SELECT
        o.employee_id,
        strftime('%m', o.issue_date) AS month_num,
        oi.product_id,
        SUM(oi.quantity) AS total_qty,
        ROW_NUMBER() OVER (PARTITION BY o.employee_id, strftime('%m', o.issue_date) ORDER BY SUM(oi.quantity) DESC) AS rn
    FROM "order" o
    JOIN order_item oi ON oi.order_id = o.id
    WHERE strftime('%Y', o.issue_date) = '2025'
    GROUP BY o.employee_id, month_num, oi.product_id
),
-- Самый доходный товар (по сумме) для каждого менеджера и месяца
top_by_revenue AS (
    SELECT
        o.employee_id,
        strftime('%m', o.issue_date) AS month_num,
        oi.product_id,
        SUM(oi.quantity * oi.price * (100 - oi.discount) / 100) AS total_revenue,
        ROW_NUMBER() OVER (PARTITION BY o.employee_id, strftime('%m', o.issue_date) ORDER BY SUM(oi.quantity * oi.price * (100 - oi.discount) / 100) DESC) AS rn
    FROM "order" o
    JOIN order_item oi ON oi.order_id = o.id
    WHERE strftime('%Y', o.issue_date) = '2025'
    GROUP BY o.employee_id, month_num, oi.product_id
),
-- Собираем итоговую таблицу со всеми месяцами и менеджерами
final_data AS (
    SELECT
        m.month_name,
        m.month_num,
        mg.full_name,
        COALESCE(ms.orders_count, 0) AS orders_count,
        ROUND(COALESCE(ms.total_sales, 0), 2) AS sales_amount,
        COALESCE(ms.total_items, 0) AS total_items_sold,
        (SELECT name FROM product WHERE id = tq.product_id) AS top_product_by_quantity,
        (SELECT name FROM product WHERE id = tr.product_id) AS top_product_by_revenue,
        LAG(COALESCE(ms.total_sales, 0), 1, 0) OVER (PARTITION BY mg.full_name ORDER BY m.month_num) AS prev_month_sales
    FROM months m
    CROSS JOIN managers mg
    LEFT JOIN monthly_sales ms ON ms.employee_id = mg.id AND ms.month_num = printf('%02d', m.month_num)
    LEFT JOIN top_by_qty tq ON tq.employee_id = mg.id AND tq.month_num = printf('%02d', m.month_num) AND tq.rn = 1
    LEFT JOIN top_by_revenue tr ON tr.employee_id = mg.id AND tr.month_num = printf('%02d', m.month_num) AND tr.rn = 1
)
SELECT
    month_name,
    full_name,
    orders_count,
    sales_amount,
    total_items_sold,
    COALESCE(top_product_by_quantity, '-') AS top_product_by_quantity,
    COALESCE(top_product_by_revenue, '-') AS top_product_by_revenue,
    CASE
        WHEN month_name = 'Январь' THEN 0.0
        WHEN prev_month_sales = 0 AND sales_amount > 0 THEN 100.0
        WHEN prev_month_sales = 0 AND sales_amount = 0 THEN 0.0
        ELSE ROUND(100.0 * (sales_amount - prev_month_sales) / prev_month_sales, 2)
    END AS growth_percent
FROM final_data
ORDER BY month_num, full_name;