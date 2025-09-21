from dataclasses import dataclass


@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "hh_vacancies"
    user: str = "postgres"
    password: str = "0055"


DB_CONFIG = DBConfig()


VACANCIES_PER_PAGE = 5
