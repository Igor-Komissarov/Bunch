import hashlib
import json

import requests


def login(user_logon: str, user_password: str) -> tuple:

    url = 'https://rest.orbit.com/rest/iorbit/user/session/'
    b2blogon = 'iorbitv1'
    headers = {'Content-type': 'application/json'}

    user_password = user_password.encode('utf-8')
    hash_password = hashlib.md5()
    hash_password.update(user_password)
    result_password = hash_password.hexdigest()

    hash_combination = hashlib.md5()
    string_combination = f'{user_logon}|{result_password}|{b2blogon}'
    string_combination = string_combination.encode('utf-8')
    hash_combination.update(string_combination)
    result_hash = hash_combination.hexdigest()

    data = json.dumps({
        'logon': user_logon,
        'password': result_password,
        'b2blogon': b2blogon,
        'hash': result_hash
    })
    result = requests.post(
        url=url,
        headers=headers,
        data=data
    )
    result = result.json()
    ticket = result['ticket']
    shard = result['shard']

    print(ticket)
    print(shard)

    return ticket, shard


def company_history(company, ticket, shard):
    num_history = 'None'
    headers = {'Content-type': 'application/json'}

    scope = 'FAMPAT'

    url = f'https://{shard}/rest/iorbit/user/history/{scope};ticket={ticket}'

    result = requests.get(url=url, headers=headers)
    result = result.json()

    with open('search_history.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    with open('search_history.json', encoding='utf-8') as file:
        data = json.load(file)
    if data['data'] != None:
        data = data['data']
        for name in data['history']:
            if name['query'].upper() == company.upper():
                num_history = name['number']
                #print(num_history)
    return num_history


def API_company(company, ticket, shard):
    scope = 'FAMPAT'
    query = company
    #print(query)
    fields = 'FAN'
    record_range = '1-2'
    sorting = 'RELEVANCE'
    anonymous = 'false'

    #  Двойное кодирование поискового запроса
    # encoded_query = urllib.parse.quote(urllib.parse.quote(query, safe=''), safe='')

    #  Создание единого URL
    url = f'https://{shard}/rest/iorbit/user/search/{scope};ticket={ticket}'

    headers = {'Content-type': 'application/json'}

    data = json.dumps({
        'query': query,
        'fields': fields,
        'range': record_range,
        'sorting': sorting,
        'anonymous': anonymous
    })

    requests.post(
        url=url,
        headers=headers,
        data=data
    )
    #
    # result = result.json()
    #
    # with open('meme.json', 'w', encoding='utf-8') as file:
    #     json.dump(result, file, ensure_ascii=False, indent=4)


def API_FAN(json_file, FAN, ticket, shard):
    scope = 'FAMPAT'
    query = '(' + FAN + ')/FAN'
    #print(query)
    #query = 'A/PN'
    fields = 'FAN TI AB ADB CLMS DESC CTGN CTN EPRD EAPD EPN FNUM V_APL LAPD EPD PA PAAD PTCC LIC OPPI STDN NPN NPR ICLM IC PERMALINK TECD'
    record_range = '1-1000'
    sorting = 'RELEVANCE'
    anonymous = 'false'

    #  Двойное кодирование поискового запроса
    # encoded_query = urllib.parse.quote(urllib.parse.quote(query, safe=''), safe='')

    #  Создание единого URL
    url = f'https://{shard}/rest/iorbit/user/search/{scope};ticket={ticket}'

    headers = {'Content-type': 'application/json'}

    data = json.dumps({
        'query': query,
        'fields': fields,
        'range': record_range,
        'sorting': sorting,
        'anonymous': anonymous
    })

    result = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    result = result.json()

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

def api_fan_company(json_file, FAN, company, ticket, shard):
    scope = 'FAMPAT'
    print(company)
    query = '(' + FAN + ')/FAN'
    #print(query)
    #query = 'A/PN'
    fields = 'FAN TI AB ADB CLMS DESC CTGN CTN EPRD EAPD EPN FNUM V_APL LAPD EPD PA PAAD PTCC LIC OPPI STDN NPN NPR ICLM IC PERMALINK TECD'
    record_range = '1-1000'
    sorting = 'RELEVANCE'
    anonymous = 'false'
    #  Двойное кодирование поискового запроса
    # encoded_query = urllib.parse.quote(urllib.parse.quote(query, safe=''), safe='')

    #  Создание единого URL
    url = f'https://{shard}/rest/iorbit/user/search/{scope};ticket={ticket}'

    headers = {'Content-type': 'application/json'}

    data = json.dumps({
        'query': query,
        'fields': fields,
        'range': record_range,
        'sorting': sorting,
        'anonymous': anonymous
    })

    result = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    result = result.json()

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
    return json_file

def API_CTN(json_file, CTN, company, ticket, shard):
    scope = 'FAMPAT'
    query = '(' + CTN + ')/PN AND ' + company
    #query = '(' + CTN + ')/CTGN'
    #print(query)
    #query = 'Elbit Systems'
    fields = 'FAN TI AB ADB CLMS DESC CTGN CTN EPRD EAPD EPN FNUM V_APL LAPD EPD PA PAAD PTCC LIC OPPI STDN NPN NPR ICLM IC PERMALINK TECD'
    #fields = 'FAN'
    record_range = '1-1000'
    sorting = 'RELEVANCE'
    anonymous = 'false'

    #  Двойное кодирование поискового запроса
    # encoded_query = urllib.parse.quote(urllib.parse.quote(query, safe=''), safe='')

    #  Создание единого URL
    url = f'https://{shard}/rest/iorbit/user/search/{scope};ticket={ticket}'

    headers = {'Content-type': 'application/json'}

    data = json.dumps({
        'query': query,
        'fields': fields,
        'range': record_range,
        'sorting': sorting,
        'anonymous': anonymous
    })

    result = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    result = result.json()

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

def API_CTGN(json_file, CTGN, ticket, shard):
    scope = 'FAMPAT'
    query = '(' + CTGN + ')/PN'
    #query = '(' + CTGN + ')/CTGN'
    #print(query)
    #query = 'Elbit Systems'
    fields = 'FAN TI AB ADB CLMS DESC CTGN CTN EPRD EAPD EPN FNUM V_APL LAPD EPD PA PAAD PTCC LIC OPPI STDN NPN NPR ICLM IC PERMALINK TECD'
    #fields = 'FAN'
    record_range = '1-100000'
    sorting = 'RELEVANCE'
    anonymous = 'false'

    #  Двойное кодирование поискового запроса
    # encoded_query = urllib.parse.quote(urllib.parse.quote(query, safe=''), safe='')

    #  Создание единого URL
    url = f'https://{shard}/rest/iorbit/user/search/{scope};ticket={ticket}'

    headers = {'Content-type': 'application/json'}

    data = json.dumps({
        'query': query,
        'fields': fields,
        'range': record_range,
        'sorting': sorting,
        'anonymous': anonymous
    })

    result = requests.post(
        url=url,
        headers=headers,
        data=data
    )

    result = result.json()

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

def clear_history(ticket, shard):
    headers = {'Content-type': 'application/json'}

    scope = 'FAMPAT'

    url = f'https://{shard}/rest/iorbit/user/history/{scope};ticket={ticket}'

    result = requests.delete(url=url, headers=headers)
    result = result.json()

    with open('output_filename.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
