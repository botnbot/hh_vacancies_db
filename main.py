"""
Основной модуль приложения - точка входа
"""

import sys
from src.database_creator import DatabaseCreator
from src.db_manager import DBManager
from src.hh_api import HHAPI
from src.config import DB_CONFIG
from utils.helpers import safe_int_input, safe_float_input, confirm_action
import psycopg2


def setup_database():
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
        return None


def fill_database_with_vacancies():
    """Заполняет базу данных вакансиями"""
    try:
        conn = get_db_connection()
        if not conn:
            return False

        hh_api = HHAPI()
        db_manager = DBManager(conn)

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

        # Сохраняем вакансии в БД
        success_count = 0
        for vacancy in vacancies:
            try:
                # Здесь будет логика сохранения вакансии в БД
                # (реализуем после создания методов в DBManager)
                success_count += 1
            except Exception as e:
                print(f"Ошибка сохранения вакансии: {e}")
                continue

        print(f"Успешно сохранено {success_count} вакансий")
        return True

    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        return False


def show_main_menu():
    """Отображает главное меню"""
    print("\n" + "=" * 50)
    print("СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ HH.RU")
    print("=" * 50)
    print("1. Компании и количество вакансий")
    print("2. Все вакансии")
    print("3. Средняя зарплата")
    print("4. Вакансии с высокой зарплатой")
    print("5. Поиск вакансий по ключевым словам")
    print("6. Вакансии по компании")
    print("7. Настройка базы данных")
    print("8. Заполнить базу вакансиями")
    print("0. Выход")
    print("=" * 50)


def main():
    """Основная функция программы"""
    print("Запуск системы управления вакансиями...")

    conn = None
    try:
        # Проверяем подключение к БД
        conn = get_db_connection()
        if not conn:
            if confirm_action("База данных не настроена. Настроить сейчас?"):
                if setup_database():
                    conn = get_db_connection()
                else:
                    print("Не удалось настроить базу данных. Завершение работы.")
                    return
            else:
                print("Работа невозможна без базы данных. Завершение работы.")
                return

        db_manager = DBManager(conn)

        while True:
            show_main_menu()
            choice = input("Выберите действие (0-8): ").strip()

            if choice == "0":
                print("До свидания!")
                break

            elif choice == "1":
                # Получить компании и количество вакансий
                pass

            elif choice == "2":
                # Получить все вакансии
                pass

            elif choice == "3":
                # Получить среднюю зарплату
                pass

            elif choice == "4":
                # Вакансии с высокой зарплатой
                pass

            elif choice == "5":
                # Поиск по ключевым словам
                pass

            elif choice == "6":
                # Вакансии по компании
                pass

            elif choice == "7":
                if confirm_action("Пересоздать базу данных? Все данные будут удалены."):
                    setup_database()
                    conn = get_db_connection()
                    if conn:
                        db_manager = DBManager(conn)

            elif choice == "8":
                fill_database_with_vacancies()

            else:
                print("Неверный выбор. Попробуйте снова.")

    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()