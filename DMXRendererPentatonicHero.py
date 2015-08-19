"""
Plugin for use with 'lighting-automation' project
"""
import operator

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererPentatonicHero(AbstractDMXRenderer):
    __name__ = 'pentatonic_hero'  # The package name of network events that are to be directed to this class

    def __init__(self):
        super().__init__()
        self.player_state = {1: set(), 2: set()}

    def render(self, frame):
        for input_num in range(1, 2):
            for button_num in range(5):
                self.dmx_universe[8*button_num] = 255 if button_num in self.player_state[input_num] else 0
        return self.dmx_universe

    def event(self, data):
        """
        Update the stored button state
        """
        button_set = self.player_state[data['input']]
        event = data.get('event')
        button = data.get('button')
        if event == 'button_up':
            button_set.discard(button)
        if event == 'button_down':
            button_set.add(button)
