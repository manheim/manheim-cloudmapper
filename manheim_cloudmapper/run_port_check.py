import os
import logging
from manheim_cloudmapper.port_check.portcheck import PortCheck

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_bad_ports():
    logger.info('Starting port check')
    PortCheck(
        os.getenv('OK_PORTS').split(","),
        os.getenv('ACCOUNT')
    ).check_ports()
    logger.info('Finished port check')


if __name__ == "__main__":
    check_bad_ports()
