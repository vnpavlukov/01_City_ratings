import re
import time
import json
import requests
from bs4 import BeautifulSoup
from write_methods import *

HOST = 'https://www.domofond.ru'
URL = 'https://www.domofond.ru/city-ratings'
HEADERS = {'authority': 'www.domofond.ru', 'cache-control': 'max-age=0',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate',
           'sec-fetch-user': '?1', 'sec-fetch-dest': 'document',
           'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}


def scrap_all_data(html_text):
    all_names_and_links = os.path.join('data', "city_names_and_links.json")

    if not os.path.isfile(all_names_and_links):
        print('Start scraping all cities names and URLs...')
        soup = BeautifulSoup(html_text, 'html.parser')
        all_cities_links = soup.find_all('tr',
                                         class_='statistic-table__tr___3O1oy')
        names_urls = dict()
        for city_link in all_cities_links:
            city_name = \
                city_link.find(
                    'td', class_='statistic-table__td___2SXmY '
                                 'statistic-table__td1___30ZsU').get_text()
            city_link = HOST + city_link.get('data-url')
            names_urls[city_name] = city_link
        saving_names_urls(names_urls)

    with open(all_names_and_links, encoding="utf8") as file:
        names_urls = json.load(file)

    print('Start scraping', len(names_urls), 'city(-ies)', '\n')
    n = 0

    for city in names_urls:
        n += 1
        city_link = city['link']
        print(str(n) + '/' + str(len(names_urls)), city_link)

        # URL request:
        first_data = {}
        i = 0
        while not first_data:
            response = requests.get(city_link, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            ratings = soup.find_all('div',
                                    class_="area-rating__score___3ERQc")

            first_keys = ['Ecology', 'Purity', 'Utilities sector',
                          'Neighbors',
                          'Conditions for children', 'Sports and recreation',
                          'The shops', 'Transport', 'Security',
                          'Cost of living']
            first_values = []

            for rating in ratings:
                first_values.append(rating.text)

            first_data = dict(zip(first_keys, first_values))
            print('first_data:', first_data)
            i += 1
            if i > 5:
                print('************some problems**************')
                break

        # CURL request:
        headers = {'authority': 'api.domofond.ru',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
                   'content-type': 'text/plain', 'accept': '*/*',
                   'origin': 'https://www.domofond.ru',
                   'sec-fetch-site': 'same-site', 'sec-fetch-mode': 'cors',
                   'sec-fetch-dest': 'empty',
                   'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
                   'cookie': '_ga=GA1.2.644829252.1591689961; rrpvid=368674596745111; __gads=ID=b485e7d6f6980254:T=1591689962:S=ALNI_MZkACGlGBKzopUIdSd6-IIujZO-_A; rcuid=5de9029edf0ee900018d8c09; duid=C40ZcpV4E6VNSTpM5hRcS3cSn6ryzddpgdHxeR9JcV5DRoZF; __cfduid=dd5145dbe5ee945c165a74df8aacafd771591690026; _ym_uid=1591690029683558500; _ym_d=1591690029; _gid=GA1.2.1613467270.1594113430; _gat=1', }
        city_id = re.findall(r'\w+$', city_link)[0][1:]
        data = '{"id":"1","jsonrpc":"2.0","method":"priceanalysis.GetAreaPricesV1","params":{"meta":{"platform":"web","language":"ru"},"areaID":' \
               + city_id + ',"areaType":"City"}}'
        response = requests.post(
            'https://api.domofond.ru/rpc', headers=headers, data=data)
        data = json.loads(response.text)

        second_data = dict()

        def exist_data_or_none(head, *parts):
            for part in parts:
                try:
                    head = head[part]
                except:
                    return None
            return head

        second_data['avgScalePrice'] = \
            exist_data_or_none(data, 'result', 'sale', 'priceAnalysisAverage',
                               'averagePrice')
        second_data['avgSalePricePerM2'] = \
            exist_data_or_none(data, 'result', 'sale', 'priceAnalysisAverage',
                               'averagePricePerM2')
        second_data['avgSalePrice1Bedroom'] = \
            exist_data_or_none(data, 'result', 'sale', 'priceAnalysisAverage',
                               'avgPrice1Bedroom')
        second_data['avgSalePrice2Bedroom'] = \
            exist_data_or_none(data, 'result', 'sale', 'priceAnalysisAverage',
                               'avgPrice2Bedroom')
        second_data['avgSalePrice3Bedroom'] = \
            exist_data_or_none(data, 'result', 'sale', 'priceAnalysisAverage',
                               'avgPrice3Bedroom')
        second_data['avgSalePrice4Bedroom'] = \
            exist_data_or_none(data, 'result', 'sale', 'priceAnalysisAverage',
                               'avgPrice4Bedroom')
        second_data['avgRentPrice'] = \
            exist_data_or_none(data, 'result', 'rent', 'priceAnalysisAverage',
                               'averagePrice')
        second_data['avgRentPricePerM2'] = \
            exist_data_or_none(data, 'result', 'rent', 'priceAnalysisAverage',
                               'averagePricePerM2')
        second_data['avgRentPrice1Bedroom'] = \
            exist_data_or_none(data, 'result', 'rent', 'priceAnalysisAverage',
                               'avgPrice1Bedroom')
        second_data['avgRentPrice2Bedroom'] = \
            exist_data_or_none(data, 'result', 'rent', 'priceAnalysisAverage',
                               'avgPrice1Bedroom')
        second_data['avgRentPrice3Bedroom'] = \
            exist_data_or_none(data, 'result', 'rent', 'priceAnalysisAverage',
                               'avgPrice1Bedroom')
        print('second_data:', second_data, '\n')
        first_data.update(second_data)
        city['data'] = first_data

    return names_urls


def all_rating_data(url):
    html = requests.get(url, headers=HEADERS)
    if html.status_code == 200:
        return scrap_all_data(html.text)
    else:
        print('Problem with request, status code:', html.status_code)


def main():
    print('Program is start working...')
    data = all_rating_data(URL)
    write_to_file(data)


if __name__ == '__main__':
    main()
