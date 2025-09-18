"""
Основной модуль приложения - точка входа
"""

import sys
import os
import psycopg2

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from database_creator import DatabaseCreator
    from db_manager import DBManager
    from hh_api import HHAPI
    from config import DB_CONFIG
    from utils.helpers import safe_int_input, safe_float_input, confirm_action, paginate_items, format_salary
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Проверьте структуру проекта:")
    print("1. Папка src/ должна содержать: database_creator.py, db_manager.py, hh_api.py")
    print("2. Папка src/utils/ должна содержать: helpers.py")
    print("3. Файл config.py должен быть в корне проекта")
    print("Текущий sys.path:")
    for path in sys.path:
        print(f"  - {path}")
    sys.exit(1)


def setup_database() -> bool:
    """Создает и настраивает базу данных"""
    creator = DatabaseCreator()
    if creator.setup_database():
        print("База данных создана и настроена")
        return True
    else:
        print("Ошибка настройки базы данных")
        return False


def get_db_connection():
    """Устанавливает соединение с базой данных"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG.host,
            database=DB_CONFIG.name,
            user=DB_CONFIG.user,
            password=DB_CONFIG.password,
            port=DB_CONFIG.port
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        print("Проверьте:")
        print("1. Запущен ли PostgreSQL")
        print("2. Правильность пароля в config.py")
        print("3. Существование БД: createdb -U postgres hh_vacancies")
        return None


def check_tables_exist(db_manager: DBManager) -> bool:
    """Проверяет существование таблиц в базе данных"""
    try:
        if not db_manager.check_tables_exist():
            print("Таблицы не созданы. Сначала выберите пункт 7 для настройки БД.")
            return False
        return True
    except Exception as e:
        print(f"Ошибка проверки таблиц: {e}")
        return False

def fill_database_with_vacancies(db_manager: DBManager) -> bool:
    """Заполняет базу данных вакансиями"""
    if not check_tables_exist(db_manager):
        return False

    try:
        hh_api = HHAPI()

        keyword = input("Введите ключевое слово для поиска вакансий: ").strip()
        if not keyword:
            print("Не указано ключевое слово")
            return False

        per_page = safe_int_input("Количество вакансий на странице (по умолчанию 20): ", 20)
        max_pages = safe_int_input("Максимальное количество страниц (по умолчанию 5): ", 5)

        print(f"Поиск вакансий по запросу: '{keyword}'...")
        vacancies = hh_api.get_vacancies(keyword, per_page=per_page, max_pages=max_pages)

        if not vacancies:
            print("Вакансий не найдено")
            return False

        print(f"Найдено {len(vacancies)} вакансий")

        saved_count = db_manager.save_vacancies(vacancies)
        print(f"Сохранено {saved_count} вакансий в базу данных")

        return saved_count > 0

    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        return False


def show_companies_and_vacancies(db_manager: DBManager) -> None:
    """Показывает компании и количество вакансий"""
    page = 1
    per_page = 10

    while True:
        companies = db_manager.get_companies_and_vacancies_count(limit=per_page, offset=(page-1)*per_page)

        if not companies:
            print("Компаний не найдено")
            break

        print(f"\nСтраница {page}:")
        print("-" * 50)
        for i, company in enumerate(companies, 1):
            print(f"{i}. {company['company_name']}: {company['vacancy_count']} вакансий")

        total_companies = db_manager.get_total_count('companies')
        total_pages = max(1, (total_companies + per_page - 1) // per_page)

        print(f"\nСтраница {page} из {total_pages}")
        print("n - следующая страница, p - предыдущая, b - назад")

        action = input("Выберите действие: ").lower().strip()

        if action == 'n' and page < total_pages:
            page += 1
        elif action == 'p' and page > 1:
            page -= 1
        elif action == 'b':
            break
        else:
            print("Неверное действие")


def show_all_vacancies(db_manager: DBManager) -> None:
    """Показывает все вакансии"""
    page = 1
    per_page = 10

    while True:
        vacancies = db_manager.get_all_vacancies(limit=per_page, offset=(page-1)*per_page)

        if not vacancies:
            print("Вакансий не найдено")
            break

        print(f"\nСтраница {page}:")
        print("-" * 80)
        for i, vac in enumerate(vacancies, 1):
            salary = format_salary(vac['salary'])
            print(f"{i}. {vac['company_name']} - {vac['vacancy_name']}")
            print(f"   Зарплата: {salary}")
            print(f"   {vac['url']}")
            print()

        total_vacancies = db_manager.get_total_count('vacancies')
        total_pages = max(1, (total_vacancies + per_page - 1) // per_page)

        print(f"Страница {page} из {total_pages}")
        print("n - следующая страница, p - предыдущая, b - назад")

        action = input("Выберите действие: ").lower().strip()

        if action == 'n' and page < total_pages:
            page += 1
        elif action == 'p' and page > 1:
            page -= 1
        elif action == 'b':
            break
        else:
            print("Неверное действие")


def show_avg_salary(db_manager: DBManager) -> None:
    """Показывает среднюю зарплату"""
    avg_salary = db_manager.get_avg_salary()
    if avg_salary is not None:
        print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f} руб.")
    else:
        print("\nНе удалось рассчитать среднюю зарплату")


def show_high_salary_vacancies(db_manager: DBManager) -> None:
    """Показывает вакансии с зарплатой выше средней"""
    vacancies = db_manager.get_vacancies_with_higher_salary(limit=20)

    if not vacancies:
        print("Вакансий с высокой зарплатой не найдено")
        return

    print(f"\nВакансии с зарплатой выше средней:")
    print("-" * 80)
    for i, vac in enumerate(vacancies, 1):
        salary = format_salary(vac['salary'])
        print(f"{i}. {vac['company_name']} - {vac['vacancy_name']}")
        print(f"   Зарплата: {salary}")
        print(f"   {vac['url']}")
        print()


def search_vacancies_by_keyword(db_manager: DBManager) -> None:
    """Поиск вакансий по ключевым словам"""
    keyword = input("Введите ключевые слова для поиска: ").strip()
    if not keyword:
        print("Не указаны ключевые слова")
        return

    company_filter = input("Фильтр по компании (оставьте пустым если не нужно): ").strip()
    min_salary = safe_float_input("Минимальная зарплата (оставьте пустым если не нужно): ")
    max_salary = safe_float_input("Максимальная зарплата (оставьте пустым если не нужно): ")

    vacancies = db_manager.get_vacancies_with_keyword(
        keyword=keyword,
        company_name=company_filter or "",
        min_salary=min_salary,
        max_salary=max_salary,
        limit=50
    )

    if not vacancies:
        print("Вакансий не найдено")
        return

    print(f"\nНайдено {len(vacancies)} вакансий:")
    print("-" * 80)
    for i, vac in enumerate(vacancies, 1):
        salary = format_salary(vac['salary'])
        remote = "Удаленная работа" if vac['remote'] else "На территории работодателя"
        print(f"{i}. {vac['company_name']} - {vac['vacancy_name']}")
        print(f"   {salary} | {remote}")
        print(f"   {vac['experience']}")
        print(f"   {vac['url']}")
        print()


def show_vacancies_by_company(db_manager: DBManager) -> None:
    """Показывает все вакансии  компании"""
    company_name = input("Введите название компании: ").strip()
    if not company_name:
        print("Не указано название компании")
        return

    vacancies = db_manager.get_vacancies_by_company(company_name, limit=50)

    if not vacancies:
        print("Вакансий не найдено")
        return

    print(f"\nВакансии компании '{company_name}':")
    print("-" * 80)
    for i, vac in enumerate(vacancies, 1):
        salary = format_salary(vac['salary'])
        if vac['remote'] : remote = "Удаленная"
        print(f"{i}. {vac['vacancy_name']}")
        print(f"   {salary} | {remote}")
        print(f"   {vac['experience']}")
        print(f"   {vac['url']}")
        print()


def show_main_menu() -> None:
    """Отображает главное меню"""
    print("\n" + "=" * 50)
    print("СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ HH.RU")
    print("=" * 50)
    print("1. Компании и количество вакансий")
    print("2. Все вакансии")
    print("3. Средняя зарплата")
    print("4. Вакансии с  зарплатой выше средней")
    print("5. Поиск вакансий по ключевым словам")
    print("6. Вакансии по компании")
    print("7. Настройка базы данных")
    print("8. Заполнить базу вакансиями")
    print("0. Выход")
    print("=" * 50)


def main() -> None:
    """Основная функция программы"""
    print("Запуск системы управления вакансиями...")

    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("Не удалось подключиться к БД. Завершение работы.")
            return

        db_manager = DBManager(conn)

        while True:
            show_main_menu()
            choice = input("Выберите действие (0-8): ").strip()

            if choice == "0":
                print("До свидания!")
                break

            elif choice == "1":
                if not check_tables_exist(db_manager):
                    continue
                show_companies_and_vacancies(db_manager)

            elif choice == "2":
                if not check_tables_exist(db_manager):
                    continue
                show_all_vacancies(db_manager)

            elif choice == "3":
                if not check_tables_exist(db_manager):
                    continue
                show_avg_salary(db_manager)

            elif choice == "4":
                if not check_tables_exist(db_manager):
                    continue
                show_high_salary_vacancies(db_manager)

            elif choice == "5":
                if not check_tables_exist(db_manager):
                    continue
                search_vacancies_by_keyword(db_manager)

            elif choice == "6":
                if not check_tables_exist(db_manager):
                    continue
                show_vacancies_by_company(db_manager)

            elif choice == "7":
                if confirm_action("Пересоздать базу данных? Все данные будут удалены."):
                    if setup_database():
                        if conn:
                            conn.close()
                        conn = get_db_connection()
                        if conn:
                            db_manager = DBManager(conn)

            elif choice == "8":
                fill_database_with_vacancies(db_manager)

            else:
                print("Неверный выбор. Попробуйте снова.")

    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Соединение с БД закрыто")


if __name__ == "__main__":
    main()