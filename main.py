import requests
import os
from dotenv import load_dotenv
from terminaltables import DoubleTable


def predict_rub_salary_for_hh(list_languages):
    hh_table_data = [
        ["language", "vacancies_found", "vacancies_processed", "average_salary"]
    ]
    for language in list_languages:
        params = {
            "text": language,
            "area": 1,
            "period": 30,
            "per_page": 50,
            "page": 0,
            "currency":"RUR"
        }

        hh_average_salary_list = []

        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        hh_vacancies = response.json()

        while params["page"] < hh_vacancies["pages"]:
            response = requests.get("https://api.hh.ru/vacancies", params=params)
            response.raise_for_status()
            hh_vacancies = response.json()
            for vacancies in range(len(hh_vacancies["items"])):
                salary = hh_vacancies["items"][vacancies]["salary"]
                if salary != None:
                    average_salary = predict_salary(salary["to"], salary["from"])
                    hh_average_salary_list.append(average_salary)
            params["page"] += 1
        average_salaries = sum(hh_average_salary_list) / len(hh_average_salary_list)
        hh_table_data.append(
            [language,hh_vacancies["found"],len(hh_average_salary_list),int(average_salaries)]
        )

    return hh_table_data


def predict_rub_salary_for_superjob(list_languages):
    sj_table_data = [
        ["language", "vacancies_found", "vacancies_processed", "average_salary"]
    ]
    for language in list_languages:
        headers = {"X-Api-App-Id": superjob_api_key}
        params = {
            "keyword": language,
            "t": 4,
            "catalogues": 48,
            "period": 30,
            "page": 0,
            "count": 5,
        }

        sj_average_salary_list = []

        response = requests.get("https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params)
        response.raise_for_status()
        sj_vacancies = response.json()

        while sj_vacancies["more"]:
            response = requests.get("https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params)
            response.raise_for_status()
            sj_vacancies = response.json()
            for vacancies in range(len(sj_vacancies["objects"])):
                salary = sj_vacancies["objects"][vacancies]
                average_salary = predict_salary(salary["payment_from"], salary["payment_to"])
                sj_average_salary_list.append(average_salary)
            params["page"] += 1
        filtered_sj_average_salary_list = filter(lambda num: num != 0, sj_average_salary_list)
        sj_average_salary_list = list(filtered_sj_average_salary_list)
        average_salaries = sum(sj_average_salary_list) / len(sj_average_salary_list)
        sj_table_data.append(
            [language,sj_vacancies["total"],len(sj_average_salary_list),int(average_salaries)]
        )

    return sj_table_data


def predict_salary(salary_from, salary_to):
    if salary_to == None:
        return salary_from * 1.2
    elif salary_from == None:
        return salary_to * 0.8
    else:
        return (salary_to+salary_from)/2


def print_table(hh_table_data, sj_table_data):
    title = "HH.ru Moscow"
    hh_table_instance = DoubleTable(hh_table_data, title)
    hh_table_instance.justify_columns[2] = "right"
    print(hh_table_instance.table)
    title = "SuperJob.ri Moscow"
    sj_table_instance = DoubleTable(sj_table_data, title)
    sj_table_instance.justify_columns[2] = "right"
    print(sj_table_instance.table)


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    list_languages = ["Python", "Java", "C", "C++", "JavaScript", "C#", "PHP", "Go"]
    hh_table_data = predict_rub_salary_for_hh(list_languages)
    sj_table_data = predict_rub_salary_for_superjob(list_languages)
    print_table(hh_table_data, sj_table_data)
