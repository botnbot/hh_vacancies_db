from typing import Optional, Any
from psycopg2.extensions import connection
from .vacancy import Vacancy


class DBManager:
    """Класс для работы с данными в БД PostgreSQL"""

    def __init__(self, connection: connection) -> None:
        self.connection = connection

    def check_tables_exist(self) -> bool:
        """Проверяет существование таблиц в базе данных"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'vacancies'
                    )
                """
                )
                result = cur.fetchone()
                vacancies_exists = bool(result and result[0])

                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'companies'
                    )
                """
                )
                result = cur.fetchone()
                companies_exists = bool(result and result[0])

                return vacancies_exists and companies_exists
        except Exception as e:
            print(f"Ошибка проверки таблиц: {e}")
            return False

    def _prepare_keyword_condition(
        self, keyword: str, search_fields: Optional[list[Any]], exact_match: bool, operator: str
    ) -> tuple[str, list[Any]]:
        """Вспомогательный метод для подготовки условия поиска по ключевым словам"""
        default_fields = ["vacancy_name", "requirements", "experience"]
        fields_to_search = search_fields if search_fields else default_fields

        keywords = [k.strip() for k in keyword.split() if k.strip()]
        params: list[Any] = []

        if not keywords:
            return "1=1", params

        conditions: list[str] = []

        for kw in keywords:
            field_conditions: list[str] = []
            kw_params: list[Any] = []

            for field in fields_to_search:
                if exact_match:
                    field_conditions.append(f"LOWER(v.{field}) = LOWER(%s)")
                    kw_params.append(kw)
                else:
                    field_conditions.append(f"LOWER(v.{field}) LIKE LOWER(%s)")
                    kw_params.append(f"%{kw}%")

            if field_conditions:
                conditions.append(f"({' OR '.join(field_conditions)})")
                params.extend(kw_params)

        if operator.upper() == "AND" and conditions:
            final_condition = " AND ".join(conditions)
        elif conditions:
            final_condition = " OR ".join(conditions)
        else:
            final_condition = "1=1"

        return final_condition, params

    def _calculate_salary(self, vacancy: Vacancy) -> Optional[float]:
        """Вычисляет среднюю зарплату для объекта Vacancy"""
        try:
            if hasattr(vacancy, "salary_range"):
                salary_from, salary_to = vacancy.salary_range
                if salary_from and salary_to:
                    return (float(salary_from) + float(salary_to)) / 2
                elif salary_from:
                    return float(salary_from)
                elif salary_to:
                    return float(salary_to)
            return None
        except (ValueError, TypeError):
            return None

    def company_exists(self, company_id: int) -> bool:
        """Проверяет существование компании в БД"""
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT 1 FROM companies WHERE company_id = %s", (company_id,))
                result = cur.fetchone()
                return result is not None
        except Exception as e:
            print(f"Ошибка при проверке компании: {e}")
            return False

    def vacancy_exists(self, url: str) -> bool:
        """Проверяет существование вакансии в БД"""
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT 1 FROM vacancies WHERE url = %s", (url,))
                result = cur.fetchone()
                return result is not None
        except Exception as e:
            print(f"Ошибка при проверке вакансии: {e}")
            return False

    def save_company(self, company: dict) -> bool:
        """Сохраняет компанию в базу данных"""
        try:
            with self.connection.cursor() as cur:
                query = """
                    INSERT INTO companies (company_id, company_name, site_url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (company_id) DO UPDATE SET
                        company_name = EXCLUDED.company_name,
                        site_url = EXCLUDED.site_url
                """
                params = (company["company_id"], company["company_name"], company.get("site_url", ""))
                cur.execute(query, params)
                return True
        except Exception as e:
            print(f"Ошибка при сохранении компании: {e}")
            return False

    def get_vacancies_by_company(self, company_name: str, limit: int = 50, offset: int = 0) -> list:
        """Получает вакансии конкретной компании с пагинацией"""
        try:
            with self.connection.cursor() as cur:
                query = """
                    SELECT v.vacancy_name, v.salary, v.url, v.requirements,
                           v.experience, v.remote, v.last_updated
                    FROM vacancies v
                    JOIN companies c ON v.company_id = c.company_id
                    WHERE LOWER(c.company_name) LIKE LOWER(%s)
                    ORDER BY v.salary DESC NULLS LAST, v.vacancy_name
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, (f"%{company_name}%", limit, offset))
                results = cur.fetchall()

                return [
                    {
                        "vacancy_name": row[0],
                        "salary": row[1],
                        "url": row[2],
                        "requirements": row[3],
                        "experience": row[4],
                        "remote": row[5],
                        "last_updated": row[6],
                    }
                    for row in results
                ]

        except Exception as e:
            print(f"Ошибка при поиске вакансий компании: {e}")
            return []

    def save_vacancy(self, vacancy: dict, company_id: int) -> bool:
        """Сохраняет вакансию в базу данных"""
        try:
            if not vacancy.get("url") or not vacancy.get("title") or not company_id:
                print(f"Пропускаем вакансию с отсутствующими данными: {vacancy}")
                return False

            with self.connection.cursor() as cur:
                query = """
                    INSERT INTO vacancies (
                        url, company_id, vacancy_name, requirements,
                        salary, remote, experience, currency
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        vacancy_name = EXCLUDED.vacancy_name,
                        requirements = EXCLUDED.requirements,
                        salary = EXCLUDED.salary,
                        remote = EXCLUDED.remote,
                        experience = EXCLUDED.experience,
                        currency = EXCLUDED.currency,
                        last_updated = CURRENT_TIMESTAMP
                """
                params = (
                    vacancy["url"],
                    company_id,
                    vacancy["title"],
                    vacancy.get("description", "") or vacancy.get("requirements", ""),
                    vacancy.get("salary"),
                    vacancy.get("remote", False),
                    vacancy.get("experience", "не указан"),
                    vacancy.get("currency", "RUR"),
                )
                cur.execute(query, params)
                return True
        except Exception as e:
            print(f"Ошибка при сохранении вакансии {vacancy.get('url', 'unknown')}: {e}")
            return False

    def save_vacancies(self, vacancies: list[Vacancy]) -> int:
        """Сохраняет список вакансий в базу данных"""
        saved_count = 0
        try:
            with self.connection.cursor():
                for vacancy in vacancies:
                    company_id = getattr(vacancy, "company_id", None)
                    if not company_id:
                        print(f"[WARNING] Пропускаем вакансию без company_id: {getattr(vacancy, 'title', 'Unknown')}")
                        continue

                    if not self.company_exists(company_id):
                        company_name = getattr(vacancy, "company_name", "Неизвестная компания")
                        company_url = getattr(vacancy, "company_url", "") or getattr(vacancy, "site_url", "")
                        self.save_company(
                            {"company_id": company_id, "company_name": company_name, "site_url": company_url}
                        )

                    salary = self._calculate_salary(vacancy)
                    vacancy_data = {
                        "url": getattr(vacancy, "url", ""),
                        "title": getattr(vacancy, "title", "Без названия"),
                        "description": getattr(vacancy, "description", "") or getattr(vacancy, "requirements", ""),
                        "salary": salary,
                        "remote": getattr(vacancy, "remote", False),
                        "experience": getattr(vacancy, "experience", "не указан"),
                        "currency": getattr(vacancy, "currency", "RUR"),
                    }

                    if not vacancy_data["url"] or not vacancy_data["title"]:
                        continue

                    if self.save_vacancy(vacancy_data, company_id):
                        saved_count += 1

                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"[ERROR] Ошибка при сохранении вакансий: {e}")
        return saved_count

    # ===================== Методы получения данных =====================

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям"""
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT ROUND(AVG(salary), 2) FROM vacancies WHERE salary IS NOT NULL AND salary > 0")
                result = cur.fetchone()
                return float(result[0]) if result and result[0] is not None else 0.0
        except Exception as e:
            print(f"Ошибка при расчете средней зарплаты: {e}")
            return 0.0

    def get_all_vacancies(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Получает список всех вакансий с пагинацией"""
        try:
            with self.connection.cursor() as cur:
                query = """
                    SELECT c.company_name, v.vacancy_name, v.salary, v.url
                    FROM vacancies v
                    JOIN companies c ON v.company_id = c.company_id
                    ORDER BY c.company_name, v.vacancy_name
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, (limit, offset))
                results = cur.fetchall()
                return [{"company_name": r[0], "vacancy_name": r[1], "salary": r[2], "url": r[3]} for r in results]
        except Exception as e:
            print(f"Ошибка при получении списка вакансий: {e}")
            return []

    def get_vacancies_with_higher_salary(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Получает вакансии с зарплатой выше средней"""
        try:
            with self.connection.cursor() as cur:
                query = """
                    SELECT c.company_name, v.vacancy_name, v.salary, v.url
                    FROM vacancies v
                    JOIN companies c ON v.company_id = c.company_id
                    WHERE v.salary > (SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL AND salary > 0)
                    ORDER BY v.salary DESC, c.company_name
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, (limit, offset))
                results = cur.fetchall()
                return [{"company_name": r[0], "vacancy_name": r[1], "salary": r[2], "url": r[3]} for r in results]
        except Exception as e:
            print(f"Ошибка при поиске вакансий с высокой зарплатой: {e}")
            return []

    def get_vacancies_with_keyword(
        self,
        keyword: str = "",
        search_fields: Optional[list[Any]] = None,
        company_name: str = "",
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        exact_match: bool = False,
        operator: str = "OR",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """Расширенный поиск вакансий с пагинацией"""
        try:
            with self.connection.cursor() as cur:
                conditions = []
                params: list[Any] = []

                if keyword:
                    cond, cond_params = self._prepare_keyword_condition(keyword, search_fields, exact_match, operator)
                    conditions.append(cond)
                    params.extend(cond_params)

                if company_name:
                    conditions.append("LOWER(c.company_name) LIKE LOWER(%s)")
                    params.append(f"%{company_name}%")
                if min_salary is not None:
                    conditions.append("v.salary >= %s")
                    params.append(min_salary)
                if max_salary is not None:
                    conditions.append("v.salary <= %s")
                    params.append(max_salary)

                where_clause = " AND ".join(conditions) if conditions else "1=1"
                params.extend([limit, offset])

                query = f"""
                    SELECT c.company_name, v.vacancy_name, v.salary, v.url,
                           v.requirements, v.experience, v.remote
                    FROM vacancies v
                    JOIN companies c ON v.company_id = c.company_id
                    WHERE {where_clause}
                    ORDER BY v.salary DESC NULLS LAST, c.company_name, v.vacancy_name
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, params)
                results = cur.fetchall()
                return [
                    {
                        "company_name": r[0],
                        "vacancy_name": r[1],
                        "salary": r[2],
                        "url": r[3],
                        "requirements": r[4],
                        "experience": r[5],
                        "remote": r[6],
                    }
                    for r in results
                ]
        except Exception as e:
            print(f"Ошибка при поиске вакансий: {e}")
            return []

    def get_companies_and_vacancies_count(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Получает список компаний и количество вакансий"""
        try:
            with self.connection.cursor() as cur:
                query = """
                    SELECT c.company_name, COUNT(v.url) as vacancy_count
                    FROM companies c
                    LEFT JOIN vacancies v ON c.company_id = v.company_id
                    GROUP BY c.company_id, c.company_name
                    ORDER BY vacancy_count DESC, c.company_name
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, (limit, offset))
                results = cur.fetchall()
                return [{"company_name": r[0], "vacancy_count": r[1]} for r in results]
        except Exception as e:
            print(f"Ошибка при получении списка компаний: {e}")
            return []

    def get_total_count(self, table_name: str) -> int:
        """Получает общее количество записей в таблице"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = cur.fetchone()
                return int(result[0]) if result and result[0] is not None else 0
        except Exception as e:
            print(f"Ошибка при получении количества записей: {e}")
            return 0
