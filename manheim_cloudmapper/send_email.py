import os
from ses.report import Report


def send_email():
    if bool_convert(os.environ['SES_ENABLED']):
        Report().generate_and_send_email()


def bool_convert(s):
    return s == "true"

if __name__ == "__main__":
    send_email()
