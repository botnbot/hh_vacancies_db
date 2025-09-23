class Company:
    """
    Класс для представления компании.
    """
    def __init__(self, company_name_real: str, company_id: str = None, site_url: str = ""):
        self.company_name_real = company_name_real
        self.company_id = company_id
        self.site_url = site_url

    def __repr__(self):
        return f"Company('{self.company_name_real}', id={self.company_id})"
