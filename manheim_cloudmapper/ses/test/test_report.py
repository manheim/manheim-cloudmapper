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

from mock import patch, call, Mock, mock_open
import pytest
import yaml
import os

from manheim_cloudmapper.ses.report import Report

pbm = 'manheim_cloudmapper.ses.report'

class TestReport(object):

    def test_init(self):
        cls = Report(
                report_source='/opt/cloudmapper/web/account-data/report.html',
                account_name='foo',
                sender='foo@maheim.com', recipient='bar@manheim.com',
                region='us-east-1',
                ses_enabled='true')
        assert cls.report_source == '/opt/cloudmapper/web/account-data/report.html'
        assert cls.account_name == 'foo'
        assert cls.sender == 'foo@maheim.com'
        assert cls.recipient == 'bar@manheim.com'
        assert cls.region == 'us-east-1'
        assert cls.ses_enabled == 'true'
    
    def test_init_with_env(self):
        with patch.dict(os.environ, {
                'ACCOUNT': 'foo',
                'SES_SENDER': 'foo@maheim.com',
                'SES_RECIPIENT': 'bar@manheim.com',
                'AWS_REGION': 'us-east-1',
                'SES_ENABLED': 'true'
            }, clear=True):
                cls = Report()
        assert cls.report_source == '/opt/cloudmapper/web/account-data/report.html'
        assert cls.account_name == 'foo'
        assert cls.sender == 'foo@maheim.com'
        assert cls.recipient == 'AWS SES <bar@manheim.com>'
        assert cls.region == 'us-east-1'
        assert cls.ses_enabled == 'true'
    
    #def test_generate_and_send_email(self):
    #    with patch('%s.logger' % pbm, autospec=True) as mock_logger:
