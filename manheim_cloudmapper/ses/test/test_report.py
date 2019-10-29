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

pbm = 'manheim_cloudmapper.ses.report'


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

            now = datetime.datetime.now()
            cloudmapper_filename = ('cloudmapper_report_' + str(now.year) +
                                    '-' + str(now.month) + '-' + str(now.day) +
                                    '.html')

            self.cls.generate_and_send_email()

            assert m_open.mock_calls == [
                call(
                    '/opt/manheim_cloudmapper/web/account-data/report.html',
                    'r'
                ),
                call().read(),
                call().close(),
                call('/opt/manheim_cloudmapper/web/js/chart.js', 'r'),
                call().read(),
                call().close(),
                call('/opt/manheim_cloudmapper/web/js/report.js', 'r'),
                call().read(),
                call().close(),
                call(
                    '/opt/manheim_cloudmapper/web/account-data/report.html',
                    'w'
                ),
                call().write('foo'),
                call().close(),
                call(
                    '/opt/manheim_cloudmapper/web/account-data/report.html',
                    'r'
                ),
                call().__enter__(),
                call('/opt/manheim_cloudmapper/' + cloudmapper_filename, 'w+'),
                call().__enter__(),
                call().read(),
                call().write('<html><head></head><body><p>foo'
                             '</p></body></html>'),
                call().__exit__(None, None, None),
                call().__exit__(None, None, None),
                call(cloudmapper_filename, 'r'),
                call().read(),
                call().close(),
                call(cloudmapper_filename, 'w'),
                call().write('foo'),
                call().close(),
                call(cloudmapper_filename, 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ]

            assert self.mock_ses.mock_calls == [
                call.send_email('foo@maheim.com', 'AWS SES <bar@manheim.com>',
                                '[cloudmapper foo] Cloudmapper audit findings',
                                'Please see the attached file for '
                                'cloudmapper results.',
                                'foo', [cloudmapper_filename])
            ]

            assert mock_logger.mock_calls == [
                call.info("Sending SES Email.")
            ]


class TestJsReplace(SesReportTester):

    def test_js_replace(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            self.cls.js_replace()

            assert m_open.mock_calls == [
                call(
                    '/opt/manheim_cloudmapper/web/account-data/report.html',
                    'r'
                ),
                call().read(),
                call().close(),
                call('/opt/manheim_cloudmapper/web/js/chart.js', 'r'),
                call().read(),
                call().close(),
                call('/opt/manheim_cloudmapper/web/js/report.js', 'r'),
                call().read(),
                call().close(),
                call(
                    '/opt/manheim_cloudmapper/web/account-data/report.html',
                    'w'
                ),
                call().write('foo'),
                call().close()
            ]


class TestCssJsFix(SesReportTester):

    def test_css_js_fix(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            now = datetime.datetime.now()
            cloudmapper_filename = ('cloudmapper_report_' + str(now.year) +
                                    '-' + str(now.month) + '-' + str(now.day) +
                                    '.html')

            self.cls.css_js_fix(cloudmapper_filename)

            assert m_open.mock_calls == [
                call(cloudmapper_filename, 'r'),
                call().read(),
                call().close(),
                call(cloudmapper_filename, 'w'),
                call().write('foo'),
                call().close()
            ]


class TestPremailerTransform(SesReportTester):

    def test_premailer_transform(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            now = datetime.datetime.now()
            cloudmapper_filename = ('cloudmapper_report_' + str(now.year) +
                                    '-' + str(now.month) + '-' + str(now.day) +
                                    '.html')

            self.cls.premailer_transform()

            assert m_open.mock_calls == [
                call(
                    '/opt/manheim_cloudmapper/web/account-data/report.html',
                    'r'
                ),
                call().__enter__(),
                call('/opt/manheim_cloudmapper/' + cloudmapper_filename, 'w+'),
                call().__enter__(),
                call().read(),
                call().write('<html><head></head><body><p>foo'
                             '</p></body></html>'),
                call().__exit__(None, None, None),
                call().__exit__(None, None, None)
            ]
