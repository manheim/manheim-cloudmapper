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
from manheim_cloudmapper.ses.ses import SES
from botocore.exceptions import ClientError

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, mock_open, ANY
else:
    from unittest.mock import patch, call, mock_open, ANY

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
        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
                patch('%s.open' % pbm, mock_open(read_data='foo'),
                      create=True) as m_open, \
                patch('%s.boto3.client' % pbm) as mock_boto:
            mock_boto.return_value.get_caller_identity.return_value = {
                'UserId': 'MyUID',
                'Arn': 'myARN',
                'Account': '1234567890'
            }
            cls = SES(region='us-east-1')
            cls.send_email(
                    sender='foo@maheim.com',
                    recipient='bar@manheim.com',
                    subject='foo',
                    body_text='body',
                    body_html='<html></html>',
                    attachments=['report.html'])

            mock_boto.assert_has_calls([
                call('ses', region_name='us-east-1'),
                call().send_raw_email(Destinations=['bar@manheim.com'],
                                      RawMessage={'Data': ANY},
                                      Source='foo@maheim.com')
            ])
            assert m_open.mock_calls == [
                call('report.html', 'rb'),
                call().read()
            ]
            mock_logger.assert_has_calls([
                call.info('Email sent!')
            ])
