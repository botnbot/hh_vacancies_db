import psycopg2
from src.hh_api import HeadHunterAPI
from src.company import Company
from config import DB_CONFIG


class DataFiller:
    """Класс для заполнения БД вакансиями через API hh.ru."""

    def __init__(self):
        self.api = HeadHunterAPI()

    def _get_connection(self):
        """Создаёт соединение с БД."""
        return psycopg2.connect(
            host=DB_CONFIG.host,
            database=DB_CONFIG.name,
            user=DB_CONFIG.user,
            password=DB_CONFIG.password,
            port=DB_CONFIG.port,
        )

    def _ensure_company(self, cur, company: Company) -> str:
        """
        Проверяет, есть ли компания в БД, и добавляет при необходимости.
        Возвращает company_id для вставки вакансий.
        """
        cur.execute("SELECT company_id FROM companies WHERE company_name_real = %s;", (company.company_name_real,))
        result = cur.fetchone()
        if result:
            return result[0]


        import uuid
        company_id = company.company_id or str(uuid.uuid4())

        cur.execute(
            """
            INSERT INTO companies (company_name, company_name_real, company_id, site_url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING;
            """,
            (company.company_name_real, company.company_name_real, company_id, company.site_url or "")
        )
        return company_id

    def fill_vacancies(self, companies: list[Company]):
        hh_api = HeadHunterAPI()
        conn = self._get_connection()
        total_inserted = 0

        with conn:
            with conn.cursor() as cur:
                for company in companies:
                    print(f"Получение вакансий для компании: {company}")
                    vacancies = hh_api.get_vacancies(keyword=company.company_name_real)
                    print(f"Найдено вакансий: {len(vacancies)}")

                    company_id = self._ensure_company(cur, company)

                    inserted_count = 0
                    for vac in vacancies:
                        vac.company_id = company_id
                        vac.company_name_real = company.company_name_real
                        cur.execute(
                            """
                            INSERT INTO vacancies (
                                vacancy_name, url, requirements, salary_from, salary_to,
                                remote, experience, company_name_real, company_id, currency
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (url) DO NOTHING
                            """,
                            (
                                vac.title,
                                vac.url,
                                vac.description,
                                vac.salary_from,
                                vac.salary_to,
                                vac.remote,
                                vac.experience,
                                vac.company_name_real,
                                vac.company_id,
                                vac.currency,
                            ),
                        )
                        inserted_count += cur.rowcount

                    total_inserted += inserted_count
                    print(f"Вставлено новых вакансий для {company.company_name_real}: {inserted_count}")

        conn.close()
        print(f"Всего новых вакансий сохранено в базе: {total_inserted}")
