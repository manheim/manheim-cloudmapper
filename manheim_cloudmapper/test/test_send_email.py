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


from manheim_cloudmapper.send_email import send_email, bool_convert
from unittest.mock import patch, call

pbm = 'manheim_cloudmapper.send_email'


class TestSendEmail(object):

    @patch.dict(
        'os.environ',
        {'SES_ENABLED': 'true'},
        clear=True)
    def test_send_email_enabled(self):
        with patch('%s.SesReportSender' % pbm) as m_ses:
            send_email()

            assert m_ses.mock_calls == [
                call(),
                call().generate_and_send_email()
            ]

    @patch.dict(
        'os.environ',
        {'SES_ENABLED': 'false'},
        clear=True)
    def test_send_email_disabled(self):
        with patch('%s.SesReportSender' % pbm) as m_ses:
            send_email()

            assert m_ses.mock_calls == []

    def test_bool_convert_true(self):
        res = bool_convert("true")
        assert res is True

    def test_bool_convert_false(self):
        res = bool_convert("false")
        assert res is False
