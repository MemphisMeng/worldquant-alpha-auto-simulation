import logging
from service.helper import publish_sqs

LOGGER = logging.getLogger(__name__)

def main(event, environment):
    LOGGER.info(event)
    QUEUE = environment['QUEUE']

    for group in ['subindustry', 'sector', 'industry', 'market']:
        _ = publish_sqs(QUEUE, {'group': group})