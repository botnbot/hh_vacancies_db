import sys
from src.database.database_creator import DatabaseCreator
from src.database.db_manager import DBManager
from src.api.hh_api import HHAPI
from src.utils.data_filler import DataFiller
import psycopg2


def setup_database():
    """Создает и настраивает базу данных"""
    creator = DatabaseCreator()
    creator.create_database()
    creator.create_tables()
    print("База данных создана и настроена")


def fill_database():
    """Заполняет базу данных вакансиями"""
    filler = DataFiller()
    companies = input("Введите названия компаний через запятую: ").split(',')
    companies = [name.strip() for name in companies if name.strip()]

    if not companies:
        print("Не указаны компании")
        return

    filler.fill_vacancies(companies)
    print("База данных заполнена вакансиями")


def show_menu():
    """Отображает главное меню"""
    print("\n" + "=" * 50)
    print("СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ")
    print("=" * 50)
    print("1. Компании и количество вакансий")
    print("2. Все вакансии")
    print("3. Средняя зарплата")
    print("4. Вакансии с высокой зарплатой")
    print("5. Поиск вакансий по ключевым словам")
    print("6. Вакансии по компании")
    print("7. Настройки базы данных")
    print("0. Выход")
    print("=" * 50)


def get_db_connection():
    """Устанавливает соединение с базой данных"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="vacancies_db",
            user="postgres",
            password="password"
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None


def main():
    """Основная функция программы"""
    print("Запуск системы управления вакансиями...")

    # Настройка базы данных
    setup_database()

    # Заполнение данными
    fill_database()

    # Основной цикл программы
    conn = get_db_connection()
    if not conn:
        return

    db_manager = DBManager(conn)

    while True:
        show_menu()
        choice = input("Выберите действие (0-7): ").strip()

        if choice == "0":
            print("До свидания!")
            break

        elif choice == "1":
            page = 1
            while True:
                companies = db_manager.get_companies_and_vacancies_count(limit=10, offset=(page - 1) * 10)
                if not companies:
                    print("Компаний не найдено")
                    break

                print(f"\nСтраница {page}:")
                for i, company in enumerate(companies, 1):
                    print(f"{i}. {company['company_name']}: {company['vacancy_count']} вакансий")

                action = input("\nСледующая страница (n), Предыдущая (p), Назад (b): ").lower()
                if action == 'n':
                    page += 1
                elif action == 'p' and page > 1:
                    page -= 1
                elif action == 'b':
                    break

        elif choice == "2":
            page = 1
            while True:
                vacancies = db_manager.get_all_vacancies(limit=10, offset=(page - 1) * 10)
                if not vacancies:
                    print("Вакансий не найдено")
                    break

                print(f"\nСтраница {page}:")
                for i, vacancy in enumerate(vacancies, 1):
                    salary = vacancy['salary'] or "Не указана"
                    print(f"{i}. {vacancy['company_name']} - {vacancy['vacancy_name']}")
                    print(f"   Зарплата: {salary}")
                    print(f"   Ссылка: {vacancy['url']}")
                    print()

                action = input("Следующая страница (n), Предыдущая (p), Назад (b): ").lower()
                if action == 'n':
                    page += 1
                elif action == 'p' and page > 1:
                    page -= 1
                elif action == 'b':
                    break

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата: {avg_salary:.2f} руб.")

        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary(limit=20)
            if not vacancies:
                print("Вакансий с высокой зарплатой не найдено")
            else:
                print("\nВакансии с зарплатой выше средней:")
                for i, vacancy in enumerate(vacancies, 1):
                    print(f"{i}. {vacancy['company_name']} - {vacancy['vacancy_name']}")
                    print(f"   Зарплата: {vacancy['salary']} руб.")
                    print(f"   Ссылка: {vacancy['url']}")
                    print()

        elif choice == "5":
            keyword = input("Введите ключевые слова для поиска: ").strip()
            if not keyword:
                print("Не указаны ключевые слова")
                continue

            company_filter = input("Фильтр по компании (оставьте пустым если не нужно): ").strip()
            min_salary = input("Минимальная зарплата (оставьте пустым если не нужно): ").strip()
            max_salary = input("Максимальная зарплата (оставьте пустым если не нужно): ").strip()

            min_salary = float(min_salary) if min_salary else None
            max_salary = float(max_salary) if max_salary else None

            vacancies = db_manager.get_vacancies_with_keyword(
                keyword=keyword,
                company_name=company_filter or "",
                min_salary=min_salary,
                max_salary=max_salary,
                limit=50
            )

            if not vacancies:
                print("Вакансий не найдено")
            else:
                print(f"\nНайдено {len(vacancies)} вакансий:")
                for i, vacancy in enumerate(vacancies, 1):
                    salary = vacancy['salary'] or "Не указана"
                    remote = "Удаленная работа" if vacancy['remote'] else "Офисная работа"
                    print(f"{i}. {vacancy['company_name']} - {vacancy['vacancy_name']}")
                    print(f"   Зарплата: {salary} руб.")
                    print(f"   Тип работы: {remote}")
                    print(f"   Ссылка: {vacancy['url']}")
                    print()

        elif choice == "6":
            company_name = input("Введите название компании: ").strip()
            if not company_name:
                print("Не указано название компании")
                continue

            vacancies = db_manager.get_vacancies_by_company(company_name, limit=50)
            if not vacancies:
                print("Вакансий не найдено")
            else:
                print(f"\nВакансии компании '{company_name}':")
                for i, vacancy in enumerate(vacancies, 1):
                    salary = vacancy['salary'] or "Не указана"
                    print(f"{i}. {vacancy['vacancy_name']}")
                    print(f"   Зарплата: {salary} руб.")
                    print(f"   Обновлено: {vacancy['last_updated']}")
                    print(f"   Ссылка: {vacancy['url']}")
                    print()

        elif choice == "7":
            print("\nНастройки базы данных:")
            print("1. Пересоздать базу данных")
            print("2. Заполнить данными заново")
            print("3. Назад")

            sub_choice = input("Выберите действие: ").strip()
            if sub_choice == "1":
                setup_database()
            elif sub_choice == "2":
                fill_database()

        else:
            print("Неверный выбор. Попробуйте снова.")

    conn.close()


if __name__ == "__main__":
    main()