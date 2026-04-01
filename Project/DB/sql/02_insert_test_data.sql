-- Должности
INSERT OR REPLACE INTO position (code, title) VALUES
    ('manager', 'Менеджер'),
    ('merchandiser', 'Товаровед'),
    ('cashier', 'Кассир'),
    ('head', 'Заведующий');

-- Категории прайс-листов
INSERT OR REPLACE INTO price_category (code, name, description) VALUES
    ('retail', 'Розничный', 'Для розничных покупателей'),
    ('wholesale', 'Оптовый', 'Для оптовых покупателей'),
    ('professional', 'Профессиональный', 'Для профессиональных клиентов');

-- Аккаунты сотрудников
INSERT OR REPLACE INTO account (id, login, password_hash, email, created_at, status) VALUES
    (1, 'ivanov', 'hash_123', 'ivanov@store.ru', '2024-01-01 10:00:00', 'active'),
    (2, 'petrova', 'hash_456', 'petrova@store.ru', '2024-01-02 11:00:00', 'active'),
    (3, 'sidorov', 'hash_789', 'sidorov@store.ru', '2024-01-03 12:00:00', 'active'),
    (4, 'kuznecova', 'hash_111', 'kuznecova@store.ru', '2024-01-04 13:00:00', 'active');

-- Сотрудники
INSERT OR REPLACE INTO employee (id, full_name, inn, passport, birth_date, gender, phone) VALUES
    (1, 'Иванов Иван Иванович', '123456789012', '4512 123456', '1985-05-15', 'м', '+79123456789'),
    (2, 'Петрова Мария Сергеевна', '234567890123', '4512 234567', '1990-08-22', 'ж', '+79234567890'),
    (3, 'Сидоров Алексей Петрович', '345678901234', '4512 345678', '1982-03-10', 'м', '+79345678901'),
    (4, 'Кузнецова Анна Владимировна', '456789012345', '4512 456789', '1978-11-30', 'ж', '+79456789012');

-- Назначение должностей сотрудникам
INSERT OR REPLACE INTO employee_position (employee_id, position_id, assignment_date) VALUES
    (1, 1, '2023-01-15'),  -- Иванов - менеджер
    (2, 2, '2023-01-20'),  -- Петрова - товаровед
    (3, 1, '2023-02-01'),  -- Сидоров - менеджер
    (4, 4, '2023-01-10'),  -- Кузнецова - заведующий
    (2, 3, '2023-06-01');  -- Петрова - также кассир

-- Аккаунты покупателей
INSERT OR REPLACE INTO account (id, login, password_hash, email, created_at, status) VALUES
    (5, 'tehno_prom', 'hash_tehno', 'tehno@prom.ru', '2024-01-10 14:00:00', 'active'),
    (6, NULL, NULL, NULL, '2024-01-15 15:00:00', 'active'),
    (7, 'roznichok', 'hash_rozn', 'roznichok@mail.ru', '2024-01-20 16:00:00', 'active');

-- Покупатели
INSERT OR REPLACE INTO purchaser (id, type, price_category_id, manager_id) VALUES
    (5, 'юр', 2, 1),  -- юрлицо, оптовый прайс, менеджер Иванов
    (6, 'физ', 1, 3),  -- физлицо, розничный прайс, менеджер Сидоров
    (7, 'физ', 3, 1);  -- физлицо, проф. прайс, менеджер Иванов

-- Юридическое лицо
INSERT OR REPLACE INTO legal_entity (id, name, legal_address, phone, bank_details, firm_category) VALUES
    (5, 'ООО "ТехноПром"', 'г. Москва, ул. Ленина, д. 10', '+74951234567',
     'р/с 40702810123456789012, БИК 044525225', 'оптовик');

-- Частные лица
INSERT OR REPLACE INTO private_person (id, last_name, first_name, middle_name, birth_year, passport_data, address, phone) VALUES
    (6, 'Смирнов', 'Дмитрий', 'Александрович', 1988, '4510 987654, выдан ОВД г. Москвы',
     'г. Москва, ул. Цветочная, д. 5, кв. 12', '+79112345678'),
    (7, 'Васильева', 'Елена', 'Петровна', 1992, '4511 123456, выдан ОВД г. Санкт-Петербурга',
     'г. Санкт-Петербург, Невский пр., д. 20, кв. 45', '+79223456789');

-- Товары
INSERT OR REPLACE INTO product (article, name, certificate_number, packaging, manufacturer, stock_quantity, purchase_price, merchandiser_id) VALUES
    ('TV-001', 'Телевизор Samsung 55"', 'Сертификат 12345', 'шт.', 'Samsung Electronics', 15, 35000.00, 2),
    ('TV-002', 'Телевизор LG 65"', 'Сертификат 12346', 'шт.', 'LG Electronics', 8, 52000.00, 2),
    ('PH-001', 'Смартфон Xiaomi 13', 'Сертификат 12347', 'шт.', 'Xiaomi', 25, 28000.00, 2),
    ('NB-001', 'Ноутбук Asus ROG', 'Сертификат 12348', 'шт.', 'Asus', 12, 85000.00, 2),
    ('ACC-001', 'Чехол для телефона', NULL, 'шт.', 'Generic', 100, 500.00, 2),
    ('ACC-002', 'Зарядное устройство', NULL, 'шт.', 'Belkin', 45, 1200.00, 2);

-- Прайс-листы
INSERT OR REPLACE INTO price_list (id, date, category_id, employee_id) VALUES
    (1, '2024-01-01', 1, 4),  -- розничный
    (2, '2024-01-01', 2, 4),  -- оптовый
    (3, '2024-01-01', 3, 4),  -- профессиональный
    (4, '2024-03-01', 1, 4);  -- обновлённый розничный

-- Заказы
INSERT OR REPLACE INTO "order" (id, issue_date, payment_date, release_date, buyer_id, price_list_id, employee_id) VALUES
    (1, '2024-02-15 10:30:00', '2024-02-15 16:20:00', '2024-02-16 14:00:00', 5, 2, 1),
    (2, '2024-02-20 14:15:00', '2024-02-20 15:30:00', '2024-02-21 11:00:00', 6, 1, 3),
    (3, '2024-03-01 11:45:00', '2024-03-02 10:00:00', '2024-03-03 09:30:00', 7, 3, 1);

-- Состав заказов
INSERT OR REPLACE INTO order_item (order_id, product_id, quantity, price, discount, is_missing) VALUES
    (1, 1, 2, 35000.00, 5.00, 0),
    (1, 4, 1, 85000.00, 10.00, 0),
    (2, 3, 1, 28000.00, 0, 0),
    (2, 5, 2, 500.00, 0, 1),
    (3, 2, 1, 52000.00, 0, 0),
    (3, 6, 3, 1200.00, 15.00, 0);

-- Платежные документы
INSERT OR REPLACE INTO payment_doc (id, type, payment_time, amount, order_id) VALUES
    (1, 'безналичный', '2024-02-15 16:20:00', 146500.00, 1),
    (2, 'наличный', '2024-02-20 15:30:00', 28000.00, 2),
    (3, 'наличный', '2024-03-02 10:00:00', 55060.00, 3);