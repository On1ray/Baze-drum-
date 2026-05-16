-- 1. Составной индекс для ускорения соединения product -> order_item -> order
CREATE INDEX IF NOT EXISTS idx_order_item_product_order ON order_item(product_id, order_id);

-- 2. Обычный индекс на дату заказа (заменяет частичный из-за ограничений SQLite)
CREATE INDEX IF NOT EXISTS idx_order_issue_date ON "order"(issue_date);

-- 3. Покрывающий индекс для order_item (все поля, нужные в запросе №4)
CREATE INDEX IF NOT EXISTS idx_order_item_covering ON order_item(product_id, quantity, price, discount, order_id);

-- 4. ЧАСТИЧНЫЙ индекс для запроса №5 – заказы только 2025 года (не использует date('now'))
--    Условие strftime('%Y', issue_date) = '2025' детерминировано для каждой строки.
CREATE INDEX IF NOT EXISTS idx_order_2025 ON "order"(employee_id, issue_date)
    WHERE strftime('%Y', issue_date) = '2025';

-- 5. Покрывающий индекс для order_item в запросе №5 (нужны order_id, quantity, price, discount)
CREATE INDEX IF NOT EXISTS idx_order_item_sales ON order_item(order_id, quantity, price, discount);

-- 6. Индекс для быстрого поиска должности менеджера
CREATE INDEX IF NOT EXISTS idx_employee_position_pos ON employee_position(position_id);