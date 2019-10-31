# Copyright 2017-2019 Manheim / Cox Automotive
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from manheim_cloudmapper.ses.ses_report_sender import SesReportSender
from unittest.mock import patch, call, Mock, mock_open

pbm = 'manheim_cloudmapper.ses.ses_report_sender'


class TestInit(object):
    def test_all_options(self):
        with patch('%s.SES' % pbm) as m_ses:
            cls = SesReportSender(
                  report_source=(
                      '/opt/manheim_cloudmapper/web/account-data/report.html'
                  ),
                  account_name='foo',
                  sender='foo@maheim.com',
                  recipient='AWS SES <bar@manheim.com>',
                  region='us-east-1')
            assert cls.report_source == (
                '/opt/manheim_cloudmapper/web/account-data/report.html')
            assert cls.account_name == 'foo'
            assert cls.sender == 'foo@maheim.com'
            assert cls.recipient == 'AWS SES <bar@manheim.com>'
            assert cls.region == 'us-east-1'
            assert m_ses.mock_calls == [
                call('us-east-1')
            ]

    @patch.dict(
        'os.environ',
        {'ACCOUNT': 'foo',
         'SES_SENDER': 'foo@maheim.com',
         'SES_RECIPIENT': 'bar@manheim.com',
         'AWS_REGION': 'us-east-1'}, clear=True)
    def test_with_env(self):
        with patch('%s.SES' % pbm) as m_ses:
            cls = SesReportSender()
            assert cls.report_source == (
                '/opt/manheim_cloudmapper/web/account-data/report.html')
            assert cls.account_name == 'foo'
            assert cls.sender == 'foo@maheim.com'
            assert cls.recipient == 'AWS SES <bar@manheim.com>'
            assert cls.region == 'us-east-1'
            assert m_ses.mock_calls == [
                call('us-east-1')
            ]


class SesReportTester(object):

    @patch.dict(
        'os.environ',
        {'ACCOUNT': 'foo',
         'SES_SENDER': 'foo@maheim.com',
         'SES_RECIPIENT': 'bar@manheim.com',
         'AWS_REGION': 'us-east-1'}, clear=True)
    def setup(self):
        self.mock_ses = Mock()
        with patch('%s.SES' % pbm) as m_ses:
            m_ses.return_value = self.mock_ses
            self.cls = SesReportSender()


class TestGenerateAndSendEmail(SesReportTester):

    def test_generate_and_send_email_enabled(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
            patch('%s.open' % pbm, mock_open(read_data='foo'),
                  create=True) as m_open:

            cloudmapper_filename = datetime.datetime.now().strftime(
                'cloudmapper_report_%Y-%m-%d.html'
            )

            self.cls.generate_and_send_email()

            assert m_open.mock_calls == [
                call('/opt/manheim_cloudmapper/web/account-data/report.html',
                     'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
                call('/opt/manheim_cloudmapper/web/js/chart.js', 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
                call('/opt/manheim_cloudmapper/web/js/report.js', 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ]

            assert self.mock_ses.mock_calls == [
                call.send_email('foo@maheim.com', 'AWS SES <bar@manheim.com>',
                                '[cloudmapper foo] Cloudmapper audit findings',
                                'Please see the attached file for '
                                'cloudmapper results.',
                                '<html><head></head><body><p>foo'
                                '</p></body></html>',
                                {cloudmapper_filename:
                                 '<html><head></head><body><p>foo'
                                 '</p></body></html>'})
            ]

            assert mock_logger.mock_calls == [
                call.info("Sending SES Email.")
            ]


class TestJsReplace(SesReportTester):

    def test_js_replace(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            new_data = self.cls.js_replace(
                '<script src="../js/chart.js"></script>'
                '<script src="../js/report.js"></script>')

            assert new_data == '<script>foo</script><script>foo</script>'
            assert m_open.mock_calls == [
                call('/opt/manheim_cloudmapper/web/js/chart.js', 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
                call('/opt/manheim_cloudmapper/web/js/report.js', 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ]


class TestCssJsFix(SesReportTester):

    def test_css_js_fix(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            additional_css = """
.mytooltip:hover .tooltiptext {visibility:visible}
#chartjs-tooltip td {background-color: #fff}
#chartjs-tooltip table {box-shadow: 5px 10px 8px #888888}
table {border-collapse:collapse;}
table, td, th {border:1px solid black; padding: 1px;}
th {background-color: #ddd; text-align: center;}"""

            new_data = self.cls.css_js_fix(
                '.mytooltip:hover .tooltiptext {visibility:visible}'
            )

            assert new_data == additional_css

            assert m_open.mock_calls == [
            ]
