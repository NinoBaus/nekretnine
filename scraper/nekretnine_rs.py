import requests
from bs4 import BeautifulSoup
import csv
import json

import constants

def get_page(page_number):
    url = f'{constants.NEKRETNINE_RS_URL}stranica/{page_number}/'
    return requests.get(url)

def room_filter(rooms):
    for room in constants.ROOMS_NEKRETNINE_RS:
        if room.lower() in rooms.lower():
            return constants.ROOMS_NEKRETNINE_RS[room]

def clean_data(page_context):
    results = list()
    soup = BeautifulSoup(page_context.content, 'lxml')
    ads_body = soup.find(attrs={"class": 'advert-list'})
    ads = ads_body.find_all(attrs={"class": 'offer-body'})
    for ad in ads:
        result = dict()
        title = ad.find(attrs={'class': 'offer-title'})
        result['title'] = title.text.strip()
        result['link'] = f'{constants.NEKRETNINE_RS}{title.a["href"]}'

        price = ad.find(attrs={'class': 'offer-price'})
        try:
            result['price'] = int(price.span.text.replace(' ', '').replace('EUR', ''))
        except:
            result['price'] = price.span.text.strip()

        location = ad.find(attrs={'class': 'offer-location'}).text
        try:
            result['township'] = location.split(',')[0].strip()
            result['city'] = location.split(',')[1].strip()
        except:
            pass

        square = ad.find(attrs={'class': 'offer-price offer-price--invert'})
        try:
            result['square'] = float(square.text.strip().replace(' m²', ''))
        except:
            result['square'] = square.text.strip()

        rooms = ad.find(attrs={'class': 'offer-adress'})
        result['rooms'] = room_filter(str(rooms.text.strip().split('  |  ')[-1]))
        results.append(result)

    return results

fields = ['city', 'rooms', 'square', 'price', 'link', 'township', 'title']
with open('nekretnine_rs.csv', 'w', encoding="utf-8") as csvfile:
    writter = csv.DictWriter(csvfile, fieldnames=fields)
    writter.writeheader()
    for pn in range(1, 120):
        print(f'RUNNING PAGE {pn}')
        res = clean_data(get_page(pn))
        if res:
            writter.writerows(res)
