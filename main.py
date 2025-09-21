from typing import Optional

import psycopg2
from psycopg2.extensions import connection

from config import DB_CONFIG
from src.company import Company
from src.data_filler import DataFiller
from src.database_creator import DatabaseCreator
from src.db_manager import DBManager
from src.vacancy import Vacancy
from utils.helpers import confirm_action, safe_int_input


def get_db_connection() -> Optional[connection]:
    """Устанавливает соединение с базой данных"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG.host,
            database=DB_CONFIG.name,
            user=DB_CONFIG.user,
            password=DB_CONFIG.password,
            port=DB_CONFIG.port,
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        print("\nПроверьте:")
        print("1. Запущен ли PostgreSQL")
        print("2. Правильность пароля в config.py")
        print(f"3. Существование БД: createdb -U {DB_CONFIG.user} {DB_CONFIG.name}")
        return None


def show_companies(db_manager: DBManager) -> None:
    """Показывает список компаний и количество вакансий"""
    results = db_manager.get_companies_and_vacancies_count()
    print("\nКомпании и количество вакансий:")
    print("-" * 80)
    for company in results:
        print(
            f"{company.get('company_name_real', company.get('company_name', 'Не указано'))}: {company['vacancy_count']}"
        )
    print()


def show_all_vacancies(db_manager: DBManager) -> None:
    """Показывает все вакансии с форматированием класса Vacancy"""
    results = db_manager.get_all_vacancies()
    vacancies = [
        Vacancy.from_dict(
            {
                "title": vac_data.get("vacancy_name", "Без названия"),
                "url": vac_data.get("url", ""),
                "description": vac_data.get("requirements", "Описание отсутствует"),
                "salary_range": (vac_data.get("salary") or 0, vac_data.get("salary") or 0),
                "experience": vac_data.get("experience", "не указан"),
                "remote": vac_data.get("remote", False),
                "company_name": vac_data.get("company_name_real") or vac_data.get("company_name", "Не указано"),
            }
        )
        for vac_data in results
    ]
    vacancies.sort(reverse=True)

    print("\nСписок вакансий (сортировка по зарплате):")
    print("-" * 80)
    for vacancy in vacancies:
        print(vacancy)
    print()


def show_avg_salary(db_manager: DBManager) -> None:
    """Показывает среднюю зарплату по вакансиям"""
    avg_salary = db_manager.get_avg_salary()
    print(f"\nСредняя зарплата: {avg_salary:.2f}\n")


def show_high_salary_vacancies(db_manager: DBManager) -> None:
    """Показывает вакансии с зарплатой выше средней"""
    results = db_manager.get_vacancies_with_higher_salary()
    vacancies = [
        Vacancy.from_dict(
            {
                "title": vac_data.get("vacancy_name", "Без названия"),
                "url": vac_data.get("url", ""),
                "description": vac_data.get("requirements", "Описание отсутствует"),
                "salary_range": (vac_data.get("salary") or 0, vac_data.get("salary") or 0),
                "experience": vac_data.get("experience", "не указан"),
                "remote": vac_data.get("remote", False),
                "company_name": vac_data.get("company_name_real") or vac_data.get("company_name", "Не указано"),
            }
        )
        for vac_data in results
    ]
    vacancies.sort(reverse=True)

    print("\nВакансии с зарплатой выше средней (сортировка по зарплате):")
    print("-" * 80)
    for vacancy in vacancies:
        print(vacancy)
    print()


def search_vacancies(db_manager: DBManager) -> None:
    """Поиск вакансий по ключевым словам"""
    keyword = input("Введите ключевое слово для поиска: ").strip()
    results = db_manager.get_vacancies_with_keyword(keyword)
    vacancies = [
        Vacancy.from_dict(
            {
                "title": vac_data.get("vacancy_name", "Без названия"),
                "url": vac_data.get("url", ""),
                "description": vac_data.get("requirements", "Описание отсутствует"),
                "salary_range": (vac_data.get("salary") or 0, vac_data.get("salary") or 0),
                "experience": vac_data.get("experience", "не указан"),
                "remote": vac_data.get("remote", False),
                "company_name": vac_data.get("company_name_real") or vac_data.get("company_name", "Не указано"),
            }
        )
        for vac_data in results
    ]
    vacancies.sort(reverse=True)

    print(f"\nВакансии по запросу '{keyword}' (сортировка по зарплате):")
    print("-" * 80)
    for vacancy in vacancies:
        print(vacancy)
    print()


def show_vacancies_by_company(db_manager: DBManager) -> None:
    """Показывает вакансии  конкретной компании"""
    company_name = input("Введите название компании: ").strip()
    results = db_manager.get_vacancies_by_company(company_name)
    print(f"\nВакансии компании '{company_name}':")
    print("-" * 80)
    for vac in results:
        vacancy = Vacancy.from_dict(
            {
                "title": vac.get("vacancy_name", "Без названия"),
                "url": vac.get("url", ""),
                "description": vac.get("requirements", "Описание отсутствует"),
                "salary_range": (vac.get("salary") or 0, vac.get("salary") or 0),
                "experience": vac.get("experience", "не указан"),
                "remote": vac.get("remote", False),
                "company_name": vac.get("company_name_real") or vac.get("company_name", company_name),
            }
        )
        print(vacancy)
    print()


def main() -> None:
    """Основная функция программы"""
    print("Запуск системы управления вакансиями...")

    while True:
        print("=" * 50)
        print("СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ HH.RU")
        print("=" * 50)
        print("1. Компании и количество вакансий компании")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с  зарплатой выше средней")
        print("5. Поиск вакансий по ключевым словам")
        print("6. Вакансии компании")
        print("7. Настройка базы данных")
        print("8. Заполнить базу вакансиями (предустановленные компании)")
        print("9. Ввести до 10 компаний для заполнения базы")
        print("0. Выход")
        print("=" * 50)

        choice = safe_int_input("Выберите действие (0-9): ", 0, 9)

        if choice == 0:
            print("Выход из программы")
            break

        if choice == 7:
            db_creator = DatabaseCreator()
            if confirm_action("Пересоздать базу данных? Все данные будут удалены."):
                db_creator.setup_database()
            continue

        conn = get_db_connection()
        if not conn:
            print("Не удалось подключиться к БД. Завершение работы.")
            break
        db_manager = DBManager(conn)

        if choice == 1:
            show_companies(db_manager)
        elif choice == 2:
            show_all_vacancies(db_manager)
        elif choice == 3:
            show_avg_salary(db_manager)
        elif choice == 4:
            show_high_salary_vacancies(db_manager)
        elif choice == 5:
            search_vacancies(db_manager)
        elif choice == 6:
            show_vacancies_by_company(db_manager)
        elif choice == 8:
            filler = DataFiller()
            # Предустановленные компании
            companies = [
                Company("Яндекс", "1740"),
                Company("Сбер", "3529"),
                Company("Тинькофф", "78638"),
            ]
            filler.fill_vacancies(companies)
        elif choice == 9:
            user_companies = []
            print("Введите названия компаний (до 10), оставьте пустое поле для завершения ввода:")
            while len(user_companies) < 10:
                name = input(f"Компания {len(user_companies)+1}: ").strip()
                if not name:
                    break
                company_obj = Company(name)
                user_companies.append(company_obj)

            if not user_companies:
                print("Компании не введены, отмена заполнения.")
            else:
                filler = DataFiller()
                filler.fill_vacancies(user_companies)

        conn.close()


if __name__ == "__main__":
    main()
