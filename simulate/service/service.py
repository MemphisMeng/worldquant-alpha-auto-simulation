import logging, ast, requests
from service.helper import delete_message, receive_message

LOGGER = logging.getLogger(__name__)

def main(event, environment):
    """
    Entrypoint to service.
    
    :param event: AWS Event Trigger
    :type event: Dict[str, Any]
    :param environment: Dictionary containing env variables.
    :type environment: Dict[str, Any]
    """
    
    LOGGER.info(event)
    QUEUE = environment['QUEUE']

    messages = receive_message(QUEUE)

    for message in messages:
        try:
            message_body = message['Body']
            body = ast.literal_eval(message_body)
            alpha_expression = body.get('expression')
            cookies = requests.utils.cookiejar_from_dict(body.get('cookies'))
            for neutralization in ["SUBINDUSTRY", "INDUSTRY", "SECTOR"]:

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
                    **settings_dict,
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

            delete_message(QUEUE, message['ReceiptHandle'])
        except Exception as e:
            LOGGER.error(e)
