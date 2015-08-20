"""
Plugin for use with 'lighting-automation' project
"""

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 127, 0),
    'orange': (255, 90, 0),
    'black': (0, 0, 0),
}
BUTTON_COLORS = tuple(COLORS[color] for color in ('red', 'green', 'yellow', 'blue', 'orange'))
LIGHT_INDEX = [0, 8, 16, 24, 32, 40, 48, 56, 64]

class DMXRendererPentatonicHero(AbstractDMXRenderer):
    __name__ = 'pentatonic_hero'  # The package name of network events that are to be directed to this class

    @staticmethod
    def set_color(dmx_universe, offset, data):
        for index, value in enumerate(data):
            dmx_universe[offset + index] = value

    def __init__(self):
        super().__init__()
        self.player_state = {1: set(), 2: set()}

    def render(self, frame):
        for input_num in range(1, 2):
            for button_num in range(5):
                if button_num in self.player_state[input_num]:
                    self.set_color(self.dmx_universe, LIGHT_INDEX[button_num], BUTTON_COLORS[button_num])
                else:
                    self.set_color(self.dmx_universe, LIGHT_INDEX[button_num], COLORS['black'])
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
