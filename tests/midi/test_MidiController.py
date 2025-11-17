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

    # Methods expected by UiDispatcher in the real KeyBoard
    def set_key_state(self, name, state):
        key = self.find_key(name)
        if key == "":
            return
        key.config(state=state)

    def set_sustain(self, pressed):
        state = fake_tkinter.ACTIVE if pressed else fake_tkinter.NORMAL
        self.sustain.config(state=state)


# Simple Fake UiDispatcher for tests: register widgets and synchronously invoke posted methods
class FakeUiDispatcher:
    def __init__(self):
        self._registry = {}
        self.calls = []

    def register(self, name, widget):
        self._registry[name] = widget

    def unregister(self, name):
        self._registry.pop(name, None)

    def post_to(self, name, method_name, *args, **kwargs):
        # Record the call for assertions
        self.calls.append((name, method_name, args, kwargs))
        widget = self._registry.get(name)
        if widget is None:
            return
        func = getattr(widget, method_name, None)
        if func is None:
            return
        # Synchronously invoke to simulate immediate main-thread execution
        return func(*args, **kwargs)

class TestMidiController(unittest.TestCase):
    def setUp(self):
        # Ensure each test gets a fresh MidiController instance
        # Patch pygame.midi functions if needed
        self.fake_dispatcher = FakeUiDispatcher()
        self.controller = MidiController(dispatcher=self.fake_dispatcher)
    # --- get_key_name tests -------------------------------------------------
    def test_get_key_name_returns_first_note(self):
        # Arrange/Act
        result = self.controller.get_key_name(0)
        # Assert
        self.assertEqual(result, self.controller.NOTE_NAME[0])

    def test_get_key_name_returns_C4_for_index(self):
        # Arrange
        idx_c4 = self.controller.NOTE_NAME.index("C4")
        # Act
        result = self.controller.get_key_name(idx_c4)
        # Assert
        self.assertEqual(result, "C4")

    def test_get_key_name_returns_empty_for_invalid_indices(self):
        # Arrange/Act/Assert
        self.assertEqual(self.controller.get_key_name(-1), "")
        self.assertEqual(self.controller.get_key_name(128), "")

    # --- add_key_event tests ------------------------------------------------
    def test_add_key_event_enqueues_note_on(self):
        # Arrange
        note_name = "C4"
        note_num = self.controller.NOTE_NAME.index(note_name)
        # ensure queue empty first
        try:
            self.controller.event_queue.get_nowait()
            self.fail("Queue should be empty at test start")
        except Empty:
            pass
        # Act
        self.controller.add_key_event(note_name, True, 64)
        # Assert
        event = self.controller.event_queue.get(timeout=1.0)
        expected = ([0x90, note_num, 64, 0], 0)
        self.assertEqual(event, expected)

    def test_add_key_event_enqueues_note_off(self):
        # Arrange
        note_name = "C4"
        note_num = self.controller.NOTE_NAME.index(note_name)
        # Act
        self.controller.add_key_event(note_name, False, 0)
        # Assert
        event_off = self.controller.event_queue.get(timeout=1.0)
        expected_off = ([0x80, note_num, 0, 0], 0)
        self.assertEqual(event_off, expected_off)

    # --- handler note on/off tests -----------------------------------------
    def test_handler_note_on_updates_midiout_and_key_state(self):
        # Arrange
        kb = FakeKeyboard()
        self.controller.keyboard = kb
        self.fake_dispatcher.register('keyboard', kb)
        midiout = mock.Mock()
        self.controller.midiout = midiout
        note_name = "C4"
        note_num = self.controller.NOTE_NAME.index(note_name)
        velocity = 77
        on_event = ([0x90, note_num, velocity, 0], 0)
        # Act
        self.controller.handler(on_event)
        # Assert
        midiout.note_on.assert_called_with(note=note_num, velocity=velocity)
        self.assertEqual(kb._key.last_state, fake_tkinter.ACTIVE)

    def test_handler_note_off_updates_midiout_and_key_state(self):
        # Arrange
        kb = FakeKeyboard()
        self.controller.keyboard = kb
        self.fake_dispatcher.register('keyboard', kb)
        midiout = mock.Mock()
        self.controller.midiout = midiout
        note_name = "C4"
        note_num = self.controller.NOTE_NAME.index(note_name)
        off_event = ([0x80, note_num, 0, 0], 0)
        # Act
        self.controller.handler(off_event)
        # Assert
        midiout.note_off.assert_called_with(note=note_num)
        self.assertEqual(kb._key.last_state, fake_tkinter.NORMAL)

    # --- handler sustain tests --------------------------------------------
    def test_handler_sustain_on_writes_midiout_and_updates_sustain(self):
        # Arrange
        kb = FakeKeyboard()
        self.controller.keyboard = kb
        self.fake_dispatcher.register('keyboard', kb)
        midiout = mock.Mock()
        self.controller.midiout = midiout
        status = 0xB0
        cc_on_event = ([status, 0x40, 127, 0], 0)
        # Act
        self.controller.handler(cc_on_event)
        # Assert
        midiout.write_short.assert_called_with(status, 0x40, 127)
        self.assertEqual(kb.sustain.last_state, fake_tkinter.ACTIVE)

    def test_handler_sustain_off_writes_midiout_and_updates_sustain(self):
        # Arrange
        kb = FakeKeyboard()
        self.controller.keyboard = kb
        self.fake_dispatcher.register('keyboard', kb)
        midiout = mock.Mock()
        self.controller.midiout = midiout
        status = 0xB0
        cc_off_event = ([status, 0x40, 0, 0], 0)
        # Act
        self.controller.handler(cc_off_event)
        # Assert
        midiout.write_short.assert_called_with(status, 0x40, 0)
        self.assertEqual(kb.sustain.last_state, fake_tkinter.NORMAL)
