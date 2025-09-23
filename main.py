import sys
import textwrap
from src.db_manager import DBManager
from src.database_creator import DatabaseCreator
from src.data_filler import DataFiller
from src.hh_api import HeadHunterAPI
from src.company import Company

creator = DatabaseCreator()
creator.ensure_database()
db_manager = DBManager()

def print_menu():
    print("=" * 50)
    print("СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ HH.RU")
    print("=" * 50)
    print("1. Компании и количество вакансий компании")
    print("2. Все вакансии")
    print("3. Средняя зарплата")
    print("4. Вакансии с зарплатой выше средней")
    print("5. Поиск вакансий по ключевым словам")
    print("6. Вакансии компании")
    print("7. Настройка базы данных")
    print("8. Заполнить базу вакансиями (предустановленные компании)")
    print("9. Ввести до 10 компаний для заполнения базы")
    print("10. Настроить количество вакансий на страницу")
    print("0. Выход")
    print("=" * 50)

def print_paginated(results, title="Результаты", width=80):
    """Выводит данные постранично с переносом текста и сортировкой по зарплате."""
    if not results:
        print("Нет данных для отображения.")
        return

    def avg_salary(vac):
        frm = vac.get("salary_from") or 0
        to = vac.get("salary_to") or 0
        return (frm + to) / 2

    # Сортируем вакансии по убыванию средней зарплаты
    results = sorted(results, key=avg_salary, reverse=True)

    page_size = 10
    total = len(results)
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        chunk = results[start:end]

        print(f"\n{title} (страница {page + 1})")
        print("=" * 50)
        for row in chunk:
            print(f"Название вакансии : {row.get('vacancy_name')}")
            print(f"Компания         : {row.get('company_name_real')}")
            print(f"Опыт работы      : {row.get('experience')}")
            print(f"Удалённая работа : {row.get('remote')}")
            salary_from = row.get('salary_from')
            salary_to = row.get('salary_to')
            if salary_from or salary_to:
                print(f"Зарплата         : {salary_from or 0} — {salary_to or 0}")
            else:
                print("Зарплата         : не указана")
            print(f"Ссылка           : {row.get('url')}")
            print("Требования:")
            requirements = row.get('requirements') or ""
            for line in textwrap.wrap(requirements, width=width):
                print(f"  {line}")
            print("-" * 50)

        print(f"Показано {start + 1}-{min(end, total)} из {total}")
        cmd = input("Enter=далее, p=назад, q=выход: ").lower()
        if cmd == "q":
            break
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "" and end < total:
            page += 1
        else:
            break

def print_paginated_companies(results, page_size=10):
    page = 0
    while True:
        start = page * page_size
        end = start + page_size
        page_results = results[start:end]

        if not page_results:
            break

        print(f"\nКомпании и количество вакансий (страница {page + 1})")
        print("=" * 50)
        for row in page_results:
            company_name = row.get("company_name_real")
            vacancies_count = row.get("vacancy_count")
            print(f"Компания : {company_name}")
            print(f"Вакансий : {vacancies_count}")
            print("-" * 50)

        print(f"Показано {start + 1}-{min(end, len(results))} из {len(results)}")
        choice = input("Enter=далее, p=назад, q=выход: ")
        if choice.lower() == "q":
            break
        elif choice.lower() == "p" and page > 0:
            page -= 1
        else:
            page += 1



def show_companies(db_manager: DBManager):
    results = db_manager.get_companies_and_vacancies_count()
    print_paginated(results, "Компании и количество вакансий")

def show_all_vacancies(db_manager: DBManager):
    results = db_manager.get_all_vacancies()
    print_paginated(results, "Все вакансии")

def show_avg_salary(db_manager: DBManager):
    avg = db_manager.get_avg_salary()
    print(f"Средняя зарплата по всем вакансиям: {avg:.2f}" if avg else "Данные о зарплатах отсутствуют.")

def show_vacancies_higher_salary(db_manager: DBManager):
    results = db_manager.get_vacancies_with_higher_salary()
    print_paginated(results, "Вакансии с зарплатой выше средней")

def search_vacancies(db_manager: DBManager):
    keyword = input("Введите ключевое слово для поиска: ")
    results = db_manager.get_vacancies_with_keyword(keyword)
    print_paginated(results, f"Вакансии по ключевому слову '{keyword}'")

def show_vacancies_by_company(db_manager: DBManager):
    company_name = input("Введите название компании: ")
    results = db_manager.get_vacancies_by_company(company_name)
    print_paginated(results, f"Вакансии компании '{company_name}'")

def setup_database():
    confirm = input("Пересоздать базу данных? Все данные будут удалены. (y/n): ")
    if confirm.lower() in ("y", "yes", "д", "да"):
        creator.setup_database()

def fill_predefined():
    companies_data = [
        ("Яндекс", None),
        ("Ozon", None),
        ("Авито", None),
        ("Сбер", None),
        ("VK", None),
        ("Тинькофф", None)
    ]
    companies = [Company(name, company_id) for name, company_id in companies_data]
    filler = DataFiller()
    filler.fill_vacancies(companies)

def fill_custom():
    companies = []
    print("Введите до 10 компаний для поиска (пустая строка завершает ввод):")
    for _ in range(10):
        name = input("Компания: ")
        if not name.strip():
            break
        companies.append(Company(name.strip()))
    if companies:
        filler = DataFiller()
        filler.fill_vacancies(companies)

def set_page_size():
    try:
        size = int(input("Введите количество вакансий на страницу: "))
        if size > 0:
            print(f"Размер страницы установлен: {size}")
            return size
    except ValueError:
        print("Ошибка: нужно ввести число.")
    return 10

def main():
    db_manager = DBManager()
    page_size = 10

    while True:
        print_menu()
        choice = input("Выберите действие (0-10): ")

        if choice == "1":
            results = db_manager.get_companies_and_vacancies_count()
            print_paginated_companies(results)
        elif choice == "2":
            show_all_vacancies(db_manager)

        elif choice == "3":
            show_avg_salary(db_manager)
        elif choice == "4":
            show_vacancies_higher_salary(db_manager)
        elif choice == "5":
            search_vacancies(db_manager)
        elif choice == "6":
            show_vacancies_by_company(db_manager)
        elif choice == "7":
            setup_database()
        elif choice == "8":
            fill_predefined()
        elif choice == "9":
            fill_custom()
        elif choice == "10":
            page_size = set_page_size()
        elif choice == "0":
            print("Выход...")
            sys.exit(0)
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
