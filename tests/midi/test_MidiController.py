import sys
import types
import unittest
from unittest import mock
from queue import Empty

from src.midi.MidiController import MidiController

# Provide safe fake tkinter and pygame.midi before importing MidiController
fake_tkinter = types.SimpleNamespace(ACTIVE="active", NORMAL="normal")
sys.modules.setdefault("tkinter", fake_tkinter)

# Create a fake pygame.midi with minimal API used by MidiController
class FakeMidiModule:
    def __init__(self):
        self.inited = False

    def init(self):
        self.inited = True

    def quit(self):
        self.inited = False

    def get_default_input_id(self):
        return -1

    def get_default_output_id(self):
        return -1

    def get_count(self):
        return 0

    def get_device_info(self, i):
        return (b"Fake", b"Device", 0, 0, 0)

    class Input:
        def __init__(self, id):
            pass
        def poll(self):
            return False
        def read(self, n):
            return []
        def close(self):
            pass

    class Output:
        def __init__(self, id):
            pass
        def note_on(self, note, velocity):
            pass
        def note_off(self, note):
            pass
        def write_short(self, status, data1, data2):
            pass

fake_pygame = types.SimpleNamespace(midi=FakeMidiModule())
sys.modules.setdefault("pygame", types.SimpleNamespace(midi=fake_pygame.midi))
sys.modules.setdefault("pygame.midi", fake_pygame.midi)


# Helper fake key and keyboard classes
class FakeKey:
    def __init__(self):
        self.last_state = None
    def config(self, state=None):
        self.last_state = state

class FakeSustain:
    def __init__(self):
        self.last_state = None
    def config(self, state=None):
        self.last_state = state

class FakeKeyboard:
    def __init__(self):
        self._key = FakeKey()
        self.sustain = FakeSustain()
        self.last_find = None
    def find_key(self, name):
        self.last_find = name
        if name == "":
            return ""
        return self._key

class TestMidiController(unittest.TestCase):
    def setUp(self):
        # Ensure each test gets a fresh MidiController instance
        # Patch pygame.midi functions if needed
        self.controller = MidiController()

    def test_get_key_name_valid_and_invalid(self):
        # valid index
        self.assertEqual(self.controller.get_key_name(0), self.controller.NOTE_NAME[0])
        # another valid: find "C4"
        idx_c4 = self.controller.NOTE_NAME.index("C4")
        self.assertEqual(self.controller.get_key_name(idx_c4), "C4")
        # invalid low
        self.assertEqual(self.controller.get_key_name(-1), "")
        # invalid high
        self.assertEqual(self.controller.get_key_name(128), "")

    def test_add_key_event_enqueues_correct_event(self):
        note_name = "C4"
        note_num = self.controller.NOTE_NAME.index(note_name)
        # ensure queue empty first
        try:
            self.controller.event_queue.get_nowait()
            self.fail("Queue should be empty at test start")
        except Empty:
            pass

        self.controller.add_key_event(note_name, True, 64)
        event = self.controller.event_queue.get(timeout=1.0)
        expected = ([0x90, note_num, 64, 0], 0)
        self.assertEqual(event, expected)

        # Test note off
        self.controller.add_key_event(note_name, False, 0)
        event_off = self.controller.event_queue.get(timeout=1.0)
        expected_off = ([0x80, note_num, 0, 0], 0)
        self.assertEqual(event_off, expected_off)

    def test_handler_note_on_and_note_off(self):
        kb = FakeKeyboard()
        self.controller.keyboard = kb

        # provide a mock midiout to capture calls
        midiout = mock.Mock()
        self.controller.midiout = midiout

        note_name = "C4"
        note_num = self.controller.NOTE_NAME.index(note_name)
        velocity = 77

        # Note On event
        on_event = ([0x90, note_num, velocity, 0], 0)
        self.controller.handler(on_event)

        midiout.note_on.assert_called_with(note=note_num, velocity=velocity)
        self.assertEqual(kb._key.last_state, fake_tkinter.ACTIVE)

        # Note Off event
        off_event = ([0x80, note_num, 0, 0], 0)
        self.controller.handler(off_event)

        midiout.note_off.assert_called_with(note=note_num)
        self.assertEqual(kb._key.last_state, fake_tkinter.NORMAL)

    def test_sustain_change(self):
        kb = FakeKeyboard()
        self.controller.keyboard = kb

        midiout = mock.Mock()
        self.controller.midiout = midiout

        status = 0xB0
        # Sustain ON (value > 0)
        cc_on_event = ([status, 0x40, 127, 0], 0)
        self.controller.handler(cc_on_event)

        midiout.write_short.assert_called_with(status, 0x40, 127)
        self.assertEqual(kb.sustain.last_state, fake_tkinter.ACTIVE)

        midiout.reset_mock()
        # Sustain OFF (value == 0)
        cc_off_event = ([status, 0x40, 0, 0], 0)
        self.controller.handler(cc_off_event)

        midiout.write_short.assert_called_with(status, 0x40, 0)
        self.assertEqual(kb.sustain.last_state, fake_tkinter.NORMAL)

if __name__ == "__main__":
    unittest.main()