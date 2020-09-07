from files_functions import *
from parsing_functions import *

PAGE_WITH_ALL_CITIES = 'https://www.domofond.ru/city-ratings'
file_name = file_name_path_data_name_d_m_h()
# file_name = os.path.join('data', f"data_cities_03.09_11.00.json")


def main():
    print('Program is start working...')
    start_time = datetime.datetime.today()

    if os.path.isfile(file_name):
        print('All cities names and URLs already into:', file_name)
        cities_names_and_urls = get_city_data_from_json_file(file_name)
    else:
        html_text = html_response(PAGE_WITH_ALL_CITIES, WEB_HEADERS)
        cities_names_and_urls = get_cities_names_and_urls(html_text)
        write_data_in_file(cities_names_and_urls, file_name)
        print('All cities names and URLs written into:', file_name)

    number_of_cities = len(cities_names_and_urls)
    city_number = 0
    print('\nStart scraping data', number_of_cities, 'city(-ies):\n')

    for city_name, city_data in cities_names_and_urls.items():
        city_number += 1
        city_url = city_data['url']
        print(f'{city_number}/{number_of_cities} {city_name} {city_url}')

        city_rating = parse_city_rating(city_name, city_data)
        city_data.update(city_rating)

        city_prices = parse_city_prices(city_name, city_data)
        city_data.update(city_prices)

        write_data_in_file(cities_names_and_urls, file_name)

    end_time = datetime.datetime.today()
    delta = end_time - start_time
    print(f'Scrapping is completed within {delta.seconds // 60} minute(s)'
          f' and {delta.seconds % 60} second(s)')
    json_to_xlsx()


if __name__ == '__main__':
    main()
