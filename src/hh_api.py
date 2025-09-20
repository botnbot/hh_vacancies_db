from typing import Any, Optional, List, Tuple
import requests

from src.base_api import BaseAPI
from src.company import Company
from src.vacancy import Vacancy


class HHAPI(BaseAPI):
    """Класс для работы с API hh.ru - получение данных вакансий и компаний"""

    def __init__(self) -> None:
        """Инициализация API без зависимостей от БД"""
        self.base_url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "HH-API-Client/1.0"}

    def _fetch_page(self, keyword: str, page: int = 0, per_page: int = 20) -> Any:
        """Отправляет запрос к API hh.ru и возвращает JSON-ответ."""
        params: dict = {"text": keyword, "page": page, "per_page": per_page}
        response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _parse_vacancy(self, item: dict) -> Vacancy:
        """Парсит данные вакансии из JSON-ответа"""
        title = item.get("name", "")
        url = item.get("alternate_url", "")

        employer = item.get("employer", {}) or {}
        company_id = employer.get("id")
        company_name = employer.get("name", "Не указано")

        snippet = item.get("snippet", {}) or {}
        responsibility = snippet.get("responsibility", "")
        requirement = snippet.get("requirement", "")
        description = f"{responsibility} {requirement}".strip()

        salary_data = item.get("salary")
        salary_from = salary_to = None
        currency = "RUR"
        if salary_data:
            salary_from = salary_data.get("from")
            salary_to = salary_data.get("to")
            currency = salary_data.get("currency", "RUR")

        experience = item.get("experience", {}).get("name", "не требуется")

        schedule = item.get("schedule", {}) or {}
        remote = schedule.get("name") == "remote" or "удален" in title.lower()

        vacancy = Vacancy(
            title=title,
            url=url,
            description=description,
            salary_range=(salary_from, salary_to),
            experience=experience,
            remote=remote,
        )

        vacancy.company_id = company_id
        vacancy.company_name = company_name
        vacancy.currency = currency

        return vacancy

    def _parse_company(self, item: dict) -> Optional[Company]:
        """Парсит данные компании из JSON-ответа"""
        employer = item.get("employer", {}) or {}
        company_id = employer.get("id")
        company_name = employer.get("name", "Без названия")
        company_site_url = employer.get("site_url", "")

        if not company_id:
            return None

        return Company(company_id=company_id, company_name=company_name, site_url=company_site_url)

    def get_vacancies(self, keyword: str, per_page: int = 20, max_pages: int = 5) -> List[Vacancy]:
        """Получает список вакансий по ключевому слову"""
        vacancies: list[Vacancy] = []
        try:
            first_page = self._fetch_page(keyword, page=0, per_page=per_page)
            total_pages = min(first_page.get("pages", 1), max_pages)
            items = first_page.get("items", [])
            vacancies.extend([self._parse_vacancy(item) for item in items])

            for page in range(1, total_pages):
                data = self._fetch_page(keyword, page=page, per_page=per_page)
                items = data.get("items", [])
                vacancies.extend([self._parse_vacancy(item) for item in items])

        except Exception as e:
            print(f"[ERROR] Ошибка при получении вакансий: {e}")

        return vacancies

    def get_vacancies_with_companies(
        self, keyword: str, per_page: int = 20, max_pages: int = 5
    ) -> Tuple[List[Vacancy], list[Company]]:
        """Получает список вакансий и компаний"""
        vacancies: list[Vacancy] = []
        companies: list[Company] = []
        seen_company_ids: set = set()

        try:
            first_page = self._fetch_page(keyword, page=0, per_page=per_page)
            total_pages = min(first_page.get("pages", 1), max_pages)
            items = first_page.get("items", [])

            for item in items:
                vacancy = self._parse_vacancy(item)
                company = self._parse_company(item)

                vacancies.append(vacancy)
                if company and company.company_id not in seen_company_ids:
                    companies.append(company)
                    seen_company_ids.add(company.company_id)

            for page in range(1, total_pages):
                data = self._fetch_page(keyword, page=page, per_page=per_page)
                items = data.get("items", [])

                for item in items:
                    vacancy = self._parse_vacancy(item)
                    company = self._parse_company(item)

                    vacancies.append(vacancy)
                    if company and company.company_id not in seen_company_ids:
                        companies.append(company)
                        seen_company_ids.add(company.company_id)

        except Exception as e:
            print(f"[ERROR] Ошибка при получении вакансий и компаний: {e}")

        return vacancies, companies
