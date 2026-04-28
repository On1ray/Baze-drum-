-- Триггер на вставку платежа
CREATE TRIGGER IF NOT EXISTS check_payment_doc_insert
BEFORE INSERT ON payment_doc
BEGIN
    SELECT CASE
        WHEN (SELECT COALESCE(SUM(oi.quantity * oi.price * (100 - oi.discount) / 100), 0)
              FROM order_item oi WHERE oi.order_id = NEW.order_id) > NEW.amount THEN
            RAISE(ABORT, 'Сумма заказа превышает сумму платежного документа')
    END;
END;

-- Триггер на обновление платежа
CREATE TRIGGER IF NOT EXISTS check_payment_doc_update
BEFORE UPDATE ON payment_doc
BEGIN
    SELECT CASE
        WHEN (SELECT COALESCE(SUM(oi.quantity * oi.price * (100 - oi.discount) / 100), 0)
              FROM order_item oi WHERE oi.order_id = NEW.order_id) > NEW.amount THEN
            RAISE(ABORT, 'Сумма заказа превышает сумму платежного документа')
    END;
END;

-- Запрет удаления платежа, привязанного к заказу
CREATE TRIGGER IF NOT EXISTS prevent_payment_doc_delete
BEFORE DELETE ON payment_doc
BEGIN
    SELECT CASE
        WHEN EXISTS (SELECT 1 FROM "order" WHERE id = OLD.order_id) THEN
            RAISE(ABORT, 'Нельзя удалить платежный документ, привязанный к заказу')
    END;
END;