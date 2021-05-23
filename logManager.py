import logging.config
import config
from datetime import date
import time


# Configure logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
f_handler = logging.FileHandler('{}{}.log'.format(config.logPath, date.today()))
logger.addHandler(f_handler)

def cmsLogger(string):
    logger.info('{}: {}'.format(time.ctime(), string))

