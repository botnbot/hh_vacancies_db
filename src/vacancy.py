from typing import Optional


class Vacancy:
    __slots__ = (
        "title",
        "url",
        "description",
        "salary_from",
        "salary_to",
        "experience",
        "remote",
        "company_id",
        "company_name_real",
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
        self.salary_from, self.salary_to = salary_range
        self.experience = experience
        self.remote = remote
        self.company_id: Optional[str] = None
        self.company_name_real: str = "Не указано"
        self.currency: str = "RUR"

    @classmethod
    def from_dict(cls, data: dict):
        """Создает объект из словаря, используемого внутри проекта"""
        return cls(
            title=data.get("title", "Без названия"),
            url=data.get("url", ""),
            description=data.get("description", ""),
            salary_range=(data.get("salary_from"), data.get("salary_to")),
            experience=data.get("experience", "не указан"),
            remote=data.get("remote", False),
        )

    @classmethod
    def from_api(cls, item: dict):
        """Создает объект Vacancy из JSON hh.ru API"""
        salary = item.get("salary") or {}
        employer = item.get("employer") or {}
        experience = item.get("experience") or {}
        schedule = item.get("schedule") or {}

        vacancy = cls(
            title=item.get("name", "Без названия"),
            url=item.get("alternate_url", ""),
            description=(item.get("snippet") or {}).get("requirement", ""),
            salary_range=(salary.get("from"), salary.get("to")),
            experience=experience.get("name", "не указан"),
            remote=schedule.get("name") == "remote" or "удален" in item.get("name", "").lower(),
        )

        vacancy.company_id = employer.get("id")
        vacancy.company_name_real = employer.get("name", "Не указано")
        vacancy.currency = salary.get("currency", "RUR")

        return vacancy

    def __repr__(self):
        salary = (
            f"{self.salary_from or 0}-{self.salary_to or 0} {self.currency}"
            if self.salary_from or self.salary_to
            else "не указана"
        )
        return f"Vacancy('{self.title}', {salary}, remote={self.remote}, company='{self.company_name_real}')"
