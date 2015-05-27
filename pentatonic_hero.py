#!/usr/local/bin/python3
import pygame
import datetime
import operator
from collections import namedtuple
from functools import partial

from libs.music import note_to_text, parse_note, SCALES
from libs.pygame_midi_wrapper import PygameMidiDeviceHelper
from libs.pygame_midi_output import PygameMidiOutputWrapper
from libs.network_display_event import DisplayEventHandler, DisplayEventHandlerNull
import controls

import logging
log = logging.getLogger(__name__)

# Contants ---------------------------------------------------------------------

VERSION = '0.3'

TITLE = 'Pentatonic Hero'

DEFAULT_DISPLAY_HOST = 'localhost:9872'

DEFAULT_MIDI_PORT_NAME = 'PentatonicHero'
DEFAULT_ROOT_NOTE = 'A3'
DEFAULT_SCALE = 'pentatonic_minor'
DEFAULT_HAMMER_DECAY = -0.01
DEFAULT_HAMMER_STRUM_BLOCK_DELAY = 50
DEFAULT_NOTE_LIMIT = (parse_note('C1'), parse_note('C#5'))
DEFAULT_DISPLAY_EVENT_FUNCTION_NAME = 'penatonic_hero.event'

now = lambda: datetime.datetime.now()

NoteLimit = namedtuple('NoteLimit', ['lower', 'upper'])

# Input Logic & State  ---------------------------------------------------------


class HeroInput(object):

    input_identifyer = 0

    def __init__(self, input_event_processor, midi_output,
        display=DisplayEventHandlerNull(),
        root_note=parse_note(DEFAULT_ROOT_NOTE),
        scale=SCALES[DEFAULT_SCALE],
        hammer_ons=True,
        hammer_decay=DEFAULT_HAMMER_DECAY,
        hammer_strum_block_delay=DEFAULT_HAMMER_STRUM_BLOCK_DELAY,
        note_limit=NoteLimit(*DEFAULT_NOTE_LIMIT),
        **kwargs
    ):
        HeroInput.input_identifyer += 1

        self.input_event_processor = input_event_processor

        self.root_note = root_note
        assert root_note >= note_limit.lower and root_note <= note_limit.upper, 'root_note is not within note range limit'

        self.scale = scale
        self.midi_output = midi_output

        def display_event(event, **kwargs):
            kwargs['event'] = event
            kwargs['input'] = HeroInput.input_identifyer
            display.event(DEFAULT_DISPLAY_EVENT_FUNCTION_NAME, **kwargs)
        self.display_event = display_event

        self.hammer_decay = hammer_decay
        self.enable_hammer_ons_and_pulloffs = hammer_ons
        self.hammer_strum_block_delay = datetime.timedelta(microseconds=hammer_strum_block_delay * 1000)
        self.note_limit = note_limit

        self.button_states = [False] * 5  # TODO: remove hard coded magic number for buttons
        self.playing_power = 0
        self.previous_note = 0
        self.previous_note_timestamp = now()
        self.pitch_bend = 0
        self.previous_pitch_bend = 0

        self.mute = False

        self.scale_index_offset = 0
        self._calculate_scale_limit()

        # A dictionary of bound methods to manipulate this HeroInput
        # The controler code can call these to update to the state
        self.control_methods = {
            method_name: getattr(self, 'ctrl_{0}'.format(method_name))
            for method_name in (
                'transpose_increment',
                'transpose_decrement',
                'note_up',
                'note_down',
                'strum',
                'pitch_bend',
            )
        }

    def _calculate_scale_limit(self):
        def _nearest_scale_index_offset(target_midi_note, index_offset, seek_direction):
            """
            seek_direction -1 or +1
            """
            if seek_direction != 1 and seek_direction != -1:
                raise AttributeError('seek_drieciton muse be 1 or -1')
            scale_index_offset = 0
            compare = operator.ge if seek_direction == 1 else operator.le
            while compare(target_midi_note, self.get_midi_note(scale_index_offset + index_offset)):
                scale_index_offset += seek_direction
            # When we pop out of the desitred range, revert the last seek_direction
            # to ensure last note (scale_index) is definantly within out range
            return scale_index_offset - seek_direction
        self.scale_index_offset_limit = NoteLimit(
            lower=_nearest_scale_index_offset(self.note_limit.lower, 0                        , -1),
            upper=_nearest_scale_index_offset(self.note_limit.upper, len(self.button_states)-1,  1),
        )

    @property
    def button_greatest(self):
        return max([-1] + [index for index, state in enumerate(self.button_states) if state])

    @property
    def button_all(self):
        return not any([not b for b in self.button_states])

    @property
    def current_midi_note(self):
        return self.get_midi_note(self.button_greatest)

    def get_midi_note(self, scale_index):
        return self.root_note + self.scale.scale_note(scale_index + self.scale_index_offset)

    def transpose_scale(self, offset):
        proposed_scale_index_offset = self.scale_index_offset + offset
        if (proposed_scale_index_offset >= self.scale_index_offset_limit.lower) and \
           (proposed_scale_index_offset <= self.scale_index_offset_limit.upper):
            self.scale_index_offset = proposed_scale_index_offset
            log.info('scale transpose: {0}'.format(offset))
            self.display_event('transpose', notes=[note_to_text(self.get_midi_note(i)) for i, v in enumerate(self.button_states)])
        else:
            log.info('scale transpose: restricted with limit')

    def transpose_root(self, offset):
        self.root_note += offset
        log.info('root note: {0}'.format(note_to_text(self.root_note)))
        self._calculate_scale_limit()

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
        self.display_event('button_up', button=index)

    def ctrl_note_down(self, index):
        self.button_states[index] = True
        self.display_event('button_down', button=index)

    def ctrl_strum(self, value=None):
        """
        Some stum inputs are joystick axis's and will pass a value.
        0 is nutral, +1 down, -1 up
        However, the floating point 0 sometimes can be 0.03328745623847. we need a threshold
        """
        if value is None or value > 0.1 or value < -0.1:
            value = value or 0
            self.playing_power = 1
            self.display_event('strum', value=1 if value >= 0 else -1)

    def ctrl_pitch_bend(self, value):
        self.pitch_bend = -value

    # Events -------------------------------------

    def toggle_mute(self):
        self.mute = not self.mute
        log.info('mute: {0}'.format(self.mute))
        if self.mute:
            self._send_note_off()

    def update_state(self, event):
        """
        Update the object state based on input events
        and input_event_indentifyer config was passed on object __init__

        If the TANSPOSE buttons are pressed:
          the note buttons shift in the scale being used (by default the pentatonic)
        If all the note buttons are pressed and the TRANSPOSE buttons are used:
          the starting note (the music key) is changed
        """
        self.input_event_processor(event, self.control_methods)

    def process_state(self):
        # Stop playing note if none pressed
        if self.button_greatest == -1:
            self.playing_power = 0
            self._send_note_off()
        if self.playing_power > 0:
            current_note = self.current_midi_note
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
            self.display_event('pitch', pitch=self.pitch_bend)

    def _send_note(self, note):
        if not note:
            return
        self._send_note_off()
        self.previous_note = note
        if note and not self.mute:
            if self.playing_power == 1 or \
               self.playing_power < 1 and self.enable_hammer_ons_and_pulloffs:
                self.midi_output.note(note, self.playing_power)
                self.display_event('note_on', value=note, button=self.button_greatest)
                self.previous_note_timestamp = now()

    def _send_note_off(self):
        if self.previous_note:
            self.midi_output.note(self.previous_note, velocity=0)
            self.display_event('note_off', value=self.previous_note)
            self.previous_note = None

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
        self.midi_out = PygameMidiDeviceHelper.open_device(options.midi_port_name)

        # Network display reporting
        self.display = DisplayEventHandler.factory(*options.display_host.split(':'))

        self.players = {
            'player1': HeroInput(
                options.input_profile,
                PygameMidiOutputWrapper.factory(self.midi_out, channel=options.channel),
                display=self.display,
                **vars(options)
            ),
            'player2': HeroInput(
                options.input_profile2,
                PygameMidiOutputWrapper.factory(self.midi_out, channel=options.channel+1),
                display=self.display,
                **vars(options)
            ),
        }

        self.running = True

    def _loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.players['player1'].toggle_mute()
                if event.key == pygame.K_F2:
                    self.players['player2'].toggle_mute()
            try:
                if event.axis != 3:  # The PS3 controler has a touch sensetive pad that constantly spams the logs with axis results
                    log.debug(event)
            except:
                log.debug(event)
            for player in self.players.values():
                player.update_state(event)
        for player in self.players.values():
            player.process_state()

    def run(self):
        while self.running:
            self.clock.tick(100)
            self._loop()
        if self.midi_out:
            self.midi_out.close()
        if self.display:
            self.display.close()
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

    parser_input.add_argument('--input_profile', choices=controls.__all__, help='input1 profile name (defined in controlers.py)', default='keyboard')
    parser_input.add_argument('--input_profile2', choices=controls.__all__, help='input2 profile name (defined in controlers.py)', default='null_input')
    parser_input.add_argument('--root_note', action='store', type=parse_note, help='root note (key)', default=DEFAULT_ROOT_NOTE)
    parser_input.add_argument('--scale', choices=SCALES.keys(), help='scale to use (defined in music.py)', default=DEFAULT_SCALE)
    parser_input.add_argument('--channel', action='store', type=int, help='Midi channel to output too (player2 is automatically +1)', default=0)
    parser_input.add_argument('--hammer_ons', action='store', type=bool, help='Enable hammer-ons', default=True)
    parser_input.add_argument('--hammer_decay', action='store', type=float, help='Decay with each hammer on', default=DEFAULT_HAMMER_DECAY)
    parser_input.add_argument('--hammer_strum_block_delay', action='store', type=int, help='After hammeron and strum of the same note, Drop the strum from duplicating the note.', default=DEFAULT_HAMMER_STRUM_BLOCK_DELAY)
    parser_input.add_argument('--note_limit', action='store', type=parse_note, nargs=2, help='Set an upper and lower limit e.g "C2 A6"', default=DEFAULT_NOTE_LIMIT)
    parser_input.add_argument('--display_host', action='store', help='ip adress and port for remote TCP display events', default=DEFAULT_DISPLAY_HOST)

    parser.add_argument('--midi_port_name', action='store', help='Output port name to attach too', default=DEFAULT_MIDI_PORT_NAME)

    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = parser.parse_args()

    args.input_profile = select_input_profile(args.input_profile)
    args.input_profile2 = select_input_profile(args.input_profile2)
    args.scale = select_scale(args.scale)
    args.note_limit = NoteLimit(*args.note_limit)

    return args


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args.log_level)
    App(args).run()
