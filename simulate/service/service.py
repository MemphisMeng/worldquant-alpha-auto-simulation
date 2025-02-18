import logging, json, requests
from service.helper import delete_message
from time import time

LOGGER = logging.getLogger(__name__)

def main(event, environment):
    """
    Entrypoint to service.
    
    :param event: AWS Event Trigger
    :type event: Dict[str, Any]
    :param environment: Dictionary containing env variables.
    :type environment: Dict[str, Any]
    """
    
    # LOGGER.info(event)
    QUEUE = environment['QUEUE']

    record = event.get('Records')[0]
    messages = json.loads(record.get('body'))
    alpha_expressions, cookies = messages.get('messages'), requests.utils.cookiejar_from_dict(messages.get('cookies'))

    i = 0
    for alpha_expression in alpha_expressions:
        for neutralization in ["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"]:
            start = time()
            try:
                type_dict = {"type": "REGULAR"}
                settings_dict = {
                    "instrumentType": "EQUITY",
                    "region": "USA",
                    "universe": "TOP3000",
                    "delay": 1,
                    "decay": 0,
                    "neutralization": neutralization,
                    "truncation": 0.08,
                    "pasteurization": "ON",
                    "unitHandling": "VERIFY",
                    "nanHandling": "ON",
                    "language": "FASTEXPR",
                    "visualization": False
                }
                regex_dict = {"regular": alpha_expression}

                simulation_data = {
                    **type_dict,
                    "settings": settings_dict,
                    **regex_dict
                }

                simulation_response = requests.post(
                    url='https://api.worldquantbrain.com/simulations',
                    json=simulation_data,
                    cookies=cookies
                )
                #TODO: get reauthenticated if the cookies expire
                simulation_progress_url = simulation_response.headers.get("Location")

                while True:
                    simulation_progress_response = requests.get(simulation_progress_url, cookies=cookies)
                    retry_after_sec = float(simulation_progress_response.headers.get("Retry-After", 0))
                    if retry_after_sec == 0:
                        break

            except Exception as e:
                LOGGER.error(e)
            finally:
                end = time()
                LOGGER.info(f"Handling the {i+1}th payload consumes {round(end - start, 2)} seconds.")
                i += 1

    # delete messages
    delete_message(QUEUE, record['receiptHandle'])