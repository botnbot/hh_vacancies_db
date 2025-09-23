import psycopg2
from config import DB_CONFIG


class DBManager:
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_CONFIG.host,
            database=DB_CONFIG.name,
            user=DB_CONFIG.user,
            password=DB_CONFIG.password,
            port=DB_CONFIG.port,
        )

    def get_companies_and_vacancies_count(self):
        """Список компаний и количество вакансий у каждой."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.company_name_real, COUNT(v.id) AS vacancies_count
                FROM companies c
                LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.company_name_real
                ORDER BY vacancies_count DESC;
            """)
            return [{"company_name_real": row[0], "vacancy_count": row[1]} for row in cur.fetchall()]

    def get_all_vacancies(self):
        """Список всех вакансий с указанием компании, зарплаты и ссылки, отсортированных по зарплате."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT v.vacancy_name, v.url, v.requirements, v.salary_from, v.salary_to,
                       v.experience, v.remote, v.company_name_real, v.company_id
                FROM vacancies v
                ORDER BY (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0))/2 DESC NULLS LAST;
            """)
            return [
                {
                    "vacancy_name": row[0],
                    "url": row[1],
                    "requirements": row[2],
                    "salary_from": row[3],
                    "salary_to": row[4],
                    "experience": row[5],
                    "remote": row[6],
                    "company_name_real": row[7],
                    "company_id": row[8],
                }
                for row in cur.fetchall()
            ]

    def get_avg_salary(self):
        """Средняя зарплата по всем вакансиям."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_from + salary_to)/2)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
            """)
            result = cur.fetchone()[0]
            return result if result is not None else 0

    def get_vacancies_with_higher_salary(self):
        """Вакансии с зарплатой выше средней, отсортированные по убыванию зарплаты."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT v.vacancy_name, v.url, v.requirements, v.salary_from, v.salary_to,
                       v.experience, v.remote, v.company_name_real, v.company_id
                FROM vacancies v
                WHERE (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0))/2 >
                      (SELECT AVG(COALESCE(salary_from,0) + COALESCE(salary_to,0))/2 FROM vacancies)
                ORDER BY (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0))/2 DESC NULLS LAST;
            """)
            return [
                {
                    "vacancy_name": row[0],
                    "url": row[1],
                    "requirements": row[2],
                    "salary_from": row[3],
                    "salary_to": row[4],
                    "experience": row[5],
                    "remote": row[6],
                    "company_name_real": row[7],
                    "company_id": row[8],
                }
                for row in cur.fetchall()
            ]

    def get_vacancies_with_keyword(self, keyword: str):
        """Поиск вакансий по ключевому слову в названии, отсортированных по зарплате."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT v.vacancy_name, v.url, v.requirements, v.salary_from, v.salary_to,
                       v.experience, v.remote, v.company_name_real, v.company_id
                FROM vacancies v
                WHERE v.vacancy_name ILIKE %s
                ORDER BY (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0))/2 DESC NULLS LAST;
            """, (f"%{keyword}%",))
            return [
                {
                    "vacancy_name": row[0],
                    "url": row[1],
                    "requirements": row[2],
                    "salary_from": row[3],
                    "salary_to": row[4],
                    "experience": row[5],
                    "remote": row[6],
                    "company_name_real": row[7],
                    "company_id": row[8],
                }
                for row in cur.fetchall()
            ]

    def get_vacancies_by_company(self, company_name: str):
        """Список вакансий для конкретной компании, отсортированных по зарплате."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT v.vacancy_name, v.url, v.requirements, v.salary_from, v.salary_to,
                       v.experience, v.remote, v.company_name_real, v.company_id
                FROM vacancies v
                WHERE v.company_name_real ILIKE %s
                ORDER BY (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0))/2 DESC NULLS LAST;
            """, (f"%{company_name}%",))
            return [
                {
                    "vacancy_name": row[0],
                    "url": row[1],
                    "requirements": row[2],
                    "salary_from": row[3],
                    "salary_to": row[4],
                    "experience": row[5],
                    "remote": row[6],
                    "company_name_real": row[7],
                    "company_id": row[8],
                }
                for row in cur.fetchall()
            ]

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()
