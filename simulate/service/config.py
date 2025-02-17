import logging, os, sys

LOGGER = logging.getLogger(__name__)


def load_env():
    """Load environment variables.

    Returns:
       dict: A dictionary containing the loaded environment variables.

    Raises:
        KeyError: If any required environment variable is missing.

    Notes:
        - The function attempts to load several environment variables including:
            - LOGGING_LEVEL: Specifies the logging level for the application.
            - STREAM: The name of the outputing kinesis delivery stream
        - If any of the required environment variables are missing, a KeyError is raised.
        - The function logs an exception message indicating the missing environment variable and exits the program with a status code of 1.
    """
    try:
        return {
            "QUEUE": os.environ["QUEUE"],
            "LOGGING_LEVEL": os.environ["LOGGING_LEVEL"]
        }
    except KeyError as error:
        LOGGER.exception("Enviroment variable %s is required.", error)
        sys.exit(1)