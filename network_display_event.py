DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9872

import logging
log = logging.getLogger(__name__)


class DisplayEventHandlerNull(object):
    def event(self, *args, **kwargs):
        pass


class DisplayEventHandler(object):

    @staticmethod
    def factory(*args, **kwargs):
        try:
            return DisplayEventHandler(*args, **kwargs)
        except Exception:
            log.warn('unable to setup network display')
            return DisplayEventHandlerNull()

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        log.debug('Setup network socket {0}:{1}'.format(host, port))
        #self.socket = ;

    def event(self, input_identifyer, function_name, value):
        log.debug('Input: {0}, Event: {1},  Value: {2}'.format(input_identifyer, function_name, value))
