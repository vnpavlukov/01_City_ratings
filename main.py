import datetime
from files_functions import *
from parsing_functions import *

HOST = 'https://www.domofond.ru'
PAGE_WITH_ALL_CITIES = 'https://www.domofond.ru/city-ratings'


def scrap_all_data(url):
    html_text = html_response(url)
    now_day_month_hour = datetime.datetime.today().strftime("%d.%m_%H")
    file_name = os.path.join('data', f"database_{now_day_month_hour}_hours.json")
    # file_name = os.path.join('data', f"database_22.08_17_hours.json")

    if not os.path.isfile(file_name):
        write_data_in_file(parse_cities_names_and_urls(html_text), file_name)
        print('All cities names and URLs written into:', file_name)
    else:
        print('All cities names and URLs already into:', file_name)

    rating_data_all_cities = get_rating_from_response(file_name)
    write_data_in_file(rating_data_all_cities, file_name)

    price_data_all_cities = get_prices_from_response(file_name)
    write_data_in_file(price_data_all_cities, file_name)


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
