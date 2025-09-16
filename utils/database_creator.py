import psycopg2
from typing import Optional


class DatabaseCreator:
    """Класс для создания базы данных и таблиц"""

    def __init__(self, db_name: str = "hh_vacancies", user: str = "postgres",
                 password: str = "password", host: str = "localhost"):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

    def get_connection(self, database: Optional[str] = None):
        """Устанавливает соединение с базой данных"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=database or self.db_name,
                user=self.user,
                password=self.password
            )
            return conn
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return None

    def create_database(self):
        """Создает базу данных если не существует"""
        try:
            # Подключаемся к базе postgres для создания новой БД
            conn = self.get_connection("postgres")
            conn.autocommit = True
            cur = conn.cursor()

            # Проверяем существование базы данных
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(f"CREATE DATABASE {self.db_name}")
                print(f"База данных {self.db_name} создана")
            else:
                print(f"База данных {self.db_name} уже существует")

            cur.close()
            conn.close()

        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")

    def create_tables(self):
        """Создает таблицы в базе данных"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            # Таблица компаний
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id INTEGER PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    site_url VARCHAR(255),
                    region VARCHAR(100),
                    telephone VARCHAR(50),
                    email VARCHAR(255)
                )
            """)

            # Таблица вакансий
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    url VARCHAR(255) PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    vacancy_name VARCHAR(255) NOT NULL,
                    requirements TEXT,
                    salary NUMERIC,
                    remote BOOLEAN,
                    experience VARCHAR(100),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            cur.close()
            conn.close()
            print("Таблицы созданы успешно")

        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")