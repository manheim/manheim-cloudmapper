import os
from .port_check.portcheck import PortCheck


def check_bad_ports():
    PortCheck(
        os.getenv('OK_PORTS').split(","),
        os.getenv('ACCOUNT')
    ).check_ports()


if __name__ == "__main__":
    check_bad_ports()
