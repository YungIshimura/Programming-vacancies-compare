import requests
import os
from dotenv import load_dotenv
from terminaltables import DoubleTable


def predict_rub_salary_for_hh(programming_languages):
    params = {
    "area": hh_id_moscow,
    "period": 30,
    "per_page": 50, 
    "currency": "RUR"
    }      
    table_data = []

    for language in programming_languages:
        params["text"] = language
        params["page"] = 0
        hh_vacancies_page = 40
        average_salary_scroll = []

        while params["page"] < hh_vacancies_page:
            response = requests.get("https://api.hh.ru/vacancies", params=params)
            response.raise_for_status()
            hh_vacancies = response.json()
            hh_vacancies_page = hh_vacancies["pages"]

            for vacancies in range(len(hh_vacancies["items"])):
                salary = hh_vacancies["items"][vacancies]["salary"]
                if salary:
                    average_salary = predict_salary(salary["to"], salary["from"])
                    average_salary_scroll.append(average_salary)
            params["page"] += 1
        try:
            average_salaries = sum(average_salary_scroll) / len(average_salary_scroll)
            table_data.append(
                [
                    language,
                    hh_vacancies["found"],
                    len(average_salary_scroll),
                    int(average_salaries),
                ]
            )
        except ZeroDivisionError:
            continue

    return table_data


def predict_rub_salary_for_superjob(programming_languages, superjob_api_key):
    headers = {"X-Api-App-Id": superjob_api_key}
    params = {
        "t": sj_id_moscow,
        "catalogues": sj_profession_catalog_number,
        "period": 30,
        "page": 0,
        "count": 5,
    }
    table_data = [] 

    for language in programming_languages:
        params["keyword"] = language
        params["page"] = 0
        sj_more_pages = True
        average_salary_scroll = []

        while sj_more_pages:
            response = requests.get(
                "https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params
            )
            response.raise_for_status()
            sj_vacancies = response.json()
            sj_more_pages = sj_vacancies["more"]

            for vacancies in range(len(sj_vacancies["objects"])):
                salary = sj_vacancies["objects"][vacancies]
                average_salary = predict_salary(
                    salary["payment_from"], salary["payment_to"]
                )
                average_salary_scroll.append(average_salary)
            params["page"] += 1

        filtered_average_salary_scroll = filter(bool, average_salary_scroll)
        average_salary_scroll = list(filtered_average_salary_scroll)

        try:
            average_salaries = sum(average_salary_scroll) / len(average_salary_scroll)
            table_data.append(
                [
                    language,
                    sj_vacancies["total"],
                    len(average_salary_scroll),
                    int(average_salaries),
                ]
            )
        except ZeroDivisionError:
            continue
    return table_data


def predict_salary(salary_from, salary_to):
    if salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    elif not salary_from and not salary_to:
        pass
    else:
        (salary_to + salary_from) / 2


def print_table(table_data, title):
    table_headers = [
        ["language", "vacancies_found", "vacancies_processed", "average_salary"]
    ]
    table = table_headers[:]
    for vacancies in table_data:
        table.append(vacancies)
    table_instance = DoubleTable(table, title)
    table_instance.justify_columns[2] = "right"
    print(table_instance.table)


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    hh_id_moscow = "1"
    sj_id_moscow = "4"
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
    hh_table_data = predict_rub_salary_for_hh(
        programming_languages
    )
    sj_table_data = predict_rub_salary_for_superjob(
        programming_languages, superjob_api_key
    )
    print_table(hh_table_data, title="hh.ru Moscow")
    print_table(sj_table_data, title="SuperJob.ru Moscow")
