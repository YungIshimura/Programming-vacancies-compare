import os

import requests

from dotenv import load_dotenv
from terminaltables import DoubleTable


def predict_rub_salary_for_hh(programming_languages):
    hh_table_lines = []
    for language in programming_languages:
        hh_vacancies_table_rows = get_hh_vacancy_table_row(
            language)
        hh_table_lines.append([language, *hh_vacancies_table_rows])
        print(hh_table_lines)

    return hh_table_lines


def get_hh_vacancy_table_row(language):
    params = {
        "area": hh_moscow_id,
        "period": 30,
        "per_page": 50,
        "currency": "RUR"
    }
    params["text"] = language
    params["page"] = 0
    hh_vacancies_number_pages = 40
    average_salaries_scroll = []
    while params["page"] < hh_vacancies_number_pages:
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        hh_vacancies = response.json()
        hh_vacancies_number_pages = hh_vacancies["pages"]
        for salary in hh_vacancies['items']:
            if salary['salary']:
                average_salaries = predict_salary(
                    salary['salary']["to"],
                    salary['salary']["from"]
                )
                average_salaries_scroll.append(average_salaries)
        params["page"] += 1
    try:
        average_salary = sum(average_salaries_scroll) / len(average_salaries_scroll)
    except ZeroDivisionError:
        average_salary = 0

    return hh_vacancies["found"], len(average_salaries_scroll), int(average_salary)


def predict_rub_salary_for_superjob(programming_languages):
    sj_table_lines = []
    for language in programming_languages:
        sj_vacancies_table_rows = get_sj_vacancies_table_row(
            language, superjob_api_key,)
        sj_table_lines.append([language, *sj_vacancies_table_rows])
        print(sj_table_lines)
    return sj_table_lines


def get_sj_vacancies_table_row(language, token):
    headers = {"X-Api-App-Id": superjob_api_key}
    params = {
        "t": sj_moscow_id,
        "catalogues": sj_profession_catalog_number,
        "period": 30,
        "page": 0,
        "count": 5,
    }
    params["keyword"] = language
    params["page"] = 0
    sj_more_pages = True
    average_salaries_scroll = []

    while sj_more_pages:
        response = requests.get(
            "https://api.superjob.ru/2.0/vacancies/",
            headers=headers,
            params=params)
        response.raise_for_status()
        sj_vacancies = response.json()
        sj_more_pages = sj_vacancies["more"]

        for salary in sj_vacancies["objects"]:
            average_salaries = predict_salary(
                salary["payment_from"], salary["payment_to"]
            )
            average_salaries_scroll.append(average_salaries)
        params["page"] += 1

    filtered_average_salaries_scroll = filter(bool, average_salaries_scroll)
    average_salaries_scroll = list(filtered_average_salaries_scroll)
    try:
        average_salary = sum(average_salaries_scroll) / len(average_salaries_scroll)
    except ZeroDivisionError:
        average_salary = 0

    return sj_vacancies["total"], len(average_salaries_scroll), int(average_salary)


def predict_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return salary_from * 1.2
    elif salary_to and not salary_from:
        return salary_to * 0.8
    elif salary_from and salary_to:
        return (salary_to + salary_from) / 2


def get_table(table_data, title):
    table_rows = [
        ["language", "vacancies_found", "vacancies_processed", "average_salary"]
    ]
    for vacancies in table_data:
        table_rows.append(vacancies)
    table_instance = DoubleTable(table_rows, title)
    table_instance.justify_columns[2] = "right"

    return table_instance.table


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    hh_moscow_id = "1"
    sj_moscow_id = "4"
    sj_profession_catalog_number = "48"
    programming_languages = [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "C#",
        "PHP",
        "Go",
    ]
    hh_table_lines = predict_rub_salary_for_hh(
        programming_languages
    )
    sj_table_lines = predict_rub_salary_for_superjob(
        programming_languages
    )
    hh_table = get_table(hh_table_lines, title="hh.ru Moscow")
    sj_table = get_table(sj_table_lines, title="SuperJob.ru Moscow")
    print(hh_table)
    print(sj_table)
