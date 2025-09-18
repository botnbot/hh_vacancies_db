import psycopg2
from src.hh_api import HHAPI
from src.db_manager import DBManager


class DataFiller:
    """Класс для заполнения базы данных данными"""

    def __init__(self, db_name: str = "hh_vacancies", user: str = "postgres",
                 password: str = "password", host: str = "localhost", port: int = 5432):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def get_connection(self):
        """Устанавливает соединение с базой данных"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user=self.user,
                password=self.password
            )
            conn.autocommit = False
            return conn
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return None

    def fill_vacancies(self, companies: list, per_page: int = 20, max_pages: int = 5):
        """
        Заполняет базу данных вакансиями указанных компаний.

        :param companies: список объектов Company
        :param per_page: количество вакансий на страницу
        :param max_pages: максимальное количество страниц
        """
        conn = self.get_connection()
        if not conn:
            return

        try:
            db_manager = DBManager(conn)
            hh_api = HHAPI()

            for company in companies:
                if not company.company_id:
                    print(f"Компания '{company.company_name}' пропущена: отсутствует company_id")
                    continue

                print(f" Получение вакансий для компании: {company.company_name}")

                vacancies, companies_data = hh_api.get_vacancies_with_companies(
                    keyword=company.company_name,
                    per_page=per_page,
                    max_pages=max_pages
                )

                print(f" Найдено {len(vacancies)} вакансий для {company.company_name}")
                print(f" Найдено {len(companies_data)} компаний")

                for comp in companies_data:
                    db_manager.save_company(comp.to_dict())

                saved_count = db_manager.save_vacancies(vacancies)
                print(f" Сохранено вакансий: {saved_count}")

            conn.commit()
            print(" Данные успешно загружены в БД")

        except Exception as e:
            conn.rollback()
            print(f" Ошибка при заполнении базы данных: {e}")
        finally:
            conn.close()
