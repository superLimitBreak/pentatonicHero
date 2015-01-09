import socket
import json
import datetime

import logging
log = logging.getLogger(__name__)

# Constants --------------------------------------------------------------------

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9872
DEFAULT_RECONNECT_TIMEOUT = datetime.timedelta(seconds=5)


# Null Handler -----------------------------------------------------------------

class DisplayEventHandlerNull(object):

    def event(self, *args, **kwargs):
        log.debug(args)
        pass

    def close(self):
        pass


# Network Display --------------------------------------------------------------

class DisplayEventHandler(object):

    @staticmethod
    def factory(*args, **kwargs):
        try:
            return DisplayEventHandler(*args, **kwargs)
        except socket.error:
            log.warn('Unable to setup TCP network socket {0} {1}'.format(args, kwargs))
            return DisplayEventHandlerNull()

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, reconnect_timeout=DEFAULT_RECONNECT_TIMEOUT):
        self.host = host
        self.port = int(port)
        self.reconnect_timout = reconnect_timeout
        self.socket_connected_attempted_timestamp = None
        self._connect()

    def _connect(self):
        log.debug('Attempting connect TCP network socket {0}:{1}'.format(self.host, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def _reconnect(self):
        # Don't try to connect if the last connection attempt was very recent
        if self.socket_connected_attempted_timestamp is not None and self.socket_connected_attempted_timestamp > datetime.datetime.now() - self.reconnect_timeout:
            return
        # Ensure existing socket is closed
        self.close()
        # Attempt new connection
        try:
            self._connect()
        except socket.error:  # ConnectionRefusedError:
            log.debug('Failed to reconnect')
            self.socket_connected_attempted_timestamp = datetime.datetime.now()

    def close(self):
        try:
            self.socket.close()
        except Exception:
            pass

    def event(self, func_name, **params):
        data = {
            'func': func_name,
        }
        data.update(params)
        data = (json.dumps(data)+'\n').encode('utf-8')
        try:
            self.socket.sendall(data)
        except socket.error:  # BrokenPipeError
            # The data send has failed - for such a transient event we have to just loose the data
            # but we should try to reconnect for the next potential send
            self._reconnect()
