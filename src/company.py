from typing import Any, Optional


class Company:
    """
    Класс для представления компании.

    :param company_name: Название компании.
    :param company_id: Уникальный идентификатор компании (из API hh.ru).
    :param site_url: Сайт компании (опционально).
    """

    def __init__(self, company_name: str, company_id: Optional[str | int], site_url: str = ""):
        if not company_id:
            print(f" Компания '{company_name}' пропущена: отсутствует company_id")
            self.company_id = ""
        else:
            self.company_id = str(company_id)
        self.company_name = company_name.strip() or "Без названия"
        self.site_url = site_url.strip()

    def __repr__(self) -> str:
        return f"Company('{self.company_name}', '{self.company_id}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Company):
            return False
        if not self.company_id or not other.company_id:
            return False
        return self.company_id == other.company_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_name": self.company_name,
            "company_id": self.company_id,
            "site_url": self.site_url
        }
