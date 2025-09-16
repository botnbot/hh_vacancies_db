from functools import total_ordering
from typing import Any, Dict, Tuple, Optional
from utils.helpers import wrap_text  # Используем существующую функцию


@total_ordering
class Vacancy:
    """Класс вакансии с приватными атрибутами и методами валидации"""

    __slots__ = ("__title", "__url", "__description", "__salary_range", "__experience", "__remote")

    def __init__(
            self,
            title: str,
            url: str,
            description: str,
            salary_range: Tuple[int, int] | int,
            experience: str = "не указан",
            remote: bool = False
    ) -> None:
        self.__title = self.__validate_string(title, "Без названия")
        self.__url = self.__validate_string(url, "")
        self.__description = self.__validate_string(description, "Описание отсутствует")
        self.__experience = self.__validate_string(experience, "не указан")
        self.__salary_range = self.__normalize_salary(salary_range)
        self.__remote = bool(remote)

    def __validate_string(self, value: str, default: str = "") -> str:
        if not isinstance(value, str) or not value.strip():
            return default
        return value.strip()

    def __normalize_salary(self, value: Tuple[int, int] | int) -> Tuple[int, int]:
        if isinstance(value, int):
            return (value, value)
        if isinstance(value, tuple) and len(value) == 2:
            try:
                return (int(value[0] or 0), int(value[1] or 0))
            except (ValueError, TypeError):
                return (0, 0)
        return (0, 0)

    @property
    def title(self) -> str:
        return self.__title

    @property
    def url(self) -> str:
        return self.__url

    @property
    def description(self) -> str:
        return self.__description

    @property
    def experience(self) -> str:
        return self.__experience

    @property
    def salary_range(self) -> Tuple[int, int]:
        return self.__salary_range

    @property
    def remote(self) -> bool:
        return self.__remote

    @property
    def avg_salary(self) -> int:
        return sum(self.__salary_range) // 2

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.__url == other.url

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.avg_salary < other.avg_salary

    def __repr__(self) -> str:
        return f"Vacancy({self.title!r}, {self.url!r}, {self.salary_range}, {self.experience!r})"

    def __str__(self) -> str:
        salary_from, salary_to = self.salary_range
        if salary_from or salary_to:
            salary_str = f"{salary_from}–{salary_to} руб."
        else:
            salary_str = "Зарплата не указана"

        remote_status = "Удаленная работа" if self.remote else "Офисная работа"

        # Используем существующую функцию wrap_text из helpers.py
        description_wrapped = wrap_text(self.description, width=80)

        return (
            f"{self.title}\n"
            f"Опыт: {self.experience}\n"
            f"Зарплата: {salary_str}\n"
            f"Тип работы: {remote_status}\n"
            f"Описание:\n{description_wrapped}\n"
            f"Ссылка: {self.url}\n"
            f"{'=' * 80}"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.__title,
            "url": self.__url,
            "description": self.__description,
            "salary_range": self.__salary_range,
            "experience": self.__experience,
            "remote": self.__remote
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vacancy":
        return cls(
            title=data.get("title", "Без названия"),
            url=data.get("url", ""),
            description=data.get("description", ""),
            salary_range=tuple(data.get("salary_range", (0, 0))),
            experience=data.get("experience", "не указан"),
            remote=data.get("remote", False)
        )