import os
import logging
import urllib3
import json

logger = logging.getLogger(__name__)

class PagerDutyV1():
    pd_url = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'

    def __init__(self, account_name=None, service_key=None, incident_key=None):
        """
        Initialize PagerDutyV1 provider.

        :param account_name: A name for the account that
          cloudmapper is currently running on, to use
          in the default incident_key and description
        :type account_name: str
        :param service_key: The PagerDuty Integration Key for
          sending events. Can also be specified with the
          ``PD_SERVICE_KEY`` environment variable.
        :type service_key: str
        :param incident_key: Optinal; The PagerDuty incident/routing key
          to use, for de-duplication and resolving alerts. This
          string will have any occurences of ``{{acount_name}}``
          replates with the account name
        :type incident_key: str
        """
        self._account_name = account_name

        if service_key is None:
            service_key = os.environ.get('PD_SERVICE_KEY', None)
        self._service_key = service_key
        
        if incident_key is None:
            incident_key = 'cloudmapper-' + account_name
        self._incident_key = incident_key

    def _send_event(self, service_key, payload):
        """
        Send an event to PagerDuty

        :param service_key: service_key to send to
        :type service_key: str
        :param payload: data to send with event
        :type payload: dict
        """
        payload['service_key'] = service_key
        http = urllib3.PoolManager()
        logger.info(
            'POSTing to PagerDuty Events API (%s): %s', self.pd_url, payload
        )
        encoded = json.dumps(payload, sort_keys=True).encode('utf-8')
        resp = http.request(
            'POST', self.pd_url,
            headers={'Content-type': 'application/json'},
            body=encoded
        )
        if resp.status == 200:
            logger.debug(
                'Successfully POSTed to PagerDuty; HTTP %d: %s',
                resp.status, resp.data
            )
            return
        raise RuntimeError(
            'ERROR creating PagerDuty Event; API responded HTTP %d: %s' % (
                resp.status, resp.data
            )
        )

    def _event_dict(self):
        """
        Return a skeleton dictionary for the PagerDuty V1 Event.
        :return: skeleton of Event
        :rtype: dict
        """
        d = {
            'incident_key': self._incident_key,
            'details': {},
            'client': 'cloudmapper'
        }
        if self._account_name is not None:
            d['details']['account_name'] = self._account_name
        return d

    def on_success(self):
        """
        Method called when no thresholds were breached, and run completed
        successfully. Should resolve any open incidents (if the service supports
        that functionality) or else simply return.
        :param duration: duration of the usage/threshold checking run
        :type duration: float
        """
        data = self._event_dict()
        data['event_type'] = 'resolve'
        data['description'] = 'cloudmapper in '
        if self._account_name is not None:
            data['description'] += self._account_name + ' found no problems'
        self._send_event(self._service_key, data)

    def on_failure(self, problem_str, exc=None):
        """
        Method called when the run encountered errors.
        :param problem_str: String representation of ``problems``.
          This is the list of publicly accessibel ports
        :type problem_str: str or None
        :param exc: Exception object that was raised during the run (optional)
        :type exc: Exception
        """
        data = self._event_dict()
        data['event_type'] = 'trigger'
        data['description'] = 'cloudmapper in '
        if self._account_name is not None:
            data['description'] += self._account_name + ' '
        if exc is not None:
            data['description'] += ' failed with an exception:' \
                                   ' %s' % exc.__repr__()
            data['details']['exception'] = exc.__repr__()
        else:
            data['description'] += 'had publicly accesible ports'
            data['details']['hosts_with_ports'] = problem_str
        self._send_event(self._service_key, data)
     