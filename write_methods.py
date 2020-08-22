import datetime
import json
import os


def write_to_file(data):
    if data:
        date_time = datetime.datetime.today()
        file_name = date_time.strftime("%d.%m_%H.%M") + '.txt' + '_len_'
        with open('data/' + file_name + str(len(data)) + '.txt', 'w') as f:
            for line in data:
                print(line, file=f)
    else:
        print('Nothing to write')


def saving_names_urls(data):
    complete_name = os.path.join('data', "city_names_and_links.json")
    with open(complete_name, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent='\n')
