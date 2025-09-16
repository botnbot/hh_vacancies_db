from src.hh_api import HHAPI
from src.db_manager import DBManager
import psycopg2


class DataFiller:
    """Класс для заполнения базы данных данными"""

    def __init__(self, db_name: str = "hh_vacancies", user: str = "postgres",
                 password: str = "password", host: str = "localhost"):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

    def get_connection(self):
        """Устанавливает соединение с базой данных"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=self.db_name,
                user=self.user,
                password=self.password
            )
            return conn
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return None

    def fill_vacancies(self, companies: list):
        """Заполняет базу данных вакансиями указанных компаний"""
        try:
            conn = self.get_connection()
            if not conn:
                return

            db_manager = DBManager(conn)
            hh_api = HHAPI(conn)

            for company in companies:
                print(f"Получение вакансий для компании: {company}")
                vacancies, companies_data = hh_api.get_vacancies(company, max_pages=5)
                print(f"Найдено {len(vacancies)} вакансий")

            conn.close()

        except Exception as e:
            print(f"Ошибка при заполнении базы данных: {e}")