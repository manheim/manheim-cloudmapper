import sys
from manheim_cloudmapper.port_check.portcheck import PortCheck

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
        self.mock_pd = Mock()
        with patch('%s.PagerDutyV1' % pbm) as m_pd:
            m_pd.return_value = self.mock_pd
            self.cls = PortCheck('80,443', 'aName')


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
        json_data = ('[{"account": "acct","arn": "abc123","hostname": '
                     '"abc123.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443,22,1999","type": "apigateway"},'
                     '{"account": "acct","arn": "abc567","hostname": '
                     '"abc567.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443,22,1999","type": "apigateway"},'
                     '{"account": "acct","arn": "abc890","hostname": '
                     '"abc890.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443,22,1999","type": "apigateway"}]')

        with patch('%s.open' % pbm,
                   mock_open(read_data=json_data), create=True) as m_open:

            self.cls.check_ports()

            m_open.assert_has_calls([
                call('aName.json', 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ])

            problem_str = ("acct\tapigateway\t"
                           "abc123.execute-api.us-east-1.amazonaws.com\t"
                           "b'22,1999'\tabc123\n"
                           "acct\tapigateway\t"
                           "abc567.execute-api.us-east-1.amazonaws.com\t"
                           "b'22,1999'\tabc567\n"
                           "acct\tapigateway\t"
                           "abc890.execute-api.us-east-1.amazonaws.com\t"
                           "b'22,1999'\tabc890\n")
            assert self.mock_pd.mock_calls == [
                call.on_failure(problem_str)
            ]

    def test_check_bad_ports_empty(self):
        json_data = ('[{"account": "acct","arn": "abc123","hostname": '
                     '"abc123.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443","type": "apigateway"},'
                     '{"account": "acct","arn": "abc567","hostname": '
                     '"abc567.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443","type": "apigateway"},'
                     '{"account": "acct","arn": "abc890","hostname": '
                     '"abc890.execute-api.us-east-1.amazonaws.com",'
                     '"ports": "80,443","type": "apigateway"}]')

        with patch('%s.open' % pbm,
                   mock_open(read_data=json_data), create=True) as m_open:

            self.cls.check_ports()

            m_open.assert_has_calls([
                call('aName.json', 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ])

            assert self.mock_pd.mock_calls == [
                call.on_success()
            ]
