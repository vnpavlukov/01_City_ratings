import re
import json
import requests
from time import sleep
from bs4 import BeautifulSoup

WEB_HEADERS = {'authority': 'www.domofond.ru', 'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWeb'
                             'Kit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.11'
                             '6 Safari/537.36',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                         'image/webp,image/apng,*/*;q=0.8,application/signed-'
                         'exchange;v=b3;q=0.9',
               'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate',
               'sec-fetch-user': '?1', 'sec-fetch-dest': 'document',
               'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}
API_HEADERS = {'authority': 'www.domofond.ru',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWe'
                             'bKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.'
                             '116 Safari/537.36',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                         'image/webp,image/apng,*/*;q=0.8,application/signed-ex'
                         'change;v=b3;q=0.9',
               'sec-fetch-site': 'none',
               'sec-fetch-mode': 'navigate',
               'sec-fetch-user': '?1',
               'sec-fetch-dest': 'document',
               'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7'}
API_URL = 'https://api.domofond.ru/rpc'


def html_response(url, headers, request_method='get', data=None):
    for _ in range(3):
        try:
            if request_method == 'get':
                html = requests.get(url, headers=headers)
                return html.text
            elif request_method == 'post':
                html = requests.post(url, headers=headers, data=data)
                return html.text
            else:
                raise Exception('You must enter post or get method')

        except ConnectionError or TimeoutError:
            print("\n*****ConnectionError or TimeoutError*****\n\n"
                  "I will retry again after 7 seconds...")
            sleep(7)
            print('Making another request...')


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


def get_city_data_from_json_file(file_name):
    with open(file_name, encoding="utf8") as file:
        return json.load(file)


def get_rating_from_response(cities_data):
    number_of_cities = len(cities_data)
    city_number = 0
    print('Start scraping ratings', number_of_cities, 'city(-ies)\n')

    for city_name, city_data in cities_data.items():
        city_number += 1
        print(str(city_number) + '/' + str(number_of_cities),
              city_name, city_data['url'])

        if 'Ecology' in city_data:
            print(f'Ratings data {city_name}, is already in the cities_data')
        else:
            print(f'Start scraping {city_name} ratings ...')
            rating_keys = ['Ecology', 'Purity', 'Utilities sector', 'Neighbors',
                           'Conditions for children', 'Sports and recreation',
                           'The shops', 'Transport', 'Security',
                           'Cost of living']
            rating_values = list()

            for _ in range(3):
                prices_response = html_response(city_data['url'],
                                                WEB_HEADERS)
                soup = BeautifulSoup(prices_response, 'html.parser')
                ratings = soup.find_all('div',
                                        class_="area-rating__score___3ERQc")
                if ratings:  # page has parsed, but there is no data
                    for rating in ratings:
                        rating_values.append(rating.text)
                    rating_data = dict(zip(rating_keys, rating_values))
                    print('rating_data:', rating_data, '\n')
                    city_data.update(rating_data)
                    sleep(1)
                    break
    return cities_data


def get_prices_from_response(cities_data):
    number_of_cities = len(cities_data)
    city_number = 0
    print('Start scraping prices', number_of_cities, 'city(-ies)\n')

    for city_name, city_data in cities_data.items():
        city_number += 1
        print(str(city_number) + '/' + str(number_of_cities), city_name,
              city_data['url'])
        if 'avgScalePrice' in city_data:
            print('Prices data', city_name, 'is already in the cities_data\n')
        else:
            print(f'Start scraping {city_name} prices...')

            city_id = re.findall(r'\w+$', city_data['url'])[0][1:]
            data = '{"id":"1","jsonrpc":"2.0","method":"priceanalysis.GetAre' \
                   'aPricesV1","params":{"meta":{"platform":"web","language":' \
                   '"ru"},"areaID":' + city_id + ',"areaType":"City"}}'

            json_response = html_response(API_URL, API_HEADERS, 'post', data)
            parsing_data = json.loads(json_response)
            prices_data = dict()

            def return_data_if_exist(head, *parts):
                for part in parts:
                    try:
                        head = head[part]
                    except TypeError:
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
    return cities_data
