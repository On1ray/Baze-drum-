PRAGMA foreign_keys = OFF;

-- ------------------------------------------------------------
-- 0. Полная очистка и сброс автоинкремента
-- ------------------------------------------------------------
DELETE FROM payment_doc;
DELETE FROM order_item;
DELETE FROM "order";
DELETE FROM price_list;
DELETE FROM product;
DELETE FROM private_person;
DELETE FROM legal_entity;
DELETE FROM purchaser;
DELETE FROM employee_position;
DELETE FROM employee;
DELETE FROM account;
DELETE FROM price_category;
DELETE FROM position;
DELETE FROM sqlite_sequence;

-- ------------------------------------------------------------
-- 1. Вспомогательная таблица чисел
-- ------------------------------------------------------------
DROP TABLE IF EXISTS temp_numbers;
CREATE TEMP TABLE temp_numbers AS
WITH RECURSIVE cnt(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM cnt WHERE x < 1000)
SELECT x AS n FROM cnt;

-- ------------------------------------------------------------
-- 2. Справочники (position, price_category)
-- ------------------------------------------------------------
INSERT INTO position (code, title) VALUES
    ('manager', 'Менеджер'),
    ('merchandiser', 'Товаровед'),
    ('cashier', 'Кассир'),
    ('head', 'Заведующий');

INSERT INTO price_category (code, name, description) VALUES
    ('retail', 'Розничный', 'Для розничных покупателей'),
    ('wholesale', 'Оптовый', 'Для оптовых покупателей'),
    ('professional', 'Профессиональный', 'Для профессиональных клиентов');

-- ------------------------------------------------------------
-- 3. Аккаунты: сотрудники (1..20), покупатели (21..70)
-- ------------------------------------------------------------
INSERT INTO account (login, password_hash, email, created_at, status)
SELECT
    'emp_' || n,
    'hash_' || n,
    'emp' || n || '@store.ru',
    datetime('2021-01-01', '+' || ((n-1)*30) || ' days'),
    'active'
FROM temp_numbers n WHERE n BETWEEN 1 AND 20;

INSERT INTO account (login, password_hash, email, created_at, status)
SELECT
    CASE WHEN (n % 5) = 0 THEN NULL ELSE 'client_' || (20 + n) END,
    CASE WHEN (n % 5) = 0 THEN NULL ELSE 'hash_' || (20 + n) END,
    CASE WHEN (n % 5) = 0 THEN NULL ELSE 'client' || (20 + n) || '@mail.ru' END,
    datetime('2021-02-01', '+' || (n*10) || ' days'),
    'active'
FROM temp_numbers n WHERE n BETWEEN 1 AND 50;

-- ------------------------------------------------------------
-- 4. Сотрудники (id = account.id для id <=20)
-- ------------------------------------------------------------
INSERT INTO employee (id, full_name, inn, passport, birth_date, gender, phone)
SELECT
    id,
    'Сотрудник_' || id || ' Фамилия',
    printf('%012d', 100000000000 + id),
    '4512 ' || printf('%06d', 100000 + id),
    date('1970-01-01', '+' || (id*365) || ' days'),
    CASE WHEN (id % 2) = 0 THEN 'м' ELSE 'ж' END,
    '+7916' || printf('%07d', 1000000 + id)
FROM account WHERE id <= 20;

-- ------------------------------------------------------------
-- 5. Должности сотрудников
-- ------------------------------------------------------------
INSERT INTO employee_position (employee_id, position_id, assignment_date)
SELECT
    e.id,
    CASE (e.id % 3)
        WHEN 0 THEN (SELECT id FROM position WHERE code = 'manager')
        WHEN 1 THEN (SELECT id FROM position WHERE code = 'merchandiser')
        ELSE (SELECT id FROM position WHERE code = 'cashier')
    END,
    date('2021-01-01')
FROM employee e;

INSERT INTO employee_position (employee_id, position_id, assignment_date)
SELECT id, (SELECT id FROM position WHERE code = 'head'), date('2022-01-01')
FROM employee WHERE id <= 5 ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 6. Покупатели 
-- ------------------------------------------------------------
INSERT INTO purchaser (id, type, price_category_id, manager_id)
SELECT
    id,
    CASE WHEN (id % 3) = 0 THEN 'юр' ELSE 'физ' END,
    CASE (id % 3)
        WHEN 0 THEN (SELECT id FROM price_category WHERE code = 'wholesale')
        WHEN 1 THEN (SELECT id FROM price_category WHERE code = 'retail')
        ELSE (SELECT id FROM price_category WHERE code = 'professional')
    END,
    1 + ((id - 21) % 20)
FROM account WHERE id > 20;

-- ------------------------------------------------------------
-- 7. Юридические и физические лица
-- ------------------------------------------------------------
INSERT INTO legal_entity (id, name, legal_address, phone, bank_details, firm_category)
SELECT p.id, 'ООО "Фирма ' || p.id || '"', 'г. Москва, ул. Примерная, д. ' || (p.id % 100),
       '+7495' || printf('%07d', 1000000 + p.id),
       'р/с 40702810' || printf('%010d', p.id) || ', БИК 044525225',
       CASE (p.id % 3) WHEN 0 THEN 'оптовик' WHEN 1 THEN 'дилер' ELSE 'розница' END
FROM purchaser p WHERE p.type = 'юр';

INSERT INTO private_person (id, last_name, first_name, middle_name, birth_year, passport_data, address, phone)
SELECT p.id, 'Фамилия_' || p.id, 'Имя_' || p.id, 'Отчество_' || p.id, 1970 + (p.id % 40),
       '4510 ' || printf('%06d', 500000 + p.id) || ', выдан ОВД',
       'г. Москва, ул. Жилая, д.' || (p.id % 100),
       '+7916' || printf('%07d', 2000000 + p.id)
FROM purchaser p WHERE p.type = 'физ';

-- ------------------------------------------------------------
-- 8. Товары (50 шт) – автоинкремент
-- ------------------------------------------------------------
INSERT INTO product (article, name, certificate_number, packaging, manufacturer, stock_quantity, purchase_price, merchandiser_id)
SELECT
    'PRD_' || printf('%04d', 100 + n),
    'Товар ' || (100 + n),
    CASE WHEN n % 3 = 0 THEN 'Серт-' || (100 + n) ELSE NULL END,
    'шт.',
    CASE (n % 4) WHEN 0 THEN 'Производитель А' WHEN 1 THEN 'Производитель Б' ELSE 'Производитель В' END,
    10 + (n % 100), 500.00 + (n * 150.0), 2
FROM temp_numbers n WHERE n BETWEEN 1 AND 50;

-- ------------------------------------------------------------
-- 9. Прайс-листы (каждый месяц с 2021-04 по 2026-04, 3 категории)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS temp_months;
CREATE TEMP TABLE temp_months AS
WITH RECURSIVE months(m) AS (SELECT 0 UNION ALL SELECT m+1 FROM months WHERE m < 60)
SELECT m FROM months;

INSERT INTO price_list (date, category_id, employee_id)
SELECT date('2021-04-01', '+' || m || ' months'), cat, 4
FROM temp_months CROSS JOIN (SELECT id AS cat FROM price_category) cats
WHERE m < 60;

-- ------------------------------------------------------------
-- 10. Заказы (300 шт) – случайные даты за 5 лет, price_list_id обязательно заполнен
-- ------------------------------------------------------------
DROP TABLE IF EXISTS temp_buyer_ids;
DROP TABLE IF EXISTS temp_emp_ids;
CREATE TEMP TABLE temp_buyer_ids AS SELECT id FROM purchaser;
CREATE TEMP TABLE temp_emp_ids AS SELECT id FROM employee 
    WHERE id IN (SELECT employee_id FROM employee_position WHERE position_id = (SELECT id FROM position WHERE code = 'manager'));

-- 1826 дней = 5 лет (с 2021-04-21 по 2026-04-21)
INSERT INTO "order" (issue_date, payment_date, release_date, buyer_id, price_list_id, employee_id)
SELECT
    datetime('2021-04-21', '+' || (abs(random()) % 1826) || ' days', '+' || (abs(random()) % 86400) || ' seconds'),
    CASE WHEN (abs(random()) % 100) < 75 
         THEN datetime('2021-04-21', '+' || (abs(random()) % 1826) || ' days', '+' || (abs(random()) % 86400) || ' seconds')
         ELSE NULL END,
    CASE WHEN (abs(random()) % 100) < 80 
         THEN datetime('2021-04-21', '+' || (abs(random()) % 1826) || ' days', '+' || (abs(random()) % 86400) || ' seconds')
         ELSE NULL END,
    (SELECT id FROM temp_buyer_ids ORDER BY random() LIMIT 1),
    (SELECT id FROM price_list ORDER BY random() LIMIT 1),
    (SELECT id FROM temp_emp_ids ORDER BY random() LIMIT 1)
FROM temp_numbers n WHERE n.n BETWEEN 1 AND 300;

-- ------------------------------------------------------------
-- 11. Позиции заказов (уникальные пары, ~900 записей)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS temp_product_ids;
CREATE TEMP TABLE temp_product_ids AS SELECT id FROM product;

INSERT OR IGNORE INTO order_item (order_id, product_id, quantity, price, discount, is_missing)
WITH order_items_gen AS (
    SELECT o.id AS order_id, p.id AS product_id,
           ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY random()) AS rn
    FROM "order" o CROSS JOIN temp_product_ids p
    WHERE (abs(random()) % 100) < 90
)
SELECT order_id, product_id,
       1 + (abs(random()) % 10) AS quantity,
       500.00 + (abs(random()) % 100000) AS price,
       CASE WHEN (abs(random()) % 100) < 25 THEN (abs(random()) % 30) ELSE 0 END AS discount,
       CASE WHEN (abs(random()) % 100) < 5 THEN 1 ELSE 0 END AS is_missing
FROM order_items_gen
WHERE rn <= (1 + (abs(random()) % 5))
LIMIT 900;

-- ------------------------------------------------------------
-- 12. Платежи (~70% от оплаченных заказов)
-- ------------------------------------------------------------
INSERT INTO payment_doc (type, payment_time, amount, order_id)
SELECT
    CASE WHEN (abs(random()) % 2) = 0 THEN 'наличный' ELSE 'безналичный' END,
    o.payment_date,
    ROUND(SUM(oi.quantity * oi.price * (100 - oi.discount) / 100), 2),
    o.id
FROM "order" o
JOIN order_item oi ON oi.order_id = o.id
WHERE o.payment_date IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM payment_doc WHERE order_id = o.id)
GROUP BY o.id
HAVING (abs(random()) % 100) < 70
LIMIT 200;

-- ------------------------------------------------------------
-- 13. Создание индексов для ускорения запросов (для EXPLAIN в запросах №4 и №5)
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_order_issue_date ON "order"(issue_date);
CREATE INDEX IF NOT EXISTS idx_order_employee_date ON "order"(employee_id, issue_date);
CREATE INDEX IF NOT EXISTS idx_order_price_list ON "order"(price_list_id);
CREATE INDEX IF NOT EXISTS idx_order_item_product ON order_item(product_id);
CREATE INDEX IF NOT EXISTS idx_order_item_order ON order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_employee_position ON employee_position(employee_id, position_id);
CREATE INDEX IF NOT EXISTS idx_purchaser_manager ON purchaser(manager_id);
CREATE INDEX IF NOT EXISTS idx_product_merchandiser ON product(merchandiser_id);

-- ------------------------------------------------------------
-- 14. Очистка временных таблиц
-- ------------------------------------------------------------
DROP TABLE IF EXISTS temp_numbers;
DROP TABLE IF EXISTS temp_months;
DROP TABLE IF EXISTS temp_buyer_ids;
DROP TABLE IF EXISTS temp_emp_ids;
DROP TABLE IF EXISTS temp_product_ids;

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 15. Статистика
-- ------------------------------------------------------------
SELECT 'Данные за 2021-2026 успешно загружены. Индексы созданы.' AS status,
       (SELECT COUNT(*) FROM employee) AS employees,
       (SELECT COUNT(*) FROM purchaser) AS purchasers,
       (SELECT COUNT(*) FROM product) AS products,
       (SELECT COUNT(*) FROM price_list) AS price_lists,
       (SELECT COUNT(*) FROM "order") AS orders,
       (SELECT COUNT(*) FROM order_item) AS order_items,
       (SELECT COUNT(*) FROM payment_doc) AS payments;

-- ------------------------------------------------------------
-- 16. Заполнение PRICE_LIST_PRODUCT 
-- ------------------------------------------------------------
INSERT OR IGNORE INTO price_list_product (price_list_id, product_id, price)
SELECT DISTINCT
    o.price_list_id,
    oi.product_id,
    MAX(oi.price) AS price   
FROM "order" o
JOIN order_item oi ON oi.order_id = o.id
WHERE o.price_list_id IS NOT NULL
GROUP BY o.price_list_id, oi.product_id;

--генерируем цену на основе закупочной + наценка по категории
INSERT INTO price_list_product (price_list_id, product_id, price)
SELECT
    pl.id AS price_list_id,
    p.id AS product_id,
    ROUND(p.purchase_price *
        CASE pc.code
            WHEN 'retail' THEN 1.5      
            WHEN 'wholesale' THEN 1.1    
            WHEN 'professional' THEN 1.3 
        END / 10) * 10 AS price   
FROM price_list pl
JOIN price_category pc ON pc.id = pl.category_id
CROSS JOIN product p
WHERE NOT EXISTS (
    SELECT 1 FROM price_list_product plp
    WHERE plp.price_list_id = pl.id AND plp.product_id = p.id
);