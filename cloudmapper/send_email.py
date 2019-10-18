from ses.report import Report

def send_email():
    report = Report()
    report.generate_and_send_email()

if __name__ == "__main__":
    send_email()
