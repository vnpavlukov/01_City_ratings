import os
import re
import json
import requests
from time import sleep
from bs4 import BeautifulSoup


def parse_cities_names_and_urls(html_text):
    print('Start scraping all cities names and URLs...')
    soup = BeautifulSoup(html_text, 'html.parser')
    all_cities_urls = soup.find_all('tr',
                                    class_='statistic-table__tr___3O1oy')
    cities_data = dict()
    for city_url in all_cities_urls:
        city_name = city_url.find(
            'td', class_='statistic-table__td___2SXmY '
                         'statistic-table__td1___30ZsU').get_text()
        city_url = 'https://www.domofond.ru' + city_url.get('data-url')
        cities_data[city_name] = {'url': city_url}
    print('Scraping all cities names and URLs is finished...')
    return cities_data


def get_rating_from_response(file_name):
    with open(file_name, encoding="utf8") as file:
        cities_data = json.load(file)

    number_of_cities = len(cities_data)
    city_number = 0
    print('Start scraping with URL REQUESTS', number_of_cities, 'city(-ies)\n')

    for city_name, city_data in cities_data.items():
        city_number += 1
        print(str(city_number) + '/' + str(number_of_cities),
              city_name, city_data['url'])


        if 'Ecology' in city_data:
            print(f'URLs data {city_name}, is already in the cities_data')
        else:
            print(f'Start scraping URL data {city_name}...')
            rating_keys = ['Ecology', 'Purity', 'Utilities sector', 'Neighbors',
                           'Conditions for children', 'Sports and recreation',
                           'The shops', 'Transport', 'Security',
                           'Cost of living']
            rating_values = list()

            for _ in range(3):
                try:
                    HEADERS = {'authority': 'www.domofond.ru',
                               'cache-control': 'max-age=0',
                               'upgrade-insecure-requests': '1',
                               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
                               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                               'sec-fetch-site': 'none',
                               'sec-fetch-mode': 'navigate',
                               'sec-fetch-user': '?1',
                               'sec-fetch-dest': 'document',
                               'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}
                    response = requests.get(city_data['url'],
                                            headers=HEADERS)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    ratings = soup.find_all('div',
                                            class_="area-rating__score___3ERQc")
                    if ratings:
                        for rating in ratings:
                            rating_values.append(rating.text)
                        rating_data = dict(zip(rating_keys, rating_values))
                        print('rating_data:', rating_data, '\n')
                        city_data.update(rating_data)
                        sleep(1)
                        break
                except:
                    print("\n*****ConnectionError or TimeoutError*****\n\n"
                          "I will retry again after 7 seconds...")
                    sleep(7)
                    print('Making another request...')
    return cities_data


def get_prices_from_response(file_name):
    with open(file_name, encoding="utf8") as file:
        database = json.load(file)

    number_of_cities = len(database)
    city_number = 0
    print('Start scraping with CURL REQUESTS', number_of_cities, 'city(-ies)\n')

    for city_name, city_data in database.items():
        city_number += 1
        print(str(city_number) + '/' + str(number_of_cities), city_name,
              city_data['url'])
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
                          "I will retry again after 7 seconds...")
                    sleep(7)
                    print('Making another request...')

            parsing_data = json.loads(response.text)
            prices_data = dict()

            def return_data_if_exist(head, *parts):
                for part in parts:
                    try:
                        head = head[part]
                    except:
                        return None
                return head

            prices_data['avgScalePrice'] = \
                return_data_if_exist(parsing_data, 'result', 'sale',
                                     'priceAnalysisAverage', 'averagePrice')
            prices_data['avgSalePricePerM2'] = \
                return_data_if_exist(parsing_data, 'result', 'sale',
                                     'priceAnalysisAverage', 'averagePricePerM2')
            prices_data['avgSalePrice1Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'sale',
                                     'priceAnalysisAverage', 'avgPrice1Bedroom')
            prices_data['avgSalePrice2Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'sale',
                                     'priceAnalysisAverage', 'avgPrice2Bedroom')
            prices_data['avgSalePrice3Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'sale',
                                     'priceAnalysisAverage', 'avgPrice3Bedroom')
            prices_data['avgSalePrice4Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'sale',
                                     'priceAnalysisAverage', 'avgPrice4Bedroom')
            prices_data['avgRentPrice'] = \
                return_data_if_exist(parsing_data, 'result', 'rent',
                                     'priceAnalysisAverage', 'averagePrice')
            prices_data['avgRentPricePerM2'] = \
                return_data_if_exist(parsing_data, 'result', 'rent',
                                     'priceAnalysisAverage', 'averagePricePerM2')
            prices_data['avgRentPrice1Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'rent',
                                     'priceAnalysisAverage', 'avgPrice1Bedroom')
            prices_data['avgRentPrice2Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'rent',
                                     'priceAnalysisAverage', 'avgPrice1Bedroom')
            prices_data['avgRentPrice3Bedroom'] = \
                return_data_if_exist(parsing_data, 'result', 'rent',
                                     'priceAnalysisAverage', 'avgPrice1Bedroom')
            print('prices_data:', prices_data, '\n')
            city_data.update(prices_data)
            sleep(1)
    return database


def html_response(url):
    HEADERS = {'authority': 'www.domofond.ru', 'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate',
               'sec-fetch-user': '?1', 'sec-fetch-dest': 'document',
               'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}
    for _ in range(3):
        try:
            html = requests.get(url, headers=HEADERS)
            print('Status code:', html.status_code)
            return html.text
        except ConnectionError or TimeoutError:
            print("\n*****ConnectionError or TimeoutError*****\n\n"
                  "I will retry again after 7 seconds...")
            sleep(7)
            print('Making another request...')
        except:
            print('Some problems with connection...')
            sleep(7)
            print('Making another request...')
