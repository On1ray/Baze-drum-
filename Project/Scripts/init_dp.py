from run_sql import execute_sql_file

def init_database():
    print("=== Создание таблиц ===")
    execute_sql_file('E:/Рабочий/Учеба/БД/DB/DB/sql/01_create_tables.sql')
    print("\n=== Добавление тестовых данных ===")
    execute_sql_file('E:/Рабочий/Учеба/БД/DB/DB/sql/02_insert_test_data.sql')
    print("\nБаза данных успешно инициализирована!")

if __name__ == '__main__':
    init_database()