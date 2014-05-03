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
        axis_pitch_bend=None,  # Pitch bending is optional as keyboard inputs dont support this
        axis_strum=None,  # Some controlers have axis change as a strum
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
    if axis_pitch_bend:
        control_config += (InputEvent(pygame.JOYAXISMOTION, 'axis', axis_pitch_bend, 'ctrl_pitch_bend', ()),)
    if axis_strum:
        control_config += (InputEvent(pygame.JOYAXISMOTION, 'axis', axis_strum, 'ctrl_strum', ()),)
    return control_config


# Control Definitions ----------------------------------------------------------

null_input = ()

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
    button_strum=7,
    button_transpose_increment=8,
    button_transpose_decrement=9,
    button_notes=(5, 1, 0, 2, 3),
    axis_pitch_bend=1,
    axis_strum=3,
)

joy2_input = ()
