#!/usr/local/bin/python3
import pygame
import datetime

from operator import attrgetter

from music import note_to_text, parse_note, SCALES
from pygame_midi_wrapper import PygameMidiWrapper
import controls

import logging
log = logging.getLogger(__name__)

# Contants ---------------------------------------------------------------------

VERSION = '0.1'

TITLE = 'Pentatonic Hero'

DEFAULT_MIDI_PORT_NAME = 'PentatonicHero'
DEFAULT_HAMMER_DECAY = -0.1
DEFAULT_HAMMER_STRUM_BLOCK_DELAY = 100

now = lambda: datetime.datetime.now()

# Input Logic & State  ---------------------------------------------------------


class HeroInput(object):

    def __init__(self, input_event_identifyers, root_note, scale, midi_output, hammer_ons=True, hammer_decay=DEFAULT_HAMMER_DECAY, hammer_strum_block_delay=DEFAULT_HAMMER_STRUM_BLOCK_DELAY):
        self.input_event_identifyers = input_event_identifyers
        self.root_note = root_note
        self.scale = scale
        self.midi_output = midi_output

        self.hammer_decay = hammer_decay
        self.enable_hammer_ons_and_pulloffs = hammer_ons
        self.hammer_strum_block_delay = datetime.timedelta(microseconds=hammer_strum_block_delay * 1000)

        self.button_states = [False] * 5  # TODO: remove hard coded majic number for buttons
        self.scale_index_offset = 0
        self.playing_power = 0
        self.previous_note = 0
        self.previous_note_timestamp = now()
        self.pitch_bend = 0
        self.previous_pitch_bend = 0

    @property
    def button_greatest(self):
        return max([-1] + [index for index, state in enumerate(self.button_states) if state])

    @property
    def button_all(self):
        return not any([not b for b in self.button_states])

    def transpose_scale(self, offset):
        self.scale_index_offset += offset
        log.info('scale transpose: {0}'.format(offset))

    def transpose_root(self, offset):
        self.root_note += offset
        log.info('root note: {0}'.format(note_to_text(self.root_note)))

    # Input Logic ----------------------------

    def ctrl_transpose_increment(self):
        if self.button_all:
            self.transpose_root(1)
        else:
            self.transpose_scale(1)

    def ctrl_transpose_decrement(self):
        if self.button_all:
            self.transpose_root(-1)
        else:
            self.transpose_scale(-1)

    def ctrl_note_up(self, index):
        self.button_states[index] = False

    def ctrl_note_down(self, index):
        self.button_states[index] = True

    def ctrl_strum(self, value=None):
        """
        Some stum inputs are joystick axis's and will pass a value.
        0 is nutral, +1 down, -1 up
        However, the floating point 0 sometimes can be 0.03328745623847. we need a threshold
        """
        if value == None or value > 0.1 or value < -0.1:
            self.playing_power = 1

    def ctrl_pitch_bend(self, value):
        self.pitch_bend = value

    # Events -------------------------------------

    def update_state(self, event):
        """
        Update the object state based on input events
        and input_event_indentifyer config was passed on object __init__

        If the TANSPOSE buttons are pressed:
          the note buttons shift in the scale being used (by default the pentatonic)
        If all the note buttons are pressed and the TRANSPOSE buttons are used:
          the starting note (the music key) is changed
        """
        for input_event_identifyer in self.input_event_identifyers:
            if input_event_identifyer.type == event.type:
                if attrgetter(input_event_identifyer.attr)(event) == input_event_identifyer.value:
                    args = input_event_identifyer.event_func_args
                    # Hack - special case for axis
                    if input_event_identifyer.attr == 'axis':
                        args = (event.value,)
                    getattr(self, input_event_identifyer.event_func_name)(*args)

    def process_state(self):
        # Stop playing note if none pressed
        if self.button_greatest == -1:
            self.playing_power = 0
            self._send_note()
        if self.playing_power > 0:
            current_note = self.root_note + self.scale.scale_note(self.button_greatest + self.scale_index_offset)
            # Do not play a strum if the note has not chaged since a recent hammer on
            if \
                self.hammer_strum_block_delay and \
                self.playing_power >= 1 and \
                self.previous_note == current_note and \
                now() - self.previous_note_timestamp < self.hammer_strum_block_delay:
                    log.debug('hammer_strum_block_delay')
                    self.playing_power += self.hammer_decay
            # Play if note changed or strum
            elif current_note != self.previous_note or self.playing_power >= 1:
                self._send_note(current_note)
                self.playing_power += self.hammer_decay
        if self.pitch_bend != self.previous_pitch_bend:
            self.previous_pitch_bend = self.pitch_bend
            self._send_pitch_bend(self.pitch_bend)

    def _send_note(self, note=None):
        self.midi_output.note(self.previous_note, velocity=0)
        self.previous_note = note
        if note:
            if self.playing_power == 1 or \
               self.playing_power < 1 and self.enable_hammer_ons_and_pulloffs:
                self.midi_output.note(note, self.playing_power)
                self.previous_note_timestamp = now()

    def _send_pitch_bend(self, pitch):
        """
        """
        self.midi_output.pitch(pitch)


# Pygame -----------------------------------------------------------------------

class App:
    def __init__(self, options):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()

        # Init joysticks
        pygame.joystick.init()
        self.joysticks = {}
        for i in range(0, pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            self.joysticks[joystick.get_name()] = joystick
            joystick.init()

        # Init midi
        pygame.midi.init()
        self.midi_out = PygameMidiWrapper.open_device(options.midi_port_name)

        self.players = {
            'player1': HeroInput(
                options.input_profile,
                options.root_note,
                options.scale,
                PygameMidiWrapper(self.midi_out, channel=options.channel),
                options.hammer_ons,
                options.hammer_decay,
            ),
            'player2': HeroInput(
                options.input_profile2,
                options.root_note,
                options.scale,
                PygameMidiWrapper(self.midi_out, channel=options.channel+1),
                options.hammer_ons,
                options.hammer_decay,
            ),
        }

        self.running = True

    def _loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.quit()
            log.debug(event)
            for player in self.players.values():
                player.update_state(event)
        for player in self.players.values():
            player.process_state()

    def run(self):
        while self.running:
            self.clock.tick(100)
            self._loop()
        self.midi_out.close()
        pygame.midi.quit()
        pygame.quit()

    def quit(self):
        self.running = False


# Main -------------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""Pentetonic Hero -
        Connect your Guitar Hero controller to a Midi synth
        """,
        epilog=""""""
    )
    #parser.add_parser('input', nargs='*', help='Define a player input')   # first subgroup
    #parser_input = argparse.ArgumentParser(prog='input')
    parser_input = parser

    def select_input_profile(input_profile_name):
        try:
            return getattr(controls, input_profile_name)
        except AttributeError:
            log.warn('Unable to locate input_profile {0}.'.format(input_profile_name))
            return controls.null_input

    def select_scale(scale_string):
        return SCALES[scale_string]

    parser_input.add_argument('--input_profile', action='store', type=select_input_profile, help='input1 profile name (defined in controlers.py)', default='key_input')
    parser_input.add_argument('--input_profile2', action='store', type=select_input_profile, help='input2 profile name (defined in controlers.py)', default='null_input')
    parser_input.add_argument('--root_note', action='store', type=parse_note, help='root note (key)', default='C3')
    parser_input.add_argument('--scale', choices=SCALES.keys(), type=select_scale, help='scale to use (defined in music.py)', default='pentatonic_major')
    parser_input.add_argument('--channel', action='store', type=int, help='Midi channel to output too (player2 is automatically +1)', default=0)
    parser_input.add_argument('--hammer_ons', action='store', type=bool, help='Enable hammer-ons', default=True)
    parser_input.add_argument('--hammer_decay', action='store', type=float, help='Decay with each hammer on', default=-0.1)
    parser_input.add_argument('--hammer_strum_block_delay', action='store', type=int, help='After hammeron and strum of the same note, Drop the strum from duplicating the note.', default=DEFAULT_HAMMER_STRUM_BLOCK_DELAY)

    parser.add_argument('--midi_port_name', action='store', help='Output port name to attach too', default=DEFAULT_MIDI_PORT_NAME)

    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args.log_level)
    App(args).run()
