import requests
from bs4 import BeautifulSoup
import csv

import constants

def get_page(page_number):
    url = f'{constants.CETIRI_ZIDA_URL_IZDAVANJE}?strana={page_number}'
    return requests.get(url)


def clean_data(page_context):
    results = list()
    soup = BeautifulSoup(page_context.content, 'lxml')
    for div in soup.findAll(attrs={"class": "meta-container"}):
        result = dict()
        result['link'] = f'{constants.CETIRI_ZIDA}{div.find("a")["href"]}'
        result['total_price'] = int(div.find(attrs={"class": "prices"}).text.split('\xa0')[0].replace('.', ''))
        section = div.find(attrs={"class": 'meta-labels'})
        if section:
            details = section.find_all(attrs={"class": 'ng-star-inserted'})
            for detail in details:
                # import ipdb; ipdb.set_trace()
                if detail.text in constants.CONDITION_LIST:
                    result['condition'] = detail.text
                elif detail.text in constants.HEATING_LIST:
                    result['heating'] = detail.text
                else:
                    for r in constants.ROOMS_LIST:
                        if r.lower() in detail.text.lower():
                            result['rooms'] = float(detail.text.split(' ')[0])

        location = div.find(attrs={"class": 'place-names'})
        if location:
            result['street'] = location.h4.find(attrs={"class": 'ad-title'}).text
            geo_position = location.find(attrs={"class": 'ng-star-inserted'}).text.split(',')
            geo_position.reverse()
            try:
                result['city'] = geo_position[0].strip()
                result['township'] = geo_position[1].strip()
                result['place'] = geo_position[-1].strip()
            except:
                pass

        if result:
            results.append(result)

    return results


fields = ['city', 'rooms', 'total_price', 'link', 'condition', 'heating', 'township', 'place', 'street']
with open('cetiri_zida.csv', 'w', encoding="utf-8") as csvfile:
    writter = csv.DictWriter(csvfile, fieldnames=fields)
    writter.writeheader()
    for pn in range(1, 364):
        print(f'RUNNING PAGE {pn}')
        res = clean_data(get_page(pn))
        if res:
            writter.writerows(res)
