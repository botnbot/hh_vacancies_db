from typing import Any, Optional

import psycopg2
from psycopg2.extensions import connection


class DBManager:
    """Класс для работы с базой данных."""

    def __init__(self, conn: Optional[connection] = None):
        """Принимает соединение с БД извне или создаёт новое."""
        self.conn = conn

    def get_companies_and_vacancies_count(self) -> list[dict[str, Any]]:
        """Возвращает список компаний и количество вакансий у каждой."""
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
        """Возвращает список всех вакансий."""
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
                    "salary_from": r[4],
                    "salary_to": r[5],
                    "experience": r[6],
                    "remote": r[7],
                    "company_name_real": r[8],
                }
            )
        return results

    def get_avg_salary(self) -> float:
        """
        Возвращает среднюю зарплату по всем вакансиям.
        В расчет берутся только вакансии, где указана хотя бы одна граница зарплаты.
        """
        query = """
        SELECT AVG((salary_from + salary_to)/2.0)
        FROM vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            avg_salary = cur.fetchone()[0]
        return float(avg_salary) if avg_salary is not None else 0

    def get_vacancies_with_higher_salary(self) -> list[dict[str, Any]]:
        """Возвращает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        query = """
        SELECT * FROM vacancies
        WHERE (COALESCE(salary_from,0) + COALESCE(salary_to,0))/2.0 > %s;
        """
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
                    "salary_from": r[4],
                    "salary_to": r[5],
                    "experience": r[6],
                    "remote": r[7],
                    "company_name_real": r[8],
                }
            )
        return results

    def get_vacancies_with_keyword(self, keyword: str) -> list[dict[str, Any]]:
        """Возвращает вакансии, где ключевое слово встречается в названии или описании."""
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
                    "salary_from": r[4],
                    "salary_to": r[5],
                    "experience": r[6],
                    "remote": r[7],
                    "company_name_real": r[8],
                }
            )
        return results

    def get_vacancies_by_company(self, company_name_real: str) -> list[dict[str, Any]]:
        """Возвращает вакансии указанной компании."""
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
                    "salary_from": r[4],
                    "salary_to": r[5],
                    "experience": r[6],
                    "remote": r[7],
                    "company_name_real": r[8],
                }
            )
        return results

    def save_company(self, company_data: dict) -> None:
        """Сохраняет компанию в БД. Использует ON CONFLICT по company_id."""
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
        self.conn.commit()

    def save_vacancies(self, vacancies: list[Any]) -> int:
        """
        Сохраняет список вакансий в БД.
        Использует ON CONFLICT по url.
        """
        query = """
        INSERT INTO vacancies (vacancy_name, url, requirements, salary_from, salary_to, experience, remote, company_name_real)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                        getattr(vac, "salary_from"),
                        getattr(vac, "salary_to"),
                        getattr(vac, "experience", ""),
                        getattr(vac, "remote", False),
                        getattr(vac, "company_name", "Не указано"),
                    ),
                )
                saved_count += cur.rowcount
        self.conn.commit()
        return saved_count
