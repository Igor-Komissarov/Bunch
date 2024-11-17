import json
import sys
from deep_translator import GoogleTranslator
import pandas as pd
from gen_api import *
import os
import shutil
import locale
import re
from openpyxl import load_workbook

def process_text_field(field, replace_dict=None, remove_country_code=False):
    """Обрабатывает текстовое поле, выполняя замены и, при необходимости, удаляет коды стран."""
    if not field:
        return ''
    
    # Удаление кода страны в начале строки, если remove_country_code=True
    if remove_country_code:
        #print(field)
        field = re.sub(r'^\([A-Z]{2,3}\d+(?:/\d+)?\)\s*', '', field)
    
    # Выполнение замен, если они указаны
    #print(field)
    if replace_dict:
        for old, new in replace_dict.items():
            field = field.replace(old, new)
    
    return field.replace('<br/>', '\n')

def process_citing_cited(field, delimiter):
    """Обрабатывает поля citing/cited патентов."""
    if field:
        return [entry.split()[0] for entry in field.split(delimiter)[1:] if entry]
    return []

def process_v_apl(v_apl):
    """Обрабатывает поле V_APL, обрабатывая как строку или как список."""
    if not v_apl:
        return None

    if isinstance(v_apl, str):
        v_apl = v_apl.replace('<br/>', '\n').replace(';', '')
        return v_apl
    elif isinstance(v_apl, list):
        result = {
            'APD': [], 'PN': [], 'DATE': [], 'KIND': [], 'XAP': [], 'STATE': [], 'STATUS': []
        }
        for entry in v_apl:
            result['APD'].append(entry.get('APD', ''))
            result['XAP'].append(entry.get('XAP', ''))
            result['STATE'].append(entry.get('ACT_STATE', ''))
            result['STATUS'].append(entry.get('ACT_STATUS', ''))

            for pub in entry.get('PUB', []):
                result['PN'].append(pub.get('PN', ''))
                result['DATE'].append(pub.get('DATE', ''))
                result['KIND'].append(pub.get('KIND', ''))
        return result
    return None

def process_pasi(fnum):
    """Обрабатывает поле FNUM для извлечения PASI."""
    true_PASI = []
    if fnum:
        fnum = fnum.replace('<br/>', '\n')
        fake_fnum = fnum.split()
        for i in fake_fnum:
            i = i.replace(';', '').split('=')
            if i[0] == 'PASI':
                PASI = i[1]
                true_PASI.append(PASI)
    return true_PASI

def process_pa_ad(pa_ad):
    """Обрабатывает поле PAAD для извлечения кода страны."""
    true_PAAD = []
    #print(pa_ad)
    if pa_ad:
        PAAD = pa_ad.replace(' , ', '\n')
        fake_PAAD = PAAD.split()
        for i in fake_PAAD:
            i = i.split('=')
            if i[0] == 'COUNTRY' and len(i) > 1:
                PAAD = i[1][0:2]
                true_PAAD.append(PAAD)
    else:
        true_PAAD.append(pa_ad)
    return true_PAAD

def format_string(input_string):
    """Форматирует строки, удаляя ненужные символы."""
    return input_string.replace('\'', '').replace('[', '').replace(']', '').replace(')', '').replace('(', '').replace('\"', '')

def process_field_list(field_list):
    """Обрабатывает список полей с заменой символов."""
    return [format_string(str(field)) for field in field_list]

def extract_patent_info(name):
    """Извлекает информацию о патентах, обрабатывая все ключевые поля."""
    return {
        'FAN': name.get('FAN', ''),
        'PA': name.get('PA', ''),
        'TI': name.get('TI', ''),
        'AB': process_text_field(name.get('AB', ''), {'<br/>': '\n'}),
        'CLMS': process_text_field(name.get('CLMS', ''), {'<p>': '', '</p>': '\n'}),
        'ADB': process_text_field(name.get('ADB', ''), {'<p>': '', '</p>': '\n'}),
        'DESC': process_text_field(name.get('DESC', ''), {'<p>': '', '</p>': '\n'}),
        'CTGN': process_citing_cited(name.get('CTGN', ''), '<br/>'),
        'CTN': process_citing_cited(name.get('CTN', ''), '<br/>'),
        'EPRD': name.get('EPRD', ''),
        'EAPD': name.get('EAPD', ''),
        'EPD': name.get('EPD', ''),
        'EPN': name.get('EPN', ''),
        'LAPD': name.get('LAPD', ''),
        'V_APL': process_v_apl(name.get('V_APL', '')),
        'PASI': process_pasi(name.get('FNUM', '')),
        'PAAD': process_pa_ad(name.get('PAAD', ''))
    }

def json_explore(json_file):
    """Основная функция для обработки JSON файла."""
    all_fields = {
        'true_FAN': [], 'true_TI': [], 'true_AB': [], 'true_CLMS': [], 'true_ADB': [], 'true_DESC': [],
        'true_CTGN': [], 'true_CTN': [], 'true_EPRD': [], 'true_EAPD': [], 'true_PASI': [], 'true_APD': [],
        'true_PN': [], 'true_DATE': [], 'true_KIND': [], 'true_LAPD': [], 'true_EPN': [], 'true_EPD': [],
        'true_XAP': [], 'true_state': [], 'true_status': [], 'true_PA': [], 'true_PAAD': []
    }

    with open(json_file, encoding='utf-8') as file:
        data_json = json.load(file)
    #print(data_json)
    try:
        if data_json['nb'] == 0:
            print('Был получен пустой json')
            sys.exit(1)
    except Exception as e:
        if 'merged' in json_file:
            pass
        else:
            print(e)
            sys.exit(1)
    while len(data_json) != 0:
        if 'merged' in json_file:
            data = dict(data_json[0])
        else:
            data = data_json
            data_json = ['none']
        documents = data['documents']
        for name in documents:
            patent_info = extract_patent_info(name)

            all_fields['true_FAN'].append(patent_info['FAN'])
            all_fields['true_PA'].append(patent_info['PA'])
            all_fields['true_TI'].append(patent_info['TI'])
            all_fields['true_AB'].append(patent_info['AB'])
            all_fields['true_CLMS'].append(patent_info['CLMS'])
            all_fields['true_ADB'].append(patent_info['ADB'])
            all_fields['true_DESC'].append(patent_info['DESC'])
            all_fields['true_CTGN'].append(patent_info['CTGN'])
            all_fields['true_CTN'].append(patent_info['CTN'])
            all_fields['true_EPRD'].append(patent_info['EPRD'])
            all_fields['true_EAPD'].append(patent_info['EAPD'])
            all_fields['true_EPD'].append(patent_info['EPD'])
            all_fields['true_EPN'].append(patent_info['EPN'])
            all_fields['true_LAPD'].append(patent_info['LAPD'])
            v_apl_info = patent_info['V_APL']
            if v_apl_info:
                all_fields['true_APD'].append(v_apl_info.get('APD', []))
                all_fields['true_PN'].append(v_apl_info.get('PN', []))
                all_fields['true_DATE'].append(v_apl_info.get('DATE', []))
                all_fields['true_KIND'].append(v_apl_info.get('KIND', []))
                all_fields['true_XAP'].append(v_apl_info.get('XAP', []))
                all_fields['true_state'].append(v_apl_info.get('STATE', []))
                all_fields['true_status'].append(v_apl_info.get('STATUS', []))

            all_fields['true_PASI'].extend(patent_info['PASI'])
            all_fields['true_PAAD'].extend(patent_info['PAAD'])

        del data_json[0]

    # Используем len_num для ограничения длины всех полей
    len_num = len(all_fields['true_PA'])

    # Обрезаем все поля до длины len_num
    for key in all_fields:
        all_fields[key] = all_fields[key][:len_num]

    # Форматирование всех данных
    all_names = {
        'Questel unique family ID (FAN)': process_field_list(all_fields['true_FAN']),
        'Title': process_field_list(all_fields['true_TI']),
        'Abstract': process_field_list(all_fields['true_AB']),
        'Claims': process_field_list(all_fields['true_CLMS']),
        'Advantages / Previous drawbacks': process_field_list(all_fields['true_ADB']),
        'English description': process_field_list(all_fields['true_DESC']),
        'Citing patents - Standardized publication number': process_field_list(all_fields['true_CTGN']),
        'Cited patents - Standardized publication number': process_field_list(all_fields['true_CTN']),
        'Earliest priority date': process_field_list(all_fields['true_EPRD']),
        'Earliest application date': process_field_list(all_fields['true_EAPD']),
        'Patent strength': process_field_list(all_fields['true_PASI']),
        'Publication numbers': process_field_list(all_fields['true_PN']),
        'Publication kind codes': process_field_list(all_fields['true_KIND']),
        'APD': process_field_list(all_fields['true_APD']),
        'DATE': process_field_list(all_fields['true_DATE']),
        'LAPD': process_field_list(all_fields['true_LAPD']),
        'Earliest publication number': process_field_list(all_fields['true_EPN']),
        'Earliest publication date': process_field_list(all_fields['true_EPD']),
        'Standardized application number': process_field_list(all_fields['true_XAP']),
        'Family legal status': process_field_list(all_fields['true_status']),
        'Family legal state': process_field_list(all_fields['true_state']),
        'Current assignees': process_field_list(all_fields['true_PA']),
        'Assignee country': process_field_list(all_fields['true_PAAD'])
    }

    return all_names, all_fields['true_FAN'], all_fields['true_LAPD']

def check_field_lengths(data_dict):
    """Проверяет и выводит длину каждого поля в словаре."""
    for key, value in data_dict.items():
        print(f"Field '{key}' has length: {len(value)}")


def clean_string(string):
    """Очищает строку CTN от ненужных символов."""
    tring = string.replace('[\'', '').replace('\']', '').replace('\'', '').replace('\"', '').replace(',', '')
    return string.split()


def prepare_query(list):
    """Подготавливает строку CTN для запроса."""
    return str(list).replace('\', \'', ' OR ').replace('[\'', '').replace('\']', '')

def process_directory(directory):
    """Создаёт или очищает директорию для JSON файлов."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        shutil.rmtree(directory)
        os.makedirs(directory)

def merge_json_files(directory, output_file):
    """Объединяет все JSON файлы в директории в один файл."""
    merged = []
    for infile in os.listdir(directory):
        with open(os.path.join(directory, infile), 'r', encoding='utf-8') as infp:
            data = json.load(infp)
            merged.append(data)
    with open(output_file, 'w', encoding="utf-8") as outfp:
        json.dump(merged, outfp)

def json_CTN(df, current_query, ticket, shard):
    """Функция для работы с Cited патентами."""
    CTN = clean_string(df['Cited patents - Standardized publication number'].iloc[0])

    # Удаление пустых значений и создание уникального списка
    true_CTN = list(set(CTN))
    if len(true_CTN) == 0:
        print('Пустой лист Cited')
        sys.exit(1)

    print('Проверим длину true_CTN: ', len(true_CTN))

    # Создание директории для JSON, если она не существует
    json_dir = 'json_CTN'
    process_directory(json_dir)

    json_file = 'CTN_REQ.json'

    if len(true_CTN) >= 590:
        num_CTN = 1
        while len(true_CTN) > 0:
            # Разбиение списка на блоки по 590 элементов
            current_block = true_CTN[:590]
            true_CTN = true_CTN[590:]

            # Подготовка строки для запроса
            CTN_query = prepare_query(current_block)

            json_file = f'CTN_REQ_{num_CTN}.json'
            num_CTN += 1

            print('Посылаем запрос в API по Cited')
            API_CTN(json_file, CTN_query, current_query, ticket, shard)
            shutil.move(json_file, json_dir)

        # Объединение всех созданных JSON файлов
        json_file = 'merged_CTGN.json'
        merge_json_files(json_dir, json_file)
    else:
        # Подготовка строки для запроса при длине менее 590
        CTN_query = prepare_query(true_CTN)

        print('Посылаем запрос в API по Cited')
        API_CTN(json_file, CTN_query, current_query, ticket, shard)

    return json_file

def json_CTGN(df, ticket, shard):
    """Функция для работы с Citing патентами."""
    check = df['Citing patents - Standardized publication number'].iloc[0]

    if check is None:
        return 'exit'

    num_CTGN = len(df['Citing patents - Standardized publication number'])
    all_CTGN = []

    # Очистка данных для всех строк
    for i in range(num_CTGN):
        CTGN = df['Citing patents - Standardized publication number'].iloc[i]
        if CTGN:
            all_CTGN.extend(clean_string(str(CTGN)))

    # Удаление пустых элементов и создание уникального списка
    true_CTGN = list(set(all_CTGN))
    if len(true_CTGN) == 0:
        print('Пустой лист Citing')
        raise Exception("File is empty")
    print('Проверим длину true_CTGN: ', len(true_CTGN))

    json_file = 'CTGN_REQ.json'
    json_dir = 'json_CTGN'
    process_directory(json_dir)

    if len(true_CTGN) >= 600:
        num_CTGN = 1
        while len(true_CTGN) > 0:
            # Разбиение на блоки по 590 элементов
            current_block = true_CTGN[:590]
            true_CTGN = true_CTGN[590:]

            CTGN_query = prepare_query(current_block)

            json_file = f'CTGN_REQ_{num_CTGN}.json'
            print('Посылаем запрос в API по Citing')
            API_CTGN(json_file, CTGN_query, ticket, shard)
            shutil.move(json_file, json_dir)

            num_CTGN += 1

        # Объединение всех созданных JSON файлов
        json_file = 'merged_CTGN.json'
        merge_json_files(json_dir, json_file)
    else:
        # Обработка запроса при длине менее 600
        CTGN_query = prepare_query(true_CTGN)
        print('Посылаем запрос в API по Citing')
        API_CTGN(json_file, CTGN_query, ticket, shard)

    return json_file

def process_fnum(fnum, name):
    """Обрабатывает поле FNUM для извлечения PASI."""
    true_data = []
    if fnum:
        fnum = fnum.replace('<br/>', '\n')
        fake_fnum = fnum.split()
        for i in fake_fnum:
            i = i.replace(';', '').split('=')
            if i[0] == name:
                name = i[1]
                true_data.append(name)
            elif i[0] == name:
                name = i[1]
                true_data.append(name)
            elif i[0] == name:
                name = i[1]
                true_data.append(name)
    return true_data