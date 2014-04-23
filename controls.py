""" Pentatonic Hero - Control definitons """

# Imports ----------------------------------------------------------------------

from collections import namedtuple
from itertools import chain

import pygame

# Exports ----------------------------------------------------------------------

__all__ = ('key_input', 'joy1_input', 'joy2_input')


# Factory ----------------------------------------------------------------------

InputEvent = namedtuple('InputEvent', ['type', 'attr', 'value', 'event_func_name', 'event_func_args'])


def _hero_control_factory(
        event_type,
        event_down,
        event_up,
        button_strum,
        button_transpose_increment,
        button_transpose_decrement,
        button_notes,
        pitch_bend_axis=None,  # Pitch bending is optional as keyboard inputs dont support this
    ):
    def _button_note(button_index, event_value):
        return (
            InputEvent(event_down, event_type, event_value, 'ctrl_note_down', (button_index,)),
            InputEvent(event_up, event_type, event_value, 'ctrl_note_up', (button_index,)),
        )
    control_config = (
        InputEvent(event_down, event_type, button_strum, 'ctrl_strum', ()),
        InputEvent(event_down, event_type, button_transpose_increment, 'ctrl_transpose_increment', ()),
        InputEvent(event_down, event_type, button_transpose_decrement, 'ctrl_transpose_decrement', ()),
    ) + tuple(chain(*(_button_note(button_index, event_value) for button_index, event_value in enumerate(button_notes))))
    if pitch_bend_axis:
        control_config += (InputEvent(pygame.JOYAXISMOTION, 'axis', pitch_bend_axis, 'ctrl_pitch_bend', ()),)
    return control_config


# Control Definitions ----------------------------------------------------------

key_input = _hero_control_factory(
    event_type='key',
    event_down=pygame.KEYDOWN,
    event_up=pygame.KEYUP,
    button_strum=pygame.K_SPACE,
    button_transpose_increment=pygame.K_p,
    button_transpose_decrement=pygame.K_o,
    button_notes=(
        pygame.K_q,
        pygame.K_w,
        pygame.K_e,
        pygame.K_r,
        pygame.K_t,
    ),
)

joy1_input = _hero_control_factory(
    event_type='button',
    event_down=pygame.JOYBUTTONDOWN,
    event_up=pygame.JOYBUTTONUP,
    button_strum=6,
    button_transpose_increment=7,
    button_transpose_decrement=8,
    button_notes=(1, 2, 3, 4, 5),
    pitch_bend_axis=1,
)

joy2_input = None
