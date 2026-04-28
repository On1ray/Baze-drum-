-- Триггер на вставку в order_item
CREATE TRIGGER IF NOT EXISTS check_order_item_before_insert
BEFORE INSERT ON order_item
BEGIN
    SELECT CASE
        WHEN NEW.discount > 100 THEN
            RAISE(ABORT, 'Скидка не может превышать 100%')
        WHEN NOT EXISTS (
            SELECT 1 
            FROM price_list_product plp
            JOIN "order" o ON o.price_list_id = plp.price_list_id
            WHERE o.id = NEW.order_id AND plp.product_id = NEW.product_id
        ) THEN
            RAISE(ABORT, 'Цена для товара не установлена в прайс-листе заказа')
    END;
END;

-- Триггер на обновление order_item
CREATE TRIGGER IF NOT EXISTS check_order_item_before_update
BEFORE UPDATE ON order_item
BEGIN
    SELECT CASE
        WHEN NEW.discount > 100 THEN
            RAISE(ABORT, 'Скидка не может превышать 100%')
        WHEN NOT EXISTS (
            SELECT 1 
            FROM price_list_product plp
            JOIN "order" o ON o.price_list_id = plp.price_list_id
            WHERE o.id = NEW.order_id AND plp.product_id = NEW.product_id
        ) THEN
            RAISE(ABORT, 'Цена для товара не установлена в прайс-листе заказа')
    END;
END;