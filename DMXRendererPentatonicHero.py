"""
Plugin for use with 'lighting-automation' project
"""

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererPentatonicHero(AbstractDMXRenderer):

    __name__ = 'pentatonic_hero'

    def __init__(self):
        super().__init__()

    def render(self, frame):
        # do stuff
        return self.dmx_universe

    def event(self, data):
        """
        Network event
        """
        print(data)
