import pygame.midi

from collections import namedtuple

from music import note_to_text, midi_pitch

import logging
log = logging.getLogger(__name__)


class PygameMidiWrapperNull(object):
    def note(self, *args, **kwargs):
        pass

    def pitch(self, *args, **kwargs):
        pass


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
        midi_device_id = pygame.midi.get_default_output_id()
        if name:
            for midi_device in PygameMidiWrapper.get_devices():
                if name.lower() in midi_device.name.decode('utf-8').lower() and bool(getattr(midi_device, io)):
                    midi_device_id = midi_device.id
        if midi_device_id == -1:
            log.warn("unable to identify a midi device with name '{0}'".format(name))
            return
        log.info("using midi {0} - {1}".format(io, PygameMidiWrapper.get_device(midi_device_id)))
        if io == 'output':
            return pygame.midi.Output(midi_device_id)
        if io == 'input':
            return pygame.midi.Input(midi_device_id)

    @staticmethod
    def factory(pygame_midi_output, channel=0):
        if pygame_midi_output:
            return PygameMidiWrapper(pygame_midi_output, channel)
        return PygameMidiWrapperNull()

    def __init__(self, pygame_midi_output, channel=0):
        assert pygame_midi_output, 'pygame_midi_output required'
        self.midi = pygame_midi_output
        self.channel = channel

    def note(self, note, velocity=0):
        """
        note int, velocity float 0->1
        """
        if not note:
            return
        velocity = int(velocity * 127)
        log.info('note: ch{0} - {1} {2} - {3}'.format(self.channel, note, note_to_text(note), velocity))
        self.midi.write_short(0x90 + self.channel, note, velocity)
        #if velocity:
        #    self.midi.note_on(note, velocity)
        #else:
        #    self.midi.note_off(note)
        #self.midi.write_short(0x90 + self.channel, note, 127)

    def pitch(self, pitch=0):
        """
        pitch float -1 to 1
        """
        log.info('pitch: ch{0} - {1}'.format(self.channel, pitch))
        self.midi.write_short(*midi_pitch(pitch, channel=self.channel))
