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

import sys
import datetime
from manheim_cloudmapper.ses.report import Report

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, mock_open
else:
    from unittest.mock import patch, call, Mock, mock_open

pbm = 'manheim_cloudmapper.ses.report'


class TestInit(object):
    def test_all_options(self):
        with patch('%s.SES' % pbm) as m_ses:
            cls = Report(
                  report_source='/opt/cloudmapper/web/account-data/report.html',
                  account_name='foo',
                  sender='foo@maheim.com',
                  recipient='AWS SES <bar@manheim.com>',
                  region='us-east-1',
                  ses_enabled='true')
            assert cls.report_source == (
                '/opt/cloudmapper/web/account-data/report.html')
            assert cls.account_name == 'foo'
            assert cls.sender == 'foo@maheim.com'
            assert cls.recipient == 'AWS SES <bar@manheim.com>'
            assert cls.region == 'us-east-1'
            assert cls.ses_enabled == 'true'
            assert m_ses.mock_calls == [
                call('us-east-1')
            ]

    @patch.dict(
        'os.environ',
        {'ACCOUNT': 'foo',
         'SES_SENDER': 'foo@maheim.com',
         'SES_RECIPIENT': 'bar@manheim.com',
         'AWS_REGION': 'us-east-1',
         'SES_ENABLED': 'true'}, clear=True)
    def test_with_env(self):
        with patch('%s.SES' % pbm) as m_ses:
            cls = Report()
            assert cls.report_source == (
                '/opt/cloudmapper/web/account-data/report.html')
            assert cls.account_name == 'foo'
            assert cls.sender == 'foo@maheim.com'
            assert cls.recipient == 'AWS SES <bar@manheim.com>'
            assert cls.region == 'us-east-1'
            assert cls.ses_enabled == 'true'
            assert m_ses.mock_calls == [
                call('us-east-1')
            ]


class ReportTester(object):

    @patch.dict(
        'os.environ',
        {'ACCOUNT': 'foo',
         'SES_SENDER': 'foo@maheim.com',
         'SES_RECIPIENT': 'bar@manheim.com',
         'AWS_REGION': 'us-east-1',
         'SES_ENABLED': 'true'}, clear=True)
    def setup(self):
        self.mock_ses = Mock()
        with patch('%s.SES' % pbm) as m_ses:
            m_ses.return_value = self.mock_ses
            self.cls = Report()


class TestGenerateAndSendEmail(ReportTester):

    def test_generate_and_send_email_disabled(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
            patch('%s.open' % pbm, mock_open(read_data='foo'),
                  create=True) as m_open:

            self.cls.ses_enabled = "false"
            self.cls.generate_and_send_email()

            assert mock_logger.mock_calls == [
                call.info("Skipping Cloudmapper SES Email"
                          " send because SES is not enabled.")
            ]
            assert m_open.mock_calls == []
            assert self.mock_ses.mock_calls == []

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
                call('/opt/cloudmapper/web/account-data/report.html', 'r'),
                call().read(),
                call().close(),
                call('/opt/cloudmapper/web/js/chart.js', 'r'),
                call().read(),
                call().close(),
                call('/opt/cloudmapper/web/js/report.js', 'r'),
                call().read(),
                call().close(),
                call('/opt/cloudmapper/web/account-data/report.html', 'w'),
                call().write('foo'),
                call().close(),
                call('/opt/cloudmapper/web/account-data/report.html', 'r'),
                call().__enter__(),
                call('/opt/cloudmapper/' + cloudmapper_filename, 'w+'),
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


class TestJsReplace(ReportTester):

    def test_js_replace(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            self.cls.js_replace('/opt/cloudmapper/web/account-data/report.html')

            assert m_open.mock_calls == [
                call('/opt/cloudmapper/web/account-data/report.html', 'r'),
                call().read(),
                call().close(),
                call('/opt/cloudmapper/web/js/chart.js', 'r'),
                call().read(),
                call().close(),
                call('/opt/cloudmapper/web/js/report.js', 'r'),
                call().read(),
                call().close(),
                call('/opt/cloudmapper/web/account-data/report.html', 'w'),
                call().write('foo'),
                call().close()
            ]


class TestCssJsFix(ReportTester):

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


class TestPremailerTransform(ReportTester):

    def test_premailer_transform(self):
        with patch('%s.open' % pbm, mock_open(read_data='foo'),
                   create=True) as m_open:

            now = datetime.datetime.now()
            cloudmapper_filename = ('cloudmapper_report_' + str(now.year) +
                                    '-' + str(now.month) + '-' + str(now.day) +
                                    '.html')

            self.cls.premailer_transform(
                '/opt/cloudmapper/web/account-data/report.html')

            assert m_open.mock_calls == [
                call('/opt/cloudmapper/web/account-data/report.html', 'r'),
                call().__enter__(),
                call('/opt/cloudmapper/' + cloudmapper_filename, 'w+'),
                call().__enter__(),
                call().read(),
                call().write('<html><head></head><body><p>foo'
                             '</p></body></html>'),
                call().__exit__(None, None, None),
                call().__exit__(None, None, None)
            ]
