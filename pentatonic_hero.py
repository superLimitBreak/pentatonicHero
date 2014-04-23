#!/usr/local/bin/python3
import pygame
import pygame.midi
from pygame.locals import *

from collections import namedtuple
from operator import attrgetter

from music import note_to_text, parse_note, midi_pitch, SCALES
from controls import key_input, joy1_input

import logging
log = logging.getLogger(__name__)

# Contants ---------------------------------------------------------------------

TITLE = 'Pentatonic Hero'


# Midi Wrapper -----------------------------------------------------------------

class PygameMidiWrapper(object):
    MidiDevice = namedtuple('MidiDevice', ('id', 'interf', 'name', 'input', 'output', 'opened'))

    @staticmethod
    def get_device(id):
        return PygameMidiWrapper.MidiDevice(*((id,)+pygame.midi.get_device_info(id)))

    @staticmethod
    def get_devices():
        return (PygameMidiWrapper.get_device(id) for id in range(pygame.midi.get_count()))

    @staticmethod
    def open_device(name=None, io='output'):
        midi_output_device_id = pygame.midi.get_default_output_id()
        if name:
            for midi_device in PygameMidiWrapper.get_devices():
                if name.lower() in midi_device.name.decode('utf-8').lower() and bool(midi_device.output):
                    midi_output_device_id = midi_device.id
        log.info("using midi output - {0}".format(PygameMidiWrapper.get_device(midi_output_device_id)))
        return pygame.midi.Output(midi_output_device_id)

    def __init__(self, pygame_midi_output, channel=0):
        self.midi = pygame_midi_output
        self.channel = channel

    def note(self, note, velocity=0):
        """
        note int, velocity float 0->1
        """
        if not note:
            return
        log.debug('note: {0} - {1}'.format(note_to_text(note), velocity))
        self.midi.write_short(0x90 + self.channel, note, int(velocity * 127))

    def pitch(self, pitch=0):
        log.debug('pitch: {1}'.format(pitch))
        self.midi.write_short(*midi_pitch(pitch, channel=self.channel))


# Input Logic & State  ---------------------------------------------------------

class HeroInput(object):

    PLAYING_DECAY = -0.1

    def __init__(self, input_event_identifyers, root_note, scale, midi_output):
        self.input_event_identifyers = input_event_identifyers
        self.root_note = root_note
        self.scale = scale
        self.midi_output = midi_output

        self.enable_hammer_ons_and_pulloffs = True

        self.button_states = [False for i in range(5)]  # TODO: remove hard coded majic number for buttons
        self.scale_index_offset = 0
        self.playing_power = 0
        self.previous_note = 0
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
            self._send_note()
        if self.playing_power > 0:
            current_note = self.root_note + self.scale.scale_note(self.button_greatest + self.scale_index_offset)
            # Play if note changed or strum
            if current_note != self.previous_note or self.playing_power >= 1:
                self._send_note(current_note)
                self.playing_power += self.PLAYING_DECAY
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

    def _send_pitch_bend(self, pitch):
        """
        """
        self.midi_output.pitch(pitch)


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
        self.midi_out = PygameMidiWrapper.open_device('PentatonicHero')

        self.players = {
            'player1': HeroInput(key_input, parse_note('C#3'), SCALES['pentatonic'], PygameMidiWrapper(self.midi_out, channel=0)),
            #'player2': HeroInput(key_input, parse_note('C#3'), scales['pentatonic'], PygameMidiWrapper(self.midi_out, channel=1)),
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
        self.midi_out.close()
        pygame.midi.quit()
        pygame.quit()

    def quit(self):
        self.running = False


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    App().run()
