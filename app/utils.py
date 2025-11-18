import os
import logging
from dotenv import load_dotenv


def load_env(path: str = '.env'):
    """
    Load environment variables from a .env file if present. Does not override existing env vars.
    """
    if os.path.exists(path):
        load_dotenv(path, override=False)


def get_logger(name: str = __name__):
    """
    Return a logger configured to log to stdout (Railway will collect console logs).
    Avoid duplicate handlers.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)
    return logger
