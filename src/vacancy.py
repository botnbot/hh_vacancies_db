from typing import Optional

from utils.helpers import wrap_text


class Vacancy:
    """
    Класс для представления вакансии.
    """

    __slots__ = (
        "title",
        "url",
        "description",
        "salary_from",
        "salary_to",
        "experience",
        "remote",
        "company_id",
        "company_name",
        "currency",
    )

    def __init__(
        self,
        title: str,
        url: str = "",
        description: str = "",
        salary_range: Optional[tuple[Optional[float], Optional[float]]] = (None, None),
        experience: str = "не указан",
        remote: bool = False,
    ):
        self.title = title
        self.url = url
        self.description = description
        self.salary_from, self.salary_to = salary_range or (None, None)
        self.experience = experience
        self.remote = remote

        self.company_id: Optional[str] = None
        self.company_name: str = "Не указано"
        self.currency: str = "RUR"

    def __repr__(self) -> str:
        salary = (
            f"{self.salary_from or 0}-{self.salary_to or 0} {self.currency}"
            if self.salary_from or self.salary_to
            else "не указана"
        )
        return f"Vacancy('{self.title}', {salary}, remote={self.remote}, company='{self.company_name}')"

    def __str__(self) -> str:
        salary = (
            f"{self.salary_from or 0}-{self.salary_to or 0} {self.currency}"
            if self.salary_from or self.salary_to
            else "не указана"
        )
        remote_str = "Да" if self.remote else "Нет"
        description_wrapped = wrap_text(self.description, width=80)
        return (
            f"Компания: {self.company_name}\n"
            f"Вакансия: {self.title}\n"
            f"Зарплата: {salary}\n"
            f"Опыт: {self.experience}\n"
            f"Удалённая: {remote_str}\n"
            f"Ссылка: {self.url}\n"
            f"Описание:\n{description_wrapped}\n" + "-" * 80
        )

    def __lt__(self, other: "Vacancy") -> bool:
        """
        Сравнение вакансий по средней зарплате для сортировки.
        Если зарплата не указана — считаем её равной 0.
        """
        self_avg = ((self.salary_from or 0) + (self.salary_to or 0)) / 2
        other_avg = ((other.salary_from or 0) + (other.salary_to or 0)) / 2
        return self_avg < other_avg

    @classmethod
    def from_dict(cls, data: dict) -> "Vacancy":
        """
        Создаёт объект Vacancy из словаря.
        Поддерживает как salary_range (from, to), так и общее поле salary.
        """
        salary_from = None
        salary_to = None

        if "salary_range" in data and isinstance(data["salary_range"], (list, tuple)):
            salary_from, salary_to = data.get("salary_range", (None, None))
        elif "salary" in data:
            salary_from = data.get("salary")
            salary_to = data.get("salary")

        vacancy = cls(
            title=data.get("title", "Без названия"),
            url=data.get("url", ""),
            description=data.get("description", "Описание отсутствует"),
            salary_range=(salary_from, salary_to),
            experience=data.get("experience", "не указан"),
            remote=data.get("remote", False),
        )

        vacancy.company_name = data.get("company_name") or "Не указано"
        vacancy.company_id = data.get("company_id")
        vacancy.currency = data.get("currency", "RUR")
        return vacancy

    def to_dict(self) -> dict:
        """
        Преобразует объект Vacancy в словарь (например, для сохранения в БД).
        """
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to,
            "experience": self.experience,
            "remote": self.remote,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "currency": self.currency,
        }
