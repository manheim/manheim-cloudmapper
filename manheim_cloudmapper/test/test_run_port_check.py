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


from manheim_cloudmapper.run_port_check import check_bad_ports
from unittest.mock import patch, call

pbm = 'manheim_cloudmapper.run_port_check'

class TestRunPortCheck(object):

    @patch.dict(
        'os.environ',
        {'OK_PORTS': '80,443',
         'ACCOUT': 'acct'},
        clear=True)
    def test_check_bad_ports(self):
        with patch('%s.PortCheck' % pbm) as m_pc:
            check_bad_ports()

            assert m_pc.mock_calls == [
                call(['80', '443'], None),
                call().check_ports()
            ]
