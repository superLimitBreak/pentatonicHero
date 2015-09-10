""" Pentatonic Hero - Control definitons """

# Imports ----------------------------------------------------------------------
import pygame

__all__ = ('keyboard', 'ps3_joy1', 'ps3_joy2', 'ps2_joy1', 'ps2_joy2')

null_input = lambda event, control_methods: None


def _ps3_joy(joystick_number):
    button_lookup = {button: index for index, button in enumerate((1, 2, 0, 3, 4))}
    transpose_increment = 8
    transpose_decrement = 9
    pitch_bend_axis = 2

    def input_event_processor(event, control_methods):
        if getattr(event, 'joy', None) != joystick_number:
            return
        # Buttons
        if event.type == pygame.JOYBUTTONDOWN and event.button in button_lookup:
            control_methods['note_down'](button_lookup[event.button])
            return
        if event.type == pygame.JOYBUTTONUP and event.button in button_lookup:
            control_methods['note_up'](button_lookup[event.button])
            return
        # Strum
        if event.type == pygame.JOYHATMOTION:
            if event.value[1] == 1 or event.value[1] == -1:
                control_methods['strum']()
                return
        # Transpose
        if event.type == pygame.JOYBUTTONDOWN and event.button == transpose_increment:
            control_methods['transpose_increment']()
            return
        if event.type == pygame.JOYBUTTONDOWN and event.button == transpose_decrement:
            control_methods['transpose_decrement']()
            return
        # Pitch
        if event.type == pygame.JOYAXISMOTION and event.axis == pitch_bend_axis:
            value = -event.value
            if value > 1:
                value = -1  # Fix for corrupt values
            control_methods['pitch_bend'](value)
            return
    return input_event_processor

ps3_joy1 = _ps3_joy(0)
ps3_joy2 = _ps3_joy(1)


_key_lookup = {button: index for index, button in enumerate((
    pygame.K_q,
    pygame.K_w,
    pygame.K_e,
    pygame.K_r,
    pygame.K_t,
))}


def keyboard(event, control_methods):
    if event.type == pygame.KEYDOWN:
        if event.key in _key_lookup:
            control_methods['note_down'](_key_lookup[event.key])
            return
        if event.key == pygame.K_SPACE:
            control_methods['strum']()
            return
        if event.key == pygame.K_p:
            control_methods['transpose_increment']()
            return
        if event.key == pygame.K_o:
            control_methods['transpose_decrement']()
            return
    if event.type == pygame.KEYUP:
        if event.key in _key_lookup:
            control_methods['note_up'](_key_lookup[event.key])
            return


def _ps2_joy(joystick_number, axis_strum, button_notes, transpose_increment, transpose_decrement):
    button_lookup = {button: index for index, button in enumerate(button_notes)}

    def input_event_processor(event, control_methods):
        if getattr(event, 'joy', None) != joystick_number:
            return
        # Buttons
        if event.type == pygame.JOYBUTTONDOWN and event.button in button_lookup:
            control_methods['note_down'](button_lookup[event.button])
            return
        if event.type == pygame.JOYBUTTONUP and event.button in button_lookup:
            control_methods['note_up'](button_lookup[event.button])
            return
        # Strum
        if event.type == pygame.JOYAXISMOTION:
            if event.value > 0.1 or event.value < -0.1:
                control_methods['strum']()
                return
        # Transpose
        if event.type == pygame.JOYBUTTONDOWN and event.button == transpose_increment:
            control_methods['transpose_increment']()
            return
        if event.type == pygame.JOYBUTTONDOWN and event.button == transpose_decrement:
            control_methods['transpose_decrement']()
            return

    return input_event_processor

ps2_joy1 = _ps2_joy(
    joystick_number=0,
    axis_strum=3,
    button_notes=(5, 1, 0, 2, 3),
    transpose_increment=9,
    transpose_decrement=8,
)
ps2_joy2 = _ps2_joy(
    joystick_number=0,
    axis_strum=7,
    button_notes=(17, 13, 12, 14, 15),
    transpose_increment=21,
    transpose_decrement=20,
)
