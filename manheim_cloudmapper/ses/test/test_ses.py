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
import boto3

from manheim_cloudmapper.ses.ses import SES

pbm = 'manheim_cloudmapper.ses.ses'

class TestSES(object):

    def test_init(self):
        with patch('%s.boto3.client' % pbm) as mock_boto:
            cls = SES(region='us-east-1')
            assert cls.region == 'us-east-1'
            assert mock_boto.mock_calls == [
                call('ses', region_name='us-east-1')
            ]
        
    def test_send_email(self):
        with patch('%s.MIMEMultipart' % pbm) as mock_mimemultipart, \
             patch('%s.MIMEText' % pbm) as mock_mimetext, \
             patch('%s.MIMEApplication' % pbm) as mock_mimeapp, \
             patch('%s.ClientError' % pbm) as mock_clienterror, \
             patch('%s.open' % pbm, mock_open(read_data='<html>test</html>'), create=True) as m_open:
                cls = SES(region='us-east-1')
                cls.send_email(
                        sender='foo@maheim.com',
                        recipient='bar@manheim.com',
                        subject='foo',
                        body_text='body',
                        body_html='<html></html>',
                        attachments=['report.html'])
                assert mock_mimemultipart.mock_calls == [
                    call('mixed')
                ]
                assert m_open.mock_calls == [
                    call().open('report.hmtl', 'rb')
                ]
                
