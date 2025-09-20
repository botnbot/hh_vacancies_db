from typing import Any, Optional


class Company:
    """
    Класс для представления компании.

    :param company_name: Название компании.
    :param company_id: Уникальный идентификатор компании (из API hh.ru).
    :param site_url: Сайт компании (опционально).
    """

    def __init__(self, company_name: str, company_id: Optional[str | int] = None, site_url: str = ""):
        self.company_name = company_name.strip() or "Без названия"
        self.site_url = site_url.strip()

        if not company_id:
            company_id = self._fetch_company_id(self.company_name)

        if not company_id:
            print(f"Не удалось найти company_id для '{self.company_name}'")
            self.company_id = ""
        else:
            self.company_id = str(company_id)

    def __repr__(self) -> str:
        return f"Company('{self.company_name}', '{self.company_id}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Company):
            return False
        if not self.company_id or not other.company_id:
            return False
        return self.company_id == other.company_id

    def to_dict(self) -> dict[str, Any]:
        return {"company_name": self.company_name, "company_id": self.company_id, "site_url": self.site_url}

    @staticmethod
    def _fetch_company_id(company_name: str) -> Optional[str]:
        """
        Запрашивает company_id через API hh.ru по названию компании.
        """
        hh = HHAPI()
        companies, _ = hh.get_vacancies_with_companies(keyword=company_name, per_page=1, max_pages=1)
        if not _:
            return None
        company = next((c for c in _ if c.company_name.lower() == company_name.lower()), None)
        return company.company_id if company else None
