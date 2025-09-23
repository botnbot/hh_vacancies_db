import requests
from src.base_api import BaseAPI
from src.vacancy import Vacancy


class HeadHunterAPI(BaseAPI):
    """Класс для работы с API hh.ru"""

    BASE_URL = "https://api.hh.ru/vacancies"

    def get_vacancies(self, keyword: str, per_page: int = 20, max_pages: int = 5) -> list[Vacancy]:
        vacancies: list[Vacancy] = []

        for page in range(max_pages):
            params = {
                "text": keyword,
                "per_page": per_page,
                "page": page,
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            if response.status_code != 200:
                print(f"Ошибка запроса к HH API: {response.status_code}")
                break

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                vacancy = Vacancy.from_api(item)
                vacancies.append(vacancy)

        return vacancies
