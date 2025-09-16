from typing import Any, List
import requests
from src.base_api import BaseAPI
from src.company import Company
from src.vacancy import Vacancy


class HHAPI(BaseAPI):
    """Класс для работы с API hh.ru - только получение данных"""

    def __init__(self):
        """Инициализация API без зависимостей от БД"""
        self.base_url = "https://api.hh.ru/vacancies"

    def _fetch_page(self, keyword: str, page: int = 0, per_page: int = 20) -> Any:
        """Отправляет запрос к API hh.ru и возвращает JSON-ответ."""
        params: dict = {"text": keyword, "page": page, "per_page": per_page}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

    def _parse_vacancy(self, item: dict) -> Vacancy:
        """Парсит данные вакансии из JSON-ответа"""
        title = item.get("name", "Без названия")
        url = item.get("alternate_url", "")

        snippet = item.get("snippet", {})
        responsibility = snippet.get("responsibility", "")
        requirement = snippet.get("requirement", "")
        description = f"{responsibility} {requirement}".strip()

        salary_data = item.get("salary")
        if salary_data:
            low = salary_data.get("from") or 0
            high = salary_data.get("to") or low
            salary_range = (low, high)
        else:
            salary_range = (0, 0)

        experience = item.get("experience", {}).get("name", "не указан")

        schedule = item.get("schedule", {})
        remote = schedule.get("name") == "remote" or "удален" in title.lower()

        return Vacancy(
            title=title,
            url=url,
            description=description,
            salary_range=salary_range,
            experience=experience,
            remote=remote
        )

    def _parse_company(self, item: dict) -> Company:
        """Парсит данные компании из JSON-ответа"""
        employer = item.get("employer", {})
        company_id = employer.get("id", "")
        company_name = employer.get("name", "Без названия")
        company_site_url = employer.get("site_url", "")

        return Company(
            company_id=company_id,
            company_name=company_name,
            site_url=company_site_url
        )

    def get_vacancies(self, keyword: str, per_page: int = 20,
                      max_pages: int = 5) -> List[Vacancy]:
        """
        Получает список вакансий по ключевому слову

        Args:
            keyword: Ключевое слово для поиска
            per_page: Количество вакансий на странице
            max_pages: Максимальное количество страниц

        Returns:
            List[Vacancy]: Список объектов Vacancy
        """
        vacancies = []

        for page in range(max_pages):
            try:
                data = self._fetch_page(keyword, page=page, per_page=per_page)
                items = data.get("items", [])

                for item in items:
                    vacancy = self._parse_vacancy(item)
                    vacancies.append(vacancy)

            except Exception as e:
                print(f"Ошибка при обработке страницы {page}: {e}")
                continue

        return vacancies

    def get_vacancies_with_companies(self, keyword: str, per_page: int = 20,
                                     max_pages: int = 5) -> tuple[List[Vacancy], List[Company]]:
        """
        Дополнительный метод для получения вакансий и компаний

        Returns:
            tuple: (список вакансий, список компаний)
        """
        vacancies = []
        companies = []
        seen_company_ids = set()

        for page in range(max_pages):
            try:
                data = self._fetch_page(keyword, page=page, per_page=per_page)
                items = data.get("items", [])

                for item in items:
                    vacancy = self._parse_vacancy(item)
                    company = self._parse_company(item)

                    vacancies.append(vacancy)

                    if company.company_id not in seen_company_ids:
                        companies.append(company)
                        seen_company_ids.add(company.company_id)

            except Exception as e:
                print(f"Ошибка при обработке страницы {page}: {e}")
                continue

        return vacancies, companies