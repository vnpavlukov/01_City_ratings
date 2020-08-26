import re
import os
import json
import datetime
import requests
from bs4 import BeautifulSoup
from time import sleep
from json_to_xlsx import json_to_xlsx

HOST = 'https://www.domofond.ru'
URL = 'https://www.domofond.ru/city-ratings'
HEADERS = {'authority': 'www.domofond.ru', 'cache-control': 'max-age=0',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate',
           'sec-fetch-user': '?1', 'sec-fetch-dest': 'document',
           'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}


def write_all_data(data, name):
    with open(name, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_data_if_exist(head, *parts):
    for part in parts:
        try:
            head = head[part]
        except:
            return None
    return head


def scrap_all_data(html_text):
    # date_time = datetime.datetime.today().strftime("%d.%m_%H")
    # file_name = os.path.join('data', f"database_{date_time}_hours.json")
    file_name = os.path.join('data', f"database_22.08_17_hours.json")

    if not os.path.isfile(file_name):
        print('Start scraping all cities names and URLs...')
        soup = BeautifulSoup(html_text, 'html.parser')
        all_cities_urls = soup.find_all('tr',
                                        class_='statistic-table__tr___3O1oy')
        database = dict()
        for city_url in all_cities_urls:
            city_name = \
                city_url.find(
                    'td', class_='statistic-table__td___2SXmY '
                                 'statistic-table__td1___30ZsU').get_text()
            city_url = HOST + city_url.get('data-url')
            database[city_name] = {'url': city_url}
        print('All cities names and URLs written into:', file_name)
        write_all_data(database, file_name)
    else:
        print('All cities names and URLs already into:', file_name)

    with open(file_name, encoding="utf8") as file:
        database = json.load(file)

    n_cities = len(database)  # number_of_cities
    n_city = 0  # city number
    print('Start scraping', n_cities, 'city(-ies)', '\n')

    for city_name, city_data in database.items():
        n_city += 1
        print(str(n_city) + '/' + str(n_cities), city_name, city_data['url'])

        # URL REQUEST
        if 'Ecology' in city_data:
            print('URLs data', city_name, 'is already in the database')
        else:

            print(f'Start scraping URL data {city_name}...')
            first_keys = ['Ecology', 'Purity', 'Utilities sector', 'Neighbors',
                          'Conditions for children', 'Sports and recreation',
                          'The shops', 'Transport', 'Security', 'Cost of living']
            first_values = list()

            while True:
                try:
                    response = requests.get(city_data['url'], headers=HEADERS)
                    break
                except:
                    print("\n*****ConnectionError or TimeoutError*****\n\n"
                          "I will retry again after 7 second...")
                    sleep(7)
                    print('Making another request:')

            soup = BeautifulSoup(response.text, 'html.parser')
            ratings = soup.find_all('div', class_="area-rating__score___3ERQc")
            for rating in ratings:
                first_values.append(rating.text)
            first_data = dict(zip(first_keys, first_values))
            print('Status code:', response.status_code)
            print('first_data:', first_data)
            city_data.update(first_data)
            write_all_data(database, file_name)
            sleep(1)

        # CURL REQUEST
        if 'avgScalePrice' in city_data:
            print('CURLs data', city_name, 'is already in the database\n')
        else:
            print(f'Start scraping CURL data {city_name}...')
            headers = {'authority': 'api.domofond.ru',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
                       'content-type': 'text/plain', 'accept': '*/*',
                       'origin': 'https://www.domofond.ru',
                       'sec-fetch-site': 'same-site', 'sec-fetch-mode': 'cors',
                       'sec-fetch-dest': 'empty',
                       'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
                       'cookie': '_ga=GA1.2.644829252.1591689961; rrpvid=368674596745111; __gads=ID=b485e7d6f6980254:T=1591689962:S=ALNI_MZkACGlGBKzopUIdSd6-IIujZO-_A; rcuid=5de9029edf0ee900018d8c09; duid=C40ZcpV4E6VNSTpM5hRcS3cSn6ryzddpgdHxeR9JcV5DRoZF; __cfduid=dd5145dbe5ee945c165a74df8aacafd771591690026; _ym_uid=1591690029683558500; _ym_d=1591690029; _gid=GA1.2.1613467270.1594113430; _gat=1', }
            city_id = re.findall(r'\w+$', city_data['url'])[0][1:]
            data = '{"id":"1","jsonrpc":"2.0","method":"priceanalysis.GetAreaPricesV1","params":{"meta":{"platform":"web","language":"ru"},"areaID":' \
                   + city_id + ',"areaType":"City"}}'

            while True:
                try:
                    response = requests.post(
                        'https://api.domofond.ru/rpc', headers=headers,
                        data=data)
                    break
                except:
                    print("ConnectionError or TimeoutError\n"
                          "I will retry again after 7 second...")
                    sleep(7)
                    print('Making another request...')

            parsing_data = json.loads(response.text)
            second_data = dict()
            second_data['avgScalePrice'] = \
                add_data_if_exist(parsing_data, 'result', 'sale',
                                  'priceAnalysisAverage', 'averagePrice')
            second_data['avgSalePricePerM2'] = \
                add_data_if_exist(parsing_data, 'result', 'sale',
                                  'priceAnalysisAverage', 'averagePricePerM2')
            second_data['avgSalePrice1Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'sale',
                                  'priceAnalysisAverage', 'avgPrice1Bedroom')
            second_data['avgSalePrice2Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'sale',
                                  'priceAnalysisAverage', 'avgPrice2Bedroom')
            second_data['avgSalePrice3Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'sale',
                                  'priceAnalysisAverage', 'avgPrice3Bedroom')
            second_data['avgSalePrice4Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'sale',
                                  'priceAnalysisAverage', 'avgPrice4Bedroom')
            second_data['avgRentPrice'] = \
                add_data_if_exist(parsing_data, 'result', 'rent',
                                  'priceAnalysisAverage', 'averagePrice')
            second_data['avgRentPricePerM2'] = \
                add_data_if_exist(parsing_data, 'result', 'rent',
                                  'priceAnalysisAverage', 'averagePricePerM2')
            second_data['avgRentPrice1Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'rent',
                                  'priceAnalysisAverage', 'avgPrice1Bedroom')
            second_data['avgRentPrice2Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'rent',
                                  'priceAnalysisAverage', 'avgPrice1Bedroom')
            second_data['avgRentPrice3Bedroom'] = \
                add_data_if_exist(parsing_data, 'result', 'rent',
                                  'priceAnalysisAverage', 'avgPrice1Bedroom')
            print('second_data:', second_data, '\n')
            city_data.update(second_data)
            write_all_data(database, file_name)
            sleep(1)


def all_rating_data(url):
    while True:
        try:
            html = requests.get(url, headers=HEADERS)
            break
        except ConnectionError or TimeoutError:
            print("\n*****ConnectionError or TimeoutError*****\n\n"
                  "I will retry again after 7 second...")
            sleep(7)
            print('Making another request...')
        except:
            print('Some problems with connection...')
            sleep(7)
            print('Making another request...')

    print('Status code:', html.status_code)
    scrap_all_data(html.text)
    sleep(1)


def main():
    print('Program is start working...')
    all_rating_data(URL)
    print('Scrapping is finished')
    json_to_xlsx()


if __name__ == '__main__':
    main()
