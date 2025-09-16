from typing import Any


class Company:
    """Класс для представления компании"""

    def __init__(self, company_name: str, company_id: str, site_url: str = ""):
        self.company_name = company_name.strip() or "Без названия"
        self.company_id = str(company_id) if company_id else ""
        self.site_url = site_url.strip()

    def __repr__(self) -> str:
        return f"Company('{self.company_name}', '{self.company_id}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Company):
            return False
        return self.company_id == other.company_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_name": self.company_name,
            "company_id": self.company_id,
            "site_url": self.site_url
        }