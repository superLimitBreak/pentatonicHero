import pygame.midi

from collections import namedtuple

from music import note_to_text, midi_pitch

import logging
log = logging.getLogger(__name__)

pygame.midi.init()

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

