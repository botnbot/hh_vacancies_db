import psycopg2
from config import DB_CONFIG


class DatabaseCreator:
    """Класс для создания и настройки базы данных"""

    def __init__(self):
        self.db_name = DB_CONFIG.name
        self.user = DB_CONFIG.user
        self.password = DB_CONFIG.password
        self.host = DB_CONFIG.host
        self.port = DB_CONFIG.port

    def _get_connection(self, db_name: str):
        """Устанавливает соединение с указанной базой данных"""
        return psycopg2.connect(
            host=self.host,
            database=db_name,
            user=self.user,
            password=self.password,
            port=self.port,
        )

    def setup_database(self):
        """Создаёт базу данных и таблицы"""
        try:
            conn = self._get_connection("postgres")
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.db_name}'")
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {self.db_name}")
                print(f"База данных '{self.db_name}' создана")
            else:
                print(f"База данных '{self.db_name}' уже существует")
            cur.close()
            conn.close()

            conn = self._get_connection(self.db_name)
            cur = conn.cursor()

            # Таблица компаний
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    company_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    company_name_real TEXT,
                    site_url TEXT
                );
            """
            )

            # Таблица вакансий
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    vacancy_name TEXT NOT NULL,
                    url TEXT UNIQUE,
                    requirements TEXT,
                    salary NUMERIC,
                    experience TEXT,
                    remote BOOLEAN,
                    company_id TEXT REFERENCES companies(company_id),
                    company_name_real TEXT
                );
            """
            )

            conn.commit()
            print("Таблицы созданы успешно")
        except Exception as e:
            print(f"Ошибка при создании базы данных или таблиц: {e}")
        finally:
            if conn:
                conn.close()
