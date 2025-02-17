import boto3, logging, itertools
from typing import Optional
import requests
from helper import authenticate, publish_sqs

LOGGER = logging.getLogger(__name__)

def main(event, environment):
    LOGGER.info(event)
    QUEUE = environment['QUEUE']

    cookies = authenticate()
    searchScope = {'region': 'USA', 'delay': '1', 'universe': 'TOP3000', 'instrumentType': 'EQUITY'}
    datafields = []
    for dataset in ['fundamental2', 'fundamental6']:
        datafields.extend(
            get_datafields(cookies=cookies, searchScope=searchScope, dataset_id=dataset))
        
    cookies_dict = requests.utils.dict_from_cookiejar(cookies)
    for field1, field2, group in itertools.product(datafields, datafields, ['subindustry', 'sector', 'industry']):
        alpha_expression = f'group_rank(({field1})/{field2}, {group})'
        message = {'expression': alpha_expression}
        message = {**message, **cookies_dict}
        _ = publish_sqs(QUEUE, message)


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

    return datafields_list