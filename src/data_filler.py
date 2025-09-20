from typing import Optional
from psycopg2.extensions import connection
import psycopg2

from config import DB_CONFIG
from src.db_manager import DBManager
from src.hh_api import HHAPI
from src.company import Company
from src.vacancy import Vacancy


class DataFiller:
    """Класс для заполнения базы данных данными"""

    def __init__(
        self,
        db_name: str = DB_CONFIG.name,
        user: str = DB_CONFIG.user,
        password: str = DB_CONFIG.password,
        host: str = DB_CONFIG.host,
        port: int = int(DB_CONFIG.port),
    ) -> None:
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def get_connection(self) -> Optional[connection]:
        """Устанавливает соединение с базой данных"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user=self.user,
                password=self.password,
            )
            conn.autocommit = False
            return conn
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return None

    def fill_vacancies(self, companies: list[Company], per_page: int = 20, max_pages: int = 5) -> None:
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
                print(f"\nПолучение вакансий для компании: {company.company_name_real}")
                vacancies: list[Vacancy] = []
                if company.company_id:
                    vacancies, companies_data = hh_api.get_vacancies_with_companies(
                        keyword=company.company_name_real, per_page=per_page, max_pages=max_pages
                    )
                    for comp in companies_data:
                        db_manager.save_company(comp.to_dict())
                else:
                    vacancies = hh_api.get_vacancies(
                        keyword=company.company_name_real, per_page=per_page, max_pages=max_pages
                    )

                saved_count = db_manager.save_vacancies(vacancies)
                print(f"Найдено вакансий: {len(vacancies)}, Сохранено: {saved_count}")

            conn.commit()
            print("\nДанные успешно загружены в БД")

        except Exception as e:
            conn.rollback()
            print(f"\nОшибка при заполнении базы данных: {e}")
        finally:
            conn.close()
