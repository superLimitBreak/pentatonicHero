import socket
import json
import traceback

import logging
log = logging.getLogger(__name__)


# Constants --------------------------------------------------------------------

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9872


# Null Handler -----------------------------------------------------------------

class DisplayEventHandlerNull(object):
    def event(self, *args, **kwargs):
        pass


# Network Display --------------------------------------------------------------

class DisplayEventHandler(object):

    @staticmethod
    def factory(*args, **kwargs):
        try:
            return DisplayEventHandler(*args, **kwargs)
        except Exception:
            log.warn('unable to setup network display {0} {1}'.format(args, kwargs))
            traceback.print_exc()
            return DisplayEventHandlerNull()

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        log.debug('Setup network socket {0}:{1}'.format(host, port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, int(port)))

    def event(self, input_identifyer, event, **params):
        log.debug('Input: {0}, Event: {1},  Value: {2}'.format(input_identifyer, event, params))
        data = {
            'func': 'penatonic_hero.event',
            'input': input_identifyer,
            'event': event,
        }
        data.update(params)
        self.socket.sendall((json.dumps(data)+'\n').encode('utf-8'))
