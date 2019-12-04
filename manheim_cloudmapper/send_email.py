import os
import logging
from manheim_cloudmapper.ses.ses_report_sender import SesReportSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_email():
    if bool_convert(os.environ['SES_ENABLED']):
        logger.info('Generating and sending report email')
        SesReportSender().generate_and_send_email()
    else:
        logger.info('SES is not enabled; Skipping sending report email')


def bool_convert(s):
    return s == "true"


if __name__ == "__main__":
    send_email()
