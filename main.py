from bs4 import BeautifulSoup
import requests
import fake_headers
import json
import re
from os import getcwd


class HhScrap:
    def __init__(self, browser, os, *args):
        self.list_vacancy = []
        self.browser = browser
        self.os = os
        self.keyword = args

    def get_headers(self):
        headers = fake_headers.Headers(browser=self.browser, os=self.os)
        headers_info = headers.generate()
        return headers_info

    def get_links(self, page) -> list:
        params = {"area": ["1", "2"], "text": "python",
                  "order_by": "publication_time", "page": f'{page}'}
        responce = requests.get("https://hh.ru/search/vacancy",
                                headers=self.get_headers(), params=params)
        soup = BeautifulSoup(responce.text, "lxml")
        info = soup.find_all('a', class_="serp-item__title")
        links = [i.get('href') for i in info]
        return links

    def page_serch(self, pages: int):
        for page in range(pages+1):
            self.serch_keyword(page)

    def serch_keyword(self, page: int):
        links = self.get_links(page)
        print(f'page:{page}', end='\n')
        for id, link in enumerate(links):
            soup = self.get_info(link)
            key = soup.get_text()
            dict_hh = {'city': 'city',
                       'company': 'company',
                       'salary': 'salary',
                       'link': 'link'}
            if set(self.keyword).issubset(set(key.split())):
                dict_hh['link'] = link
                self.get_company(soup, dict_hh)
                self.get_city(soup, dict_hh)
                self.get_salary(soup, dict_hh)
                self.list_vacancy.append(dict_hh)
            print(f'{id+1}', end=' ')
        print(f'найдено вакансий - {len(self.list_vacancy)}')

    def get_info(self, link):
        responce = requests.get(link, headers=self.get_headers())
        soup = BeautifulSoup(responce.text, "lxml")
        return soup

    def get_company(self, soup, dict_hh: dict):
        info = soup.find('span', class_='vacancy-company-name').text
        dict_hh['company'] = info

    def get_city(self, soup, dict_hh: dict):
        info = soup.find(attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
        dict_hh['city'] = info

    def get_salary(self, soup, dict_hh: dict):
        info = soup.find(attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
        if info:
            pattern = re.compile("(\Sxa)")
            subs = '.'
            dict_hh['salary'] = pattern.sub(subs, info.text)
        else:
            dict_hh['salary'] = 'договорная'

    def to_json(self):
        with open(f'{getcwd()}/vacancies.json' "w") as f:
            json.dump(self.list_vacancy, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    pythonHh = HhScrap('opera', 'win', 'Django', 'Flask')
    pythonHh.page_serch(10)
    pythonHh.to_json()
