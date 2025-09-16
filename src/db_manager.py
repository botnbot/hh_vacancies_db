import psycopg2
from typing import List, Dict, Any, Optional, Tuple


class DBManager:
    """Класс для работы с данными в БД PostgreSQL"""

    def __init__(self, connection):
        self.connection = connection

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям

        :return: Средняя зарплата
        """
        try:
            with self.connection.cursor() as cur:
                query = """
                    SELECT ROUND(AVG(salary), 2) as average_salary
                    FROM vacancies
                    WHERE salary IS NOT NULL AND salary > 0
                """

                cur.execute(query)
                result = cur.fetchone()

                return result[0] if result and result[0] is not None else 0.0

        except Exception as e:
            print(f"Ошибка при расчете средней зарплаты: {e}")
            return 0.0

    def save_vacancy(self, vacancy: Dict[str, Any], company_id: int) -> bool:
        """
        Сохраняет вакансию в базу данных

        :param vacancy: Данные вакансии
        :param company_id: ID компании
        :return: True если успешно, False если ошибка
        """
        try:
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
                        last_updated = CURRENT_TIMESTAMP
                """

                params = (
                    vacancy['url'],
                    company_id,
                    vacancy['title'],
                    vacancy['description'],
                    vacancy.get('salary'),
                    vacancy.get('remote', False),
                    vacancy.get('experience', 'не указан'),
                    vacancy.get('currency', 'RUR')
                )

                cur.execute(query, params)
                self.connection.commit()
                return True

        except Exception as e:
            print(f"Ошибка при сохранении вакансии: {e}")
            return False

    def save_company(self, company: Dict[str, Any]) -> bool:
        """
        Сохраняет компанию в базу данных

        :param company: Данные компании
        :return: True если успешно, False если ошибка
        """
        try:
            with self.connection.cursor() as cur:
                query = """
                    INSERT INTO companies (company_id, company_name, site_url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (company_id) DO UPDATE SET
                        company_name = EXCLUDED.company_name,
                        site_url = EXCLUDED.site_url
                """

                params = (
                    company['company_id'],
                    company['company_name'],
                    company.get('site_url', '')
                )

                cur.execute(query, params)
                self.connection.commit()
                return True

        except Exception as e:
            print(f"Ошибка при сохранении компании: {e}")
            return False

    def company_exists(self, company_id: int) -> bool:
        """
        Проверяет существование компании в БД

        :param company_id: ID компании
        :return: True если существует, False если нет
        """
        try:
            with self.connection.cursor() as cur:
                query = "SELECT 1 FROM companies WHERE company_id = %s"
                cur.execute(query, (company_id,))
                return cur.fetchone() is not None

        except Exception as e:
            print(f"Ошибка при проверке компании: {e}")
            return False

    def vacancy_exists(self, url: str) -> bool:
        """
        Проверяет существование вакансии в БД

        :param url: URL вакансии
        :return: True если существует, False если нет
        """
        try:
            with self.connection.cursor() as cur:
                query = "SELECT 1 FROM vacancies WHERE url = %s"
                cur.execute(query, (url,))
                return cur.fetchone() is not None

        except Exception as e:
            print(f"Ошибка при проверке вакансии: {e}")
            return False

    def get_vacancies_by_company(self, company_name: str,
                                 limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает вакансии конкретной компании с пагинацией

        :param company_name: Название компании (частичное совпадение)
        :param limit: Количество записей на странице
        :param offset: Смещение для пагинации
        :return: Список вакансий компании
        """
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
                        'vacancy_name': row[0],
                        'salary': row[1],
                        'url': row[2],
                        'requirements': row[3],
                        'experience': row[4],
                        'remote': row[5],
                        'last_updated': row[6]
                    }
                    for row in results
                ]

        except Exception as e:
            print(f"Ошибка при поиске вакансий компании: {e}")
            return []

    def get_companies_and_vacancies_count(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает список компаний и количество вакансий с пагинацией
        """
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

                return [
                    {'company_name': row[0], 'vacancy_count': row[1]}
                    for row in results
                ]

        except Exception as e:
            print(f"Ошибка при получении списка компаний: {e}")
            return []

    def get_all_vacancies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с пагинацией
        """
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

                return [
                    {
                        'company_name': row[0],
                        'vacancy_name': row[1],
                        'salary': row[2],
                        'url': row[3]
                    }
                    for row in results
                ]

        except Exception as e:
            print(f"Ошибка при получении списка вакансий: {e}")
            return []

    def get_vacancies_with_higher_salary(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает вакансии с зарплатой выше средней с пагинацией
        """
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

                return [
                    {
                        'company_name': row[0],
                        'vacancy_name': row[1],
                        'salary': row[2],
                        'url': row[3]
                    }
                    for row in results
                ]

        except Exception as e:
            print(f"Ошибка при поиске вакансий с высокой зарплатой: {e}")
            return []

    def get_vacancies_with_keyword(self, keyword: str = "", company_name: str = "",
                                   min_salary: float = None, max_salary: float = None,
                                   search_fields: List[str] = None, exact_match: bool = False,
                                   operator: str = "OR", limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Расширенный поиск вакансий с пагинацией
        """
        try:
            with self.connection.cursor() as cur:
                conditions = []
                params = []

                if keyword:
                    keyword_condition, keyword_params = self._prepare_keyword_condition(
                        keyword, search_fields, exact_match, operator
                    )
                    conditions.append(keyword_condition)
                    params.extend(keyword_params)

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
                        'company_name': row[0],
                        'vacancy_name': row[1],
                        'salary': row[2],
                        'url': row[3],
                        'requirements': row[4],
                        'experience': row[5],
                        'remote': row[6]
                    }
                    for row in results
                ]

        except Exception as e:
            print(f"Ошибка при поиске вакансий: {e}")
            return []

    def get_total_count(self, table_name: str) -> int:
        """
        Получает общее количество записей в таблице

        :param table_name: Название таблицы ('vacancies' или 'companies')
        :return: Количество записей
        """
        try:
            with self.connection.cursor() as cur:
                query = f"SELECT COUNT(*) FROM {table_name}"
                cur.execute(query)
                result = cur.fetchone()
                return result[0] if result else 0

        except Exception as e:
            print(f"Ошибка при получении количества записей: {e}")
            return 0

    def _prepare_keyword_condition(self, keyword: str, search_fields: List[str],
                                   exact_match: bool, operator: str) -> str:
        """Вспомогательный метод для подготовки условия поиска"""
        default_fields = ['vacancy_name', 'requirements', 'experience']
        fields_to_search = search_fields if search_fields else default_fields

        keywords = [k.strip() for k in keyword.split() if k.strip()]

        if not keywords:
            return "1=1"

        conditions = []

        for kw in keywords:
            field_conditions = []

            for field in fields_to_search:
                if exact_match:
                    # Используем параметризованный запрос для безопасности
                    field_conditions.append(f"LOWER(v.{field}) = LOWER(%s)")
                else:
                    field_conditions.append(f"LOWER(v.{field}) LIKE LOWER(%s)")

            if field_conditions:
                # Объединяем условия для одного слова через OR
                conditions.append(f"({' OR '.join(field_conditions)})")

        # Объединяем условия для всех слов через выбранный оператор
        if operator.upper() == "AND":
            return " AND ".join(conditions)
        else:
            return " OR ".join(conditions)