from typing import Any, Optional
import psycopg2
from psycopg2.extensions import connection


class DBManager:
    """Класс для работы с базой данных"""

    def __init__(self, conn: Optional[connection] = None):
        """Принимает соединение с БД извне или создает новое"""
        self.conn = conn

    def get_companies_and_vacancies_count(self) -> list[dict[str, Any]]:
        query = """
        SELECT company_name_real, COUNT(*) as vacancy_count
        FROM vacancies
        GROUP BY company_name_real
        ORDER BY vacancy_count DESC;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        return [{"company_name_real": r[0], "vacancy_count": r[1]} for r in rows]

    def get_all_vacancies(self) -> list[dict[str, Any]]:
        query = "SELECT * FROM vacancies;"
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        results = []
        for r in rows:
            results.append(
                {
                    "vacancy_name": r[1],
                    "url": r[2],
                    "requirements": r[3],
                    "salary": r[4],
                    "experience": r[5],
                    "remote": r[6],
                    "company_name_real": r[7],
                }
            )
        return results

    def get_avg_salary(self) -> float:
        query = "SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL;"
        with self.conn.cursor() as cur:
            cur.execute(query)
            avg_salary = cur.fetchone()[0]
        return avg_salary or 0

    def get_vacancies_with_higher_salary(self) -> list[dict[str, Any]]:
        avg_salary = self.get_avg_salary()
        query = "SELECT * FROM vacancies WHERE salary > %s;"
        with self.conn.cursor() as cur:
            cur.execute(query, (avg_salary,))
            rows = cur.fetchall()
        results = []
        for r in rows:
            results.append(
                {
                    "vacancy_name": r[1],
                    "url": r[2],
                    "requirements": r[3],
                    "salary": r[4],
                    "experience": r[5],
                    "remote": r[6],
                    "company_name_real": r[7],
                }
            )
        return results

    def get_vacancies_with_keyword(self, keyword: str) -> list[dict[str, Any]]:
        query = "SELECT * FROM vacancies WHERE vacancy_name ILIKE %s OR requirements ILIKE %s;"
        pattern = f"%{keyword}%"
        with self.conn.cursor() as cur:
            cur.execute(query, (pattern, pattern))
            rows = cur.fetchall()
        results = []
        for r in rows:
            results.append(
                {
                    "vacancy_name": r[1],
                    "url": r[2],
                    "requirements": r[3],
                    "salary": r[4],
                    "experience": r[5],
                    "remote": r[6],
                    "company_name_real": r[7],
                }
            )
        return results

    def get_vacancies_by_company(self, company_name_real: str) -> list[dict[str, Any]]:
        query = "SELECT * FROM vacancies WHERE company_name_real ILIKE %s;"
        with self.conn.cursor() as cur:
            cur.execute(query, (company_name_real,))
            rows = cur.fetchall()
        results = []
        for r in rows:
            results.append(
                {
                    "vacancy_name": r[1],
                    "url": r[2],
                    "requirements": r[3],
                    "salary": r[4],
                    "experience": r[5],
                    "remote": r[6],
                    "company_name_real": r[7],
                }
            )
        return results

    def save_company(self, company_data: dict) -> None:
        """
        Сохраняет компанию в базу данных. Используется ON CONFLICT по company_id.
        """
        sql = """
            INSERT INTO companies (company_name, company_name_real, company_id, site_url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING;
        """
        params = (
            company_data.get("company_name"),
            company_data.get("company_name_real"),
            company_data.get("company_id"),
            company_data.get("site_url"),
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)

    def save_vacancies(self, vacancies: list[Any]) -> int:
        query = """
        INSERT INTO vacancies (vacancy_name, url, requirements, salary, experience, remote, company_name_real)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """
        saved_count = 0
        with self.conn.cursor() as cur:
            for vac in vacancies:
                cur.execute(
                    query,
                    (
                        getattr(vac, "title", "Без названия"),
                        getattr(vac, "url", ""),
                        getattr(vac, "description", ""),
                        getattr(vac, "salary_range", (0, 0))[0],
                        getattr(vac, "experience", ""),
                        getattr(vac, "remote", False),
                        getattr(vac, "company_name_real", getattr(vac, "company_name", "Не указано")),
                    ),
                )
                saved_count += cur.rowcount
        self.conn.commit()
        return saved_count
