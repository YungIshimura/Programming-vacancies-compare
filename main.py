import os

import requests

from dotenv import load_dotenv
from terminaltables import DoubleTable


def predict_rub_salary_for_hh(programming_languages, city_id):
    table_lines = []
    for language in programming_languages:
        vacancies_stats = get_hh_vacancy_stats(
            language, city_id)
        table_lines.append([language, *vacancies_stats])

    return table_lines


def get_hh_vacancy_stats(language, city_id):
    params = {
        "area": city_id,
        "period": 30,
        "per_page": 50,
        "currency": "RUR",
        "text": language,
        "page": 0
    }

    vacancies_number_pages = 40
    average_salaries = []

    while params["page"] < vacancies_number_pages:
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        vacancies = response.json()
        vacancies_number_pages = vacancies["pages"]
        for salary in vacancies["items"]:
            if salary["salary"]:
                average_salary = predict_salary(
                    salary["salary"]["to"],
                    salary["salary"]["from"]
                )
                average_salaries.append(average_salary)
        params["page"] += 1
    try:
        average_salary = sum(average_salaries) / len(average_salaries)
    except ZeroDivisionError:
        average_salary = 0

    return vacancies["found"], len(average_salaries), int(average_salary)


def predict_rub_salary_for_superjob(
        programming_languages,
        token,
        city_id,
        profession_catalog_number):
    table_lines = []
    for language in programming_languages:
        vacancies_stats = get_sj_vacancies_stats(
            language,
            token,
            city_id,
            profession_catalog_number)
        table_lines.append([language, *vacancies_stats])

    return table_lines


def get_sj_vacancies_stats(language, token, city_id, proffesion_id):
    headers = {"X-Api-App-Id": token}
    params = {
        "t": city_id,
        "catalogues": proffesion_id,
        "period": 30,
        "page": 0,
        "count": 5,
        "keyword": language,
        "page": 0
    }

    more_pages = True
    average_salaries = []

    while more_pages:
        response = requests.get(
            "https://api.superjob.ru/2.0/vacancies/",
            headers=headers,
            params=params)
        response.raise_for_status()
        vacancies = response.json()
        more_pages = vacancies["more"]

        for salary in vacancies["objects"]:
            if salary["currency"] == "rub":
                average_salary = predict_salary(
                    salary["payment_from"], salary["payment_to"]
                )
                average_salaries.append(average_salary)
        params["page"] += 1

    filtered_average_salaries_scroll = filter(bool, average_salaries)
    average_salaries = list(filtered_average_salaries_scroll)
    try:
        average_salary = sum(average_salaries) / len(average_salaries)
    except ZeroDivisionError:
        average_salary = 0

    return vacancies["total"], len(average_salaries), int(average_salary)


def predict_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return salary_from * 1.2
    elif salary_to and not salary_from:
        return salary_to * 0.8
    elif salary_from and salary_to:
        return (salary_to + salary_from) / 2


def get_table(table_data, title):
    table_rows = [
        ["language",
         "vacancies_found",
         "vacancies_processed",
         "average_salary"]
    ]
    for vacancies in table_data:
        table_rows.append(vacancies)
    table = DoubleTable(table_rows, title)
    table.justify_columns[2] = "right"

    return table.table


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    hh_moscow_id = "1"
    sj_moscow_id = "4"
    sj_profession_catalog_number = "48"
    programming_languages = [
        "Python",
        "Java",
        "JavaScript",
        "C",
        "C++",
        "C#",
        "PHP",
        "Go",
    ]
    hh_table_stats = predict_rub_salary_for_hh(
        programming_languages, hh_moscow_id
    )
    sj_table_stats = predict_rub_salary_for_superjob(
        programming_languages,
        superjob_api_key,
        sj_moscow_id,
        sj_profession_catalog_number
    )
    hh_table = get_table(hh_table_stats, title="hh.ru Moscow")
    sj_table = get_table(sj_table_stats, title="SuperJob.ru Moscow")
    print(hh_table)
    print(sj_table)
