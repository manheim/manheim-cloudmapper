import sys
import os
import pytest
from manheim_cloudmapper.port_check.portcheck import PortCheck
from manheim_cloudmapper.port_check.pagerdutyv1 import PagerDutyV1

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, mock_open, DEFAULT
else:
    from unittest.mock import patch, call, Mock, mock_open, DEFAULT

pbm = 'manheim_cloudmapper.port_check.portcheck'
pb = '%s.PortCheck' % pbm

class TestInit(object):

    @patch.dict(
        'os.environ',
        {'PD_SERVICE_KEY': 'cKey'},
        clear=True
    )
    def test_all_options(self):
        cls = PortCheck(ok_ports='80,443', account_name='aName')
        assert cls.ok_ports == '80,443'
        assert cls.account_name == 'aName'
        assert cls.filename_in == 'aName.json'

class PortCheckTester(object):

    @patch.dict(
        'os.environ',
        {'PD_SERVICE_KEY': '123456789012345678901234567890ab'},
        clear=True
    )
    def setup(self):
        with patch('%s.__init__' % pb) as m_init:
            m_init.return_value = None
            self.cls = PortCheck('80,443', 'aName')
            self.cls.ok_ports = '80,443'
            self.cls.account_name = 'aName'
            self.cls.filename_in= 'aName.json'
            self.cls.pd = PagerDutyV1('aName')

class TestGetBadPorts(PortCheckTester):

    def test_get_bad_ports(self):
        bad_ports = self.cls.get_bad_ports('80,443,1999,22,80,432,12435,443'.split(','))
        assert bad_ports == '1999,22,432,12435'

    def test_get_bad_ports_empty(self):
        bad_ports = self.cls.get_bad_ports('80,443'.split(','))
        assert bad_ports == ''

class TestCheckBadPorts(PortCheckTester):

    def test_check_bad_ports(self):
        json_data = '{"account": "acct", "type": "test", "hostname": "host.name.aws.com", "ports": ["80","443", "1999"], "arn": "fdsad132"}\n'
        csv_data = 'account,type,hostname,ports,arn\nacct,test,host.name.aws.com,80,443,1999,fdsad132\n'

        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
            patch('%s.open' % pbm, mock_open(), create=True) as m_open:

            with open('aName.json', 'w') as json:
                json.write(json_data)
            with open('aName.csv', 'w') as csv:
                csv.write(csv_data)

            
            self.cls.check_ports()

            m_open.assert_has_calls([
                call('aName.json', 'r'),
                call().__enter__(),
                call().read(),
                call('aName.csv'),
                call().__enter__()
            ])

            mock_logger.assert_has_calls([
                call.info('{"account": "acct"\t "type": "test"\t "hostname": "host.name.aws.com"\tb\' "ports": [80\'\t443]')
            ])

            #os.remove('aName.json')
            #os.remove('aName.csv')

