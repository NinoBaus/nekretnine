import requests
from bs4 import BeautifulSoup
import csv

import constants

def get_page(page_number):
    url = f'{constants.HALO_NEKRETNINE_URL_IZDAVANJE}&page={page_number}'
    return requests.get(url)

def clean_data(page_context):
    results = list()
    soup = BeautifulSoup(page_context.content, 'lxml')
    for div in soup.findAll(attrs={"class": "product-list-item"}):
        result = {}
        try:
            result['total_price'] = int(div.find(attrs={'class': 'central-feature'}).text.strip('\xa0€').replace('.', ''))
            result['title'] = div.find(attrs={'class': 'product-title'}).text
            result['link'] = f'{constants.HALO_NEKRETNITNE}{div.find(attrs={"class": "product-title"}).a["href"]}'
            ul_places = div.find(attrs={'class': 'subtitle-places'})
            try:
                loc = ul_places.find_all('li')
                result['city'] = loc[0].text.strip('\xa0')
                result['township'] = loc[1].text.strip('\xa0')
                result['place'] = loc[2].text.strip('\xa0')
                result['street'] = loc[3].text.strip('\xa0')
            except IndexError as e:
                print(e)
            sq_ro_fl = div.find_all(attrs={'class': 'value-wrapper'})
            for field in sq_ro_fl:
                if 'kvadratura' in str(field).lower():
                    result['square'] = float(field.text.split('\xa0')[0].replace(',', ''))
                    continue

                if 'broj soba' in str(field).lower():
                    result['rooms'] = float(field.text.split('\xa0')[0].replace('+', ''))
                    continue

                if 'spratnost' in str(field).lower():
                    result['floor'] = str(field.text.split('\xa0')[0])
                    continue
        except AttributeError:
            pass

        if result:
            results.append(result)

    return results


fields = ['city', 'square', 'rooms', 'total_price', 'link', 'floor', 'township', 'place', 'street', 'title']
with open('test.csv', 'w', encoding="utf-8") as csvfile:
    writter = csv.DictWriter(csvfile, fieldnames=fields)
    writter.writeheader()
    for pn in range(16):
        res = clean_data(get_page(pn))
        if res:
            writter.writerows(res)
