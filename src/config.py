"""
Конфигурация базы данных и API
"""

import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Конфигурация подключения к PostgreSQL"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: str = os.getenv("DB_PORT", "5432")
    name: str = os.getenv("DB_NAME", "hh_vacancies")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "password")

@dataclass
class APIConfig:
    """Конфигурация API"""
    base_url: str = "https://api.hh.ru"
    timeout: int = 30
    user_agent: str = "HHVacancyParser/1.0"

# Создаем экземпляры конфигурации
DB_CONFIG = DatabaseConfig()
API_CONFIG = APIConfig()