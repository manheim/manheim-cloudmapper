import os
import datetime
import logging
from premailer import transform
from .ses import SES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SesReportSender():

    # Base path for CSS stylings, default for cloudmapper
    BASE_PATH = '/opt/manheim_cloudmapper/web/css'

    def __init__(self,
                 report_source=(
                     '/opt/manheim_cloudmapper/web/account-data/report.html'
                 ),
                 account_name=None, sender=None, recipient=None,
                 region=None):
        """
        Initialize the Cloudmapper report. Sets variables for email.

        :param account_name: AWS account name
        :type account_name: str
        :param sender: Email address registered to SES that will send emails
        :type sender: str
        :param recipient: Email address to send emails to
        :type recipient: str
        :param region: AWS Region
        :type region: str
        """

        self.report_source = report_source
        if account_name is None:
            account_name = os.environ['ACCOUNT']

        if sender is None:
            sender = os.environ['SES_SENDER']

        if recipient is None:
            recipient = ('AWS SES <' +
                         os.environ['SES_RECIPIENT'] + '>')

        if region is None:
            region = os.environ['AWS_REGION']

        self.account_name = account_name
        self.sender = sender
        self.recipient = recipient
        self.region = region

        self.ses = SES(self.region)

    def generate_and_send_email(self):
        """
        Generate Cloudmapper Email and send via AWS SES

        Transformations are done on the report.html file
        to support CSS and JS functionality
        """

        subject = (f'[cloudmapper {self.account_name}]'
                   ' Cloudmapper audit findings')
        body_text = 'Please see the attached file for cloudmapper results.'

        with open(self.report_source, 'r') as f_in:
            html_data = f_in.read()

        # Inject JS file contents into HTML
        html_data = self.js_replace(html_data)

        # Run premailer transformation to inject CSS data directly in HTML
        html_data = transform(html_data, base_path=self.BASE_PATH)

        # Fix CSS post-premailer
        html_data = self.css_js_fix(html_data)

        cloudmapper_filename = datetime.datetime.now().strftime(
            'cloudmapper_report_%Y-%m-%d.html'
        )

        attachments = {cloudmapper_filename: html_data}
        logger.info("Sending SES Email.")
        self.ses.send_email(self.sender, self.recipient,
                            subject, body_text, html_data, attachments)

    def js_replace(self, html_data):
        """
        Replaces js source file tags with js file contents.
        This allows the html to contain all data needed for the report
        with no additional links, etc.

        :param source: Filepath to report.html
        :type source: str
        """

        with open('/opt/manheim_cloudmapper/web/js/chart.js', 'r') as chart_js:
            chart_js_data = chart_js.read()

        with open('/opt/manheim_cloudmapper/web/js/report.js',
                  'r') as report_js:
            report_js_data = report_js.read()

        chart_needle = '<script src="../js/chart.js"></script>'
        report_needle = '<script src="../js/report.js"></script>'
        new_html_data = html_data.replace(chart_needle,
                                          '<script>' + chart_js_data +
                                          '</script>')
        new_html_data = new_html_data.replace(report_needle,
                                              '<script>' + report_js_data +
                                              '</script>')

        return new_html_data

    def css_js_fix(self, html_data):
        """
        Adds additional CSS to support formatting of JS tables
        Premailer has a hard time evaluating the CSS on JS componenets
        This fixes the background on js pop-up tables.

        :param source: Filepath to report.html
        :type source: str
        """

        additional_css = """
.mytooltip:hover .tooltiptext {visibility:visible}
#chartjs-tooltip td {background-color: #fff}
#chartjs-tooltip table {box-shadow: 5px 10px 8px #888888}
table {border-collapse:collapse;}
table, td, th {border:1px solid black; padding: 1px;}
th {background-color: #ddd; text-align: center;}"""

        tooltip_needle = '.mytooltip:hover .tooltiptext {visibility:visible}'
        new_html_data = html_data.replace(tooltip_needle, additional_css)

        return new_html_data
