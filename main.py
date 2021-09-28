import requests
import os
from dotenv import load_dotenv
from terminaltables import DoubleTable


def predict_rub_salary_for_hh(programming_languages,average_salary_scroll):
    for language in programming_languages:
        params = {
            "text": language,
            "area": hh_id_moscow,
            "period": 30,
            "per_page": 50,
            "page": 0,
            "currency": "RUR"
        }

        average_salary_scroll = []

        hh_vacancies_page = 40

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
        except ZeroDivisionError:
            continue
        print_table(language, hh_vacancies["found"], len(average_salary_scroll), int(average_salaries),hh_table_data,title = "hh.ru Moscow")


def predict_rub_salary_for_superjob(programming_languages,superjob_api_key,average_salary_scroll):
    for language in programming_languages:
        headers = {"X-Api-App-Id": superjob_api_key}
        params = {
            "keyword": language,
            "t": sj_id_moscow,
            "catalogues": sj_profession_catalog_number,
            "period": 30,
            "page": 0,
            "count": 5,
        }

        average_salary_scroll = []

        sj_more_pages = True

        while sj_more_pages:
            response = requests.get("https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params)
            response.raise_for_status()
            sj_vacancies = response.json()
            sj_more_pages = sj_vacancies["more"]

            for vacancies in range(len(sj_vacancies["objects"])):
                salary = sj_vacancies["objects"][vacancies]
                average_salary = predict_salary(salary["payment_from"], salary["payment_to"])
                average_salary_scroll.append(average_salary)
            params["page"] += 1

        filtered_average_salary_scroll = filter(bool, average_salary_scroll)
        average_salary_scroll = list(filtered_average_salary_scroll)
        
        try:
            average_salaries = sum(average_salary_scroll) / len(average_salary_scroll)
        except ZeroDivisionError:
            continue
        print_table(language, sj_vacancies["total"], len(average_salary_scroll), int(average_salaries),sj_table_data,title="SuperJob.ru Moscow")


def predict_salary(salary_from, salary_to):
    if salary_from:
        return salary_from*1.2
    elif salary_to:
        return salary_to*0.8
    elif not salary_from and not salary_to:
        pass
    else:
        return (salary_to + salary_from) / 2


def print_table(language,total_vacancies,average_salary_scroll,average_salaries,table_data, title):
    table_data.append(
            [language, total_vacancies, average_salary_scroll, average_salaries]
        )

    if len(table_data)==9:
        table_instance = DoubleTable(table_data, title)
        table_instance.justify_columns[2] = "right"
        print(table_instance.table)
            


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    average_salary_scroll = []
    hh_id_moscow = "1"
    sj_id_moscow = "4"
    sj_profession_catalog_number = "48"
    table_headers = [
        ["language", "vacancies_found", "vacancies_processed", "average_salary"]
    ]
    hh_table_data = table_headers[:]
    sj_table_data = table_headers[:]
    programming_languages = [
     "Python",
     "Java",
     "C", 
     "C++", 
     "JavaScript",
     "C#",
     "PHP",
     "Go"]
    hh_table_data = predict_rub_salary_for_hh(programming_languages,average_salary_scroll)
    sj_table_data = predict_rub_salary_for_superjob(programming_languages,superjob_api_key,average_salary_scroll)
    