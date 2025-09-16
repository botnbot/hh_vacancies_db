"""
Вспомогательные утилиты для проекта hh_vacancies_db
"""
import textwrap
from typing import Any, Dict, List, Optional


def format_salary(salary: Optional[float]) -> str:
    """
    Форматирует зарплату для читаемого отображения

    Args:
        salary: Сумма зарплаты

    Returns:
        str: Отформатированная строка зарплаты
    """
    if salary is None or salary == 0:
        return "Не указана"

    return f"{salary:,.0f} руб.".replace(',', ' ')


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Обрезает текст до указанной длины и добавляет многоточие

    Args:
        text: Текст для обрезки
        max_length: Максимальная длина текста

    Returns:
        str: Обрезанный текст
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def paginate_items(items: List[Any], page: int, per_page: int = 10) -> tuple[List[Any], int, int]:
    """
    Разбивает список элементов на страницы

    Args:
        items: Список элементов
        page: Номер страницы (начинается с 1)
        per_page: Количество элементов на странице

    Returns:
        tuple: (элементы_страницы, всего_страниц, всего_элементов)
    """
    if not items:
        return [], 0, 0

    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)

    return items[start_idx:end_idx], total_pages, total_items


def safe_int_input(prompt: str, default: Optional[int] = None) -> Optional[int]:
    """
    Безопасный ввод целого числа с обработкой ошибок

    Args:
        prompt: Подсказка для ввода
        default: Значение по умолчанию

    Returns:
        int or None: Введенное число или None при ошибке
    """
    try:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        return int(value) if value else None
    except ValueError:
        print("Ошибка: введите целое число")
        return None


def safe_float_input(prompt: str, default: Optional[float] = None) -> Optional[float]:
    """
    Безопасный ввод числа с плавающей точкой с обработкой ошибок

    Args:
        prompt: Подсказка для ввода
        default: Значение по умолчанию

    Returns:
        float or None: Введенное число или None при ошибке
    """
    try:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        return float(value) if value else None
    except ValueError:
        print("Ошибка: введите число")
        return None


def confirm_action(prompt: str) -> bool:
    """
    Запрашивает подтверждение действия у пользователя

    Args:
        prompt: Вопрос для подтверждения

    Returns:
        bool: True если пользователь подтвердил, иначе False
    """
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ['y', 'yes', 'да', 'д']

def wrap_text(text: str, width: int = 120) -> str:
    """
    Переносит длинный текст на строки шириной width.
    """
    if not text:
        return ""
    return "\n".join(textwrap.wrap(text, width=width))