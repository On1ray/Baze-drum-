PRAGMA foreign_keys = ON;

-- Создание таблицы ACCOUNT
CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login VARCHAR(50) UNIQUE,
    password_hash VARCHAR(50),
    email VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL CHECK (status IN ('active', 'blocked', 'pending'))
);

-- Создание таблицы PRICE_CATEGORY
CREATE TABLE IF NOT EXISTS price_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Создание таблицы EMPLOYEE
CREATE TABLE IF NOT EXISTS employee (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    inn VARCHAR(12) NOT NULL UNIQUE,
    passport VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('м', 'ж')),
    phone VARCHAR(20) NOT NULL,
    FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
);

-- Создание таблицы PURCHASER
CREATE TABLE IF NOT EXISTS purchaser (
    id INTEGER PRIMARY KEY,
    type VARCHAR(3) NOT NULL CHECK (type IN ('юр', 'физ')),
    price_category_id INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE,
    FOREIGN KEY (price_category_id) REFERENCES price_category(id),
    FOREIGN KEY (manager_id) REFERENCES employee(id)
);

-- Создание таблицы LEGAL_ENTITY
CREATE TABLE IF NOT EXISTS legal_entity (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    license_number VARCHAR(50),
    bank_details TEXT NOT NULL,
    firm_category VARCHAR(100) NOT NULL,
    FOREIGN KEY (id) REFERENCES purchaser(id) ON DELETE CASCADE
);

-- Создание таблицы PRIVATE_PERSON
CREATE TABLE IF NOT EXISTS private_person (
    id INTEGER PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    birth_year INTEGER NOT NULL CHECK (birth_year BETWEEN 1900 AND 2100),
    passport_data VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    FOREIGN KEY (id) REFERENCES purchaser(id) ON DELETE CASCADE
);

-- Создание таблицы POSITION
CREATE TABLE IF NOT EXISTS position (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(100) NOT NULL
);

-- Создание таблицы EMPLOYEE_POSITION
CREATE TABLE IF NOT EXISTS employee_position (
    employee_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    assignment_date DATE,
    PRIMARY KEY (employee_id, position_id),
    FOREIGN KEY (employee_id) REFERENCES employee(id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES position(id) ON DELETE CASCADE
);

-- Создание таблицы PRICE_LIST
CREATE TABLE IF NOT EXISTS price_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    category_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES price_category(id),
    FOREIGN KEY (employee_id) REFERENCES employee(id)
);

-- Создание таблицы PRODUCT
CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    certificate_number VARCHAR(100),
    packaging VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    purchase_price DECIMAL(10,2) NOT NULL CHECK (purchase_price >= 0),
    merchandiser_id INTEGER NOT NULL,
    FOREIGN KEY (merchandiser_id) REFERENCES employee(id)
);

-- Создание таблицы ORDER
CREATE TABLE IF NOT EXISTS "order" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_date DATETIME,
    release_date DATETIME,
    buyer_id INTEGER NOT NULL,
    price_list_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (buyer_id) REFERENCES purchaser(id),
    FOREIGN KEY (price_list_id) REFERENCES price_list(id),
    FOREIGN KEY (employee_id) REFERENCES employee(id)
);

-- Создание таблицы ORDER_ITEM
CREATE TABLE IF NOT EXISTS order_item (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    discount DECIMAL(5,2) DEFAULT 0 CHECK (discount >= 0 AND discount <= 100),
    is_missing BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- Создание таблицы PAYMENT_DOC
CREATE TABLE IF NOT EXISTS payment_doc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(20) NOT NULL CHECK (type IN ('наличный', 'безналичный')),
    payment_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    order_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE
);