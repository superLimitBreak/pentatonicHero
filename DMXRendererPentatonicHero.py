"""
Plugin for use with 'lighting-automation' project
"""

from lighting import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


COLORS = {
    'red': (255, 0, 0),
    'green': (0, 72, 0),  # (0, 255, 0)
    'blue': (0, 0, 200),  # (0, 0, 255)
    'yellow': (255, 72, 0),  # (255, 255, 0),
    'orange': (255, 30, 0),
    'black': (0, 0, 0),
}
BUTTON_COLORS = tuple(COLORS[color] for color in ('green', 'red', 'yellow', 'blue', 'orange'))
LIGHT_INDEX = [0, 8, 16, 24, 32, 40, 48, 56, 64]
LIGHT_CONFIG = {
    1: [0, 16, 8],  # floor 2 - 77, 80, 83
    2: [40, 56, 48],  # floor 3 - 88, 91, 94
}


class DMXRendererPentatonicHero(AbstractDMXRenderer):
    __name__ = 'pentatonic_hero'  # The package name of network events that are to be directed to this class

    @staticmethod
    def set_color(dmx_universe, offset, color):
        for index, value in enumerate(color):
            dmx_universe[offset + index] = value

    @staticmethod
    def set_player_color(dmx_universe, input_num, color):
        for index in LIGHT_CONFIG[input_num]:
            DMXRendererPentatonicHero.set_color(dmx_universe, index, color)

    def __init__(self):
        super().__init__()
        self.player_state = {1: set(), 2: set()}

    def render(self, frame):
        for input_num in (1, 2):
            for button_num in range(5):
                if not self.player_state[input_num]:
                    self.set_player_color(self.dmx_universe, input_num, COLORS['black'])
                elif button_num in self.player_state[input_num]:
                    self.set_player_color(self.dmx_universe, input_num, BUTTON_COLORS[button_num])
                # Reference for old logic that activated differnt lights for each button
                #if button_num in self.player_state[input_num]:
                #    self.set_color(self.dmx_universe, LIGHT_INDEX[button_num], BUTTON_COLORS[button_num])
                #else:
                #    self.set_color(self.dmx_universe, LIGHT_INDEX[button_num], COLORS['black'])
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
