import logging, json
from time import time, sleep
from typing import Optional
import requests
from service.helper import authenticate, publish_sqs

LOGGER = logging.getLogger(__name__)

def main(event, environment):
    LOGGER.info(event)
    QUEUE = environment['QUEUE']

    record = event.get('Records')[0]
    group = json.loads(record.get('body')).get('group')

    try:
        cookies = authenticate()
        LOGGER.info("Authentication is successful!")
        searchScope = {'region': 'USA', 'delay': '1', 'universe': 'TOP3000', 'instrumentType': 'EQUITY'}
        datafields = []
        for i, dataset in enumerate(['fundamental2', 'fundamental6']):
            LOGGER.info(f"Starting the {i+1}th iteration...")
            start = time()
            datafields.extend(
                get_datafields(cookies=cookies, searchScope=searchScope, dataset_id=dataset))
            end = time()
            LOGGER.info(f"The {i+1}th iteration of API calls takes {round(end - start)} seconds.")
            
        cookies_dict = {'cookies': requests.utils.dict_from_cookiejar(cookies)}
        messages = []
        start = time()
        for field1 in datafields:
            for field2 in datafields:
                alpha_expression = f'group_rank(({field1})/{field2}, {group})'
                messages.append(alpha_expression)
                if len(messages) == 20: # batch delivery
                    _ = publish_sqs(QUEUE, {'messages': messages, **cookies_dict})
                    messages = [] # reset
        end = time()
        LOGGER.info(f"The batch delivery takes {round(end - start)} seconds.")

    except Exception as e:
        LOGGER.error(e)


def get_datafields(
        cookies,
        searchScope,
        dataset_id: str = '',
        search: Optional[str] = None
):
    instrument_type = searchScope.get('instrumentType', 'EQUITY')
    region = searchScope.get('region', 'USA')
    delay = searchScope.get('delay', 1)
    universe = searchScope.get('universe', 'TOP3000')

    if not search:
        url_template = "https://api.worldquantbrain.com/data-fields?" + \
                       f"&instrumentType={instrument_type}" + \
                       f"&region={region}&delay={str(delay)}&universe={universe}&dataset.id={dataset_id}&limit=50" + \
                       "&offset={x}"
        LOGGER.info("Calling API...")
        count = requests.get(
            url=url_template.format(x=0),
            cookies=cookies).json()['count']
    else:
        url_template = "https://api.worldquantbrain.com/data-fields?" + \
                       f"&instrumentType={instrument_type}" + \
                       f"&region={region}&delay={str(delay)}&universe={universe}&limit=50" + \
                       f"&search={search}" + \
                       "&offset={x}"
        count = 100

    datafields_list = []
    for x in range(0, count, 50):
        datafields = requests.get(url_template.format(x=x), cookies=cookies)
        datafields_list.extend(
            [datafield.get('id') for datafield in datafields.json()['results'] if datafield.get('type') == 'MATRIX']
            )
        LOGGER.info(f"{len(datafields_list)} datafields are collected")
        sleep(1)

    return datafields_list