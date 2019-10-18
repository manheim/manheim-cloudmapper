import os
from port_check.portcheck import PortCheck

def check_bad_ports():
    # Get variables from env
    ok_ports        = list(os.getenv('OK_PORTS').split(","))
    account_name    = os.getenv('ACCOUNT')
    pc = PortCheck(ok_ports, account_name)
    pc.check_ports()

if __name__ == "__main__":
    check_bad_ports()
