import os
from manheim_cloudmapper.ses.ses_report_sender import SesReportSender


def send_email():
    if bool_convert(os.environ['SES_ENABLED']):
        SesReportSender().generate_and_send_email()


def bool_convert(s):
    return s == "true"


if __name__ == "__main__":
    send_email()
