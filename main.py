import datetime
from files_functions import *
from parsing_functions import *

PAGE_WITH_ALL_CITIES = 'https://www.domofond.ru/city-ratings'


def scrap_all_data(url):
    # now_day_month_hour = datetime.datetime.today().strftime("%d.%m_%H")
    # file_name = os.path.join('data', f"data_cities_{now_day_month_hour}.00.json")
    file_name = os.path.join('data', f"data_cities_03.09_11.00.json")

    if not os.path.isfile(file_name):
        html_text = html_response(url, WEB_HEADERS)
        cities_names_and_urls = parse_cities_names_and_urls(html_text)
        write_data_in_file(cities_names_and_urls, file_name)
        print('All cities names and URLs written into:', file_name)
    else:
        print('All cities names and URLs already into:', file_name)

    cities_names_and_urls = get_city_data_from_json_file(file_name)
    data_with_cities_rating = scrap_rating_if_not_exist(cities_names_and_urls)
    write_data_in_file(data_with_cities_rating, file_name)

    data_with_cities_prices = scrap_prices_if_not_exist(data_with_cities_rating)
    write_data_in_file(data_with_cities_prices, file_name)


def main():
    print('Program is start working...')
    start_time = datetime.datetime.today()

    scrap_all_data(PAGE_WITH_ALL_CITIES)

    end_time = datetime.datetime.today()
    delta = end_time - start_time
    print(f'Scrapping is completed within {delta.seconds // 60} minute(s)'
          f' and {delta.seconds % 60} second(s)')
    json_to_xlsx()


if __name__ == '__main__':
    main()
