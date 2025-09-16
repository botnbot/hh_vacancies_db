from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.vacancy import Vacancy


class BaseAPI(ABC):
    """Абстрактный класс для API сервисов вакансий"""

    @abstractmethod
    def get_vacancies(self, keyword: str, per_page: int = 20, max_pages: int = 5) -> list["Vacancy"]:
        """Получение списка вакансий по ключевому слову"""
        pass

