#!/usr/local/bin/python3
import pygame
import pygame.midi
from pygame.locals import *

import re

from collections import namedtuple
from operator import attrgetter
from itertools import chain

TITLE = 'Pentatonic Hero'


# Music Note Utils -------------------------------------------------------------

LOOKUP_NOTE_STR = {
    0: 'C',
    1: 'C#',
    2: 'D',
    3: 'D#',
    4: 'E',
    5: 'F',
    6: 'F#',
    7: 'G',
    8: 'G#',
    9: 'A',
    10: 'A#',
    11: 'B',
}
LOOKUP_STR_NOTE = {text: note for note, text in LOOKUP_NOTE_STR.items()}
NUM_NOTES_IN_OCTAVE = len(LOOKUP_NOTE_STR)


def note_to_text(note):
    """
    >>> note_to_text(0)
    'C0'
    >>> note_to_text(1)
    'C#0'
    >>> note_to_text(12)
    'C1'
    >>> note_to_text(13)
    'C#1'
    """
    return '{0}{1}'.format(
        LOOKUP_NOTE_STR[note % NUM_NOTES_IN_OCTAVE],
        int(note/NUM_NOTES_IN_OCTAVE)
    )  # INTEGER DEVISION REQUIRED!!!


def parse_note(item):
    """
    >>> parse_note('C0')
    0
    >>> parse_note('C1')
    12
    >>> parse_note('C#0')
    1
    >>> parse_note('C#1')
    13
    """
    try:
        note_str, octave = re.match(r'([ABCDEFG]#?)(\d)', item.upper()).groups()
        return LOOKUP_STR_NOTE[note_str] + (int(octave) * NUM_NOTES_IN_OCTAVE)
    except Exception:
        raise Exception('Unable to parse note {0}'.format(item))


def note_to_stdout(note, velocity=None):
    if note:
        print('{0} - {1}'.format(note_to_text(note), velocity))


class Scale(object):
    def __init__(self, scale):
        self.scale = scale

    @property
    def len(self):
        return len(self.scale)

    def scale_note(self, scale_index):
        """
        Calculate the distance in semitones from the scale's root
        """
        index = scale_index % self.len
        octave = int(scale_index / self.len)  # INTEGER DEVISION NEEDED!!!
        return self.scale[index] + (octave * NUM_NOTES_IN_OCTAVE)


scales = {
    'pentatonic': Scale([0, 3, 5, 7, 10]),
}


# Controls ---------------------------------------------------------------------

InputEvent = namedtuple('InputEvent', ['type', 'attr', 'value', 'event_func_name', 'event_func_args'])


def hero_control_factory(
        event_type,
        event_down,
        event_up,
        button_strum,
        button_transpose_increment,
        button_transpose_decrement,
        button_notes,
        pitch_bend_axis = None,
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
        control_config += (InputEvent(JOYAXISMOTION, 'axis', pitch_bend_axis, 'ctrl_pitch_bend', ()),)
    return control_config

key_input = hero_control_factory(
    event_type='key',
    event_down=KEYDOWN,
    event_up=KEYUP,
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

joy_input = hero_control_factory(
    event_type='button',
    event_down=JOYBUTTONDOWN,
    event_up=JOYBUTTONUP,
    button_strum=6,
    button_transpose_increment=7,
    button_transpose_decrement=8,
    button_notes=(1, 2, 3, 4, 5),
    pitch_bend_axis=1,
)


# Input Logic & State  ---------------------------------------------------------

class HeroInput(object):

    PLAYING_DECAY = -0.1

    def __init__(self, input_event_identifyers, starting_note, scale, output):
        self.input_event_identifyers = input_event_identifyers
        self._starting_note = starting_note
        self.scale = scale
        self.output = output

        self.enable_hammer_ons_and_pulloffs = True

        self.button_states = [False for i in range(5)]  # TODO: remove hard coded majic number for buttons
        self.scale_index_offset = 0
        self.playing_power = 0
        self.previous_note = 0
        self.pitch_bend = 0
        self.previous_pitch_bend = 0

    @property
    def starting_note(self):
        return self._starting_note
    @starting_note.setter
    def starting_note(self, starting_note):
        self._starting_note = starting_note
        note_to_stdout(self._starting_note)

    @property
    def button_greatest(self):
        return max([-1] + [index for index, state in enumerate(self.button_states) if state])

    @property
    def button_all(self):
        return not any([not b for b in self.button_states])

    # Input Logic ----------------------------

    def ctrl_transpose_increment(self):
        if self.button_all:
            self.starting_note += 1
        else:
            self.scale_index_offset += 1

    def ctrl_transpose_decrement(self):
        if self.button_all:
            self.starting_note += -1
        else:
            self.scale_index_offset += -1

    def ctrl_note_up(self, index):
        self.button_states[index] = False

    def ctrl_note_down(self, index):
        self.button_states[index] = True

    def ctrl_strum(self):
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
            self.send_note()
        if self.playing_power > 0:
            current_note = self.starting_note + self.scale.scale_note(self.button_greatest + self.scale_index_offset)
            # Play if note changed or strum
            if current_note != self.previous_note or self.playing_power >= 1:
                self.send_note(current_note)
                self.playing_power += self.PLAYING_DECAY
        if self.pitch_bend != self.previous_pitch_bend:
            self.previous_pitch_bend = self.pitch_bend
            self.send_pitch_bend(self.pitch_bend)

    def send_note(self, note=None):
        self.output(self.previous_note, None)
        self.previous_note = note
        if note:
            if self.playing_power == 1 or \
               self.playing_power < 1 and self.enable_hammer_ons_and_pulloffs:
                self.output(note, self.playing_power)

    def send_pitch_bend(self, pitch_bend):
        # TODO - cant use .output because we want to send control signals not notes
        #self.output()
        print('pitch bend: {0}'.format(pitch_bend))

# Pygame -----------------------------------------------------------------------

class App:
    def __init__(self):
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
        MidiDevice = namedtuple('MidiDevice', ('id', 'interf', 'name', 'input', 'output', 'opened'))
        def get_midi_device(id):
            return MidiDevice(*((id,)+pygame.midi.get_device_info(id)))
        midi_output_device_id = pygame.midi.get_default_output_id()
        for midi_device in (get_midi_device(id) for id in range(pygame.midi.get_count())):
            if 'PentatonicHero'.lower() in midi_device.name.decode('utf-8').lower() and bool(midi_device.output):
                midi_output_device_id = midi_device.id
        print ("using midi output - {0}".format(get_midi_device(midi_output_device_id)))
        self.midi_out = pygame.midi.Output(midi_output_device_id)
        self.midi_out.set_instrument(0)

        def note_to_midi(note, velocity=None):
            if not note:
                return
            if velocity:
                self.midi_out.note_on(note, int(velocity * 127))
            else:
                self.midi_out.note_off(note)
            note_to_stdout(note, velocity)

        self.players = {
            'player1': HeroInput(joy_input, parse_note('C#3'), scales['pentatonic'], note_to_midi),  # note_to_stdout
        }

        self.running = True

    def _loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.quit()
            #print(event)
            for player in self.players.values():
                player.update_state(event)
        for player in self.players.values():
            player.process_state()

    def run(self):
        while self.running:
            self.clock.tick(100)
            self._loop()
        del self.midi_out
        pygame.midi.quit()
        pygame.quit()

    def quit(self):
        self.running = False


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    App().run()
