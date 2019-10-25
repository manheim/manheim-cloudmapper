import sys
import os
from manheim_cloudmapper.port_check.portcheck import PortCheck
from manheim_cloudmapper.port_check.pagerdutyv1 import PagerDutyV1

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, mock_open
else:
    from unittest.mock import patch, call, Mock, mock_open

pbm = 'manheim_cloudmapper.port_check.portcheck'
pb = '%s.PortCheck' % pbm

pd = 'manheim_cloudmapper.port_check.pagerdutyv1'
pds = '%s.PagerDutyV1' % pd


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
            self.cls.filename_in = 'aName.json'
            self.cls.pd = PagerDutyV1('aName')


class TestGetBadPorts(PortCheckTester):

    def test_get_bad_ports(self):
        bad_ports = self.cls.get_bad_ports(
            '80,443,1999,22,80,432,12435,443'.split(','))
        assert bad_ports == '1999,22,432,12435'

    def test_get_bad_ports_empty(self):
        bad_ports = self.cls.get_bad_ports('80,443'.split(','))
        assert bad_ports == ''


class TestCheckBadPorts(PortCheckTester):

    def test_check_bad_ports(self):
        # mock_http = Mock()
        # mock_resp = Mock(
        #    status=200, data='{"status": "success", "message": '
        #                     '"Event processed", "incident_key":'
        #                     ' "iKey"}'
        # )
        # mock_http.request.return_value = mock_resp
        json_data = ('[{"account": "acct","arn": "abc123","hostname": '
                     '"abc123.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443,22,1999","type": "apigateway"},'
                     '{"account": "acct","arn": "abc567","hostname": '
                     '"abc567.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443,22,1999","type": "apigateway"},'
                     '{"account": "acct","arn": "abc890","hostname": '
                     '"abc890.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443,22,1999","type": "apigateway"}]')
        csv_data = ('acct,apigateway,'
                    'abc123.execute-api.us-east-1.amazonaws.com,'
                    '"80,443,22,1999",abc123\n'
                    'acct,apigateway,'
                    'abc567.execute-api.us-east-1.amazonaws.com,'
                    '"80,443,22,1999",abc567\n'
                    'acct,apigateway,'
                    'abc890.execute-api.us-east-1.amazonaws.com,'
                    '"80,443,22,1999",abc890')

        mock_pd = Mock()
        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
                patch('%s.PagerDutyV1' % pbm, autospec=True) as m_pd, \
                patch('%s.open' % pbm,
                      mock_open(read_data=json_data), create=True) as m_open:

            # mock_pm.return_value = mock_http
            m_pd.return_value = mock_pd
            m_open.side_effect = (m_open.return_value,
                                  mock_open(read_data=csv_data).return_value)

            self.cls.check_ports()

            m_open.assert_has_calls([
                call('aName.json', 'r'),
                call().__enter__(),
                call().read(),
                call('aName.csv'),
                call().__exit__(None, None, None)
            ])

            mock_logger.assert_has_calls([
                call.info("acct\tapigateway\t"
                          "abc123.execute-api.us-east-1.amazonaws.com\t"
                          "b'22,1999'\tabc123"),
                call.info("acct\tapigateway\t"
                          "abc567.execute-api.us-east-1.amazonaws.com\t"
                          "b'22,1999'\tabc567"),
                call.info("acct\tapigateway\t"
                          "abc890.execute-api.us-east-1.amazonaws.com\t"
                          "b'22,1999'\tabc890")
            ])

            os.remove('aName.csv')

    def test_check_bad_ports_empty(self):
        mock_http = Mock()
        mock_resp = Mock(
            status=200, data='{"status": "success", "message": '
                             '"Event processed", "incident_key":'
                             ' "iKey"}'
        )
        mock_http.request.return_value = mock_resp
        json_data = ('[{"account": "acct","arn": "abc123","hostname": '
                     '"abc123.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443","type": "apigateway"},'
                     '{"account": "acct","arn": "abc567","hostname": '
                     '"abc567.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443","type": "apigateway"},'
                     '{"account": "acct","arn": "abc890","hostname": '
                     '"abc890.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443","type": "apigateway"}]')
        csv_data = ('acct,apigateway,'
                    'abc123.execute-api.us-east-1.amazonaws.com,'
                    '"80,443",abc123\n'
                    'acct,apigateway,'
                    'abc567.execute-api.us-east-1.amazonaws.com,'
                    '"80,443",abc567\n'
                    'acct,apigateway,'
                    'abc890.execute-api.us-east-1.amazonaws.com,'
                    '"80,443",abc890')

        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
                patch('%s.urllib3.PoolManager' % pd) as mock_pm, \
                patch('%s.open' % pbm,
                      mock_open(read_data=json_data), create=True) as m_open:

            mock_pm.return_value = mock_http
            m_open.side_effect = (m_open.return_value,
                                  mock_open(read_data=csv_data).return_value)

            self.cls.check_ports()

            m_open.assert_has_calls([
                call('aName.json', 'r'),
                call().__enter__(),
                call().read(),
                call('aName.csv'),
                call().__exit__(None, None, None)
            ])

            mock_logger.assert_has_calls([])

            os.remove('aName.csv')
