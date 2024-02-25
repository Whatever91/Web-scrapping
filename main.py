import json
import re

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


BASE_URL = "https://spb.hh.ru/search/vacancy"

vacations_dict = {}

def get_vacations(params: dict, city_list: list) -> None:
    for elem in city_list:
        area = {"area": elem}
        params.update(area)
        headers_gen = Headers(os="Windows", browser="chrome")

        main_page = requests.get(BASE_URL, params=params, headers=headers_gen.generate()).text
        main_soup = BeautifulSoup(main_page, "lxml")
        all_vacations = main_soup.find_all("div", class_="serp-item")

        for vacation in all_vacations:
            vacation_link = vacation.find("a", class_="serp-item__title")["href"]

            vacation_page = requests.get(vacation_link, headers=headers_gen.generate()).text
            vacation_page_soup = BeautifulSoup(vacation_page, "lxml")

            vacation_desc = vacation_page_soup.find("div", class_="g-user-content").text

            if "Django" in vacation_desc or "Flask" in vacation_desc:
                vacation_name = vacation.find("h3", class_="bloko-header-section-3").text
                if vacation.find("span", class_="bloko-header-section-2"):
                    salary = vacation.find("span", class_="bloko-header-section-2").text
                    salary = re.sub("\u202f", "", salary)
                else:
                    salary = "не указана"

                company_name = vacation.find("div", class_="vacancy-serp-item__meta-info-company").text
                company_name = re.sub("\xa0", " ", company_name)
                city = vacation.find("div", attrs={'class': "bloko-text",
                                                   'data-qa': "vacancy-serp__vacancy-address"}).text.split(",")[0]

                vacations_dict.update({f'{vacation_name}':
                    [
                        {"Ссылка": f"{vacation_link}",
                         "Зарплата": f"{salary}",
                         "Компания": f"{company_name}",
                         "Город": f"{city}"}
                    ]})
            else:
                continue


def write_to_json(vacations_list: dict) -> None:
    with open("vacations.json", "w", encoding="utf-8", ) as file:
        json.dump(vacations_list, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    """
    Москва - 1, 
    Санкт-Петербург - 2
    """
    params = {
        "text": "python",
        "order_by": "publication_time",
        "items_on_page": 20
    }

    get_vacations(params, [1, 2])
    write_to_json(vacations_dict)