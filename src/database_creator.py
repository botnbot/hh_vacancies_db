import psycopg2
from psycopg2 import sql
from config import DB_CONFIG


class DatabaseCreator:
    """Класс для создания базы данных и таблиц."""

    def __init__(self):
        self.db_name = DB_CONFIG.name

    def _get_connection(self, dbname="postgres"):
        """Создаёт соединение с указанной БД."""
        return psycopg2.connect(
            host=DB_CONFIG.host,
            database=dbname,
            user=DB_CONFIG.user,
            password=DB_CONFIG.password,
            port=DB_CONFIG.port,
        )

    def setup_database(self):
        """Настраивает базу данных и таблицы."""
        self._create_database()
        self._create_tables()

    def ensure_database(self):
        """Создаёт базу и таблицы, если их нет."""
        self._create_database()
        self._create_tables()

    def _create_database(self):
        """Создаёт базу данных, если её нет."""
        try:
            conn = self._get_connection()
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))
            print(f"База данных '{self.db_name}' успешно создана")
        except psycopg2.errors.DuplicateDatabase:
            print(f"База данных '{self.db_name}' уже существует")
        finally:
            conn.close()

    def _create_tables(self):
        """Создаёт таблицы companies и vacancies с актуальной схемой."""
        conn = self._get_connection(self.db_name)
        with conn:
            with conn.cursor() as cur:
                # Таблица компаний
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        company_name TEXT NOT NULL,
                        company_name_real TEXT NOT NULL,
                        company_id TEXT UNIQUE,
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
                        salary_from NUMERIC,
                        salary_to NUMERIC,
                        experience TEXT,
                        remote BOOLEAN,
                        company_name_real TEXT NOT NULL,
                        company_id TEXT REFERENCES companies(company_id),
                        currency TEXT DEFAULT 'RUR'
                    );
                    """
                )
            conn.commit()
        print("Таблицы созданы успешно")
        conn.close()
