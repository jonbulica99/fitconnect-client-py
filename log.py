import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)
logger = logging.getLogger("fitconnect")
