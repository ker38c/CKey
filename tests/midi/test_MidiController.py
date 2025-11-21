import sys
import types
import pytest
from unittest import mock
from queue import Empty, Queue
import threading

from src.midi.MidiController import MidiController
from src.midi.MidiHandler import MidiHandler

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


@pytest.fixture
def fake_dispatcher():
    return FakeUiDispatcher()


# MidiHandler tests have been moved to tests/midi/test_MidiHandler.py
@pytest.fixture
def controller(fake_dispatcher):
    return MidiController(dispatcher=fake_dispatcher)


def test_add_key_event_enqueues_note_on(controller):
    # Arrange
    note_name = "C4"
    note_num = controller.handler.NOTE_NAME.index(note_name)
    # ensure queue empty first
    try:
        controller.event_queue.get_nowait()
        pytest.fail("Queue should be empty at test start")
    except Empty:
        pass
    # Act
    controller.add_key_event(note_name, True, 64)
    # Assert
    event = controller.event_queue.get(timeout=1.0)
    expected = ([0x90, note_num, 64, 0], 0)
    assert event == expected


def test_add_key_event_enqueues_note_off(controller):
    # Arrange
    note_name = "C4"
    note_num = controller.handler.NOTE_NAME.index(note_name)
    # Act
    controller.add_key_event(note_name, False, 0)
    # Assert
    event_off = controller.event_queue.get(timeout=1.0)
    expected_off = ([0x80, note_num, 0, 0], 0)
    assert event_off == expected_off
