from ses.report import Report


def send_email():
    Report().generate_and_send_email()


if __name__ == "__main__":
    send_email()
