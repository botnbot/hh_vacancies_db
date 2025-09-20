from typing import Optional
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection
from config import DB_CONFIG


class DatabaseCreator:
    """Класс для создания БД и таблиц"""

    def __init__(self, config=DB_CONFIG):
        self.config = config

    def get_connection(self, database_name: Optional[str] = None) -> Optional[connection]:
        """Устанавливает соединение с указанной базой данных"""
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=database_name or self.config.name,
                user=self.config.user,
                password=self.config.password,
            )
            return conn
        except Exception as e:
            print(f"Ошибка подключения к БД '{database_name or self.config.name}': {e}")
            return None

    def create_database(self) -> bool:
        """Создаёт базу данных, если она не существует"""
        try:
            conn = self.get_connection("postgres")
            if not conn:
                return False
            conn.autocommit = True

            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.config.name,))
                exists = cur.fetchone()
                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.config.name)))
                    print(f"База данных '{self.config.name}' создана")
                else:
                    print(f"База данных '{self.config.name}' уже существует")

            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")
            return False

    def create_tables(self) -> bool:
        """Создаёт таблицы в базе данных"""
        try:
            conn = self.get_connection()
            if not conn:
                return False

            with conn.cursor() as cur:
                # Таблица компаний
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS companies (
                        company_id INTEGER PRIMARY KEY,
                        company_name VARCHAR(255) NOT NULL,
                        site_url VARCHAR(255),
                        region VARCHAR(100),
                        telephone VARCHAR(50),
                        email VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Таблица вакансий
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies (
                        url VARCHAR(255) PRIMARY KEY,
                        company_id INTEGER NOT NULL,
                        vacancy_name VARCHAR(255) NOT NULL,
                        requirements TEXT,
                        salary NUMERIC,
                        remote BOOLEAN DEFAULT FALSE,
                        experience VARCHAR(100),
                        currency VARCHAR(10),
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (company_id)
                            REFERENCES companies(company_id)
                            ON DELETE CASCADE
                    )
                """
                )

            conn.commit()
            conn.close()
            print("Таблицы созданы успешно")
            return True

        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            return False

    def setup_database(self) -> bool:
        """Полная настройка базы данных"""
        print("Настройка базы данных...")
        if self.create_database() and self.create_tables():
            print("База данных настроена успешно")
            return True
        return False
