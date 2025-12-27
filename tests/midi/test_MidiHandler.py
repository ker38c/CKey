import sys
import types
import pytest
from unittest import mock

# Provide safe fake tkinter and pygame.midi before importing MidiHandler
fake_tkinter = types.SimpleNamespace(ACTIVE="active", NORMAL="normal")
sys.modules.setdefault("tkinter", fake_tkinter)

# Minimal fake pygame.midi to avoid importing the real library in tests
class FakeMidiModule:
    def init(self):
        pass
    def quit(self):
        pass
    def get_default_input_id(self):
        return -1
    def get_default_output_id(self):
        return -1
    def get_count(self):
        return 0
    def get_device_info(self, i):
        return (b"Fake", b"Device", 0, 0, 0)

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

from src.midi.MidiHandler import MidiHandler


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
    def _find_key(self, name):
        self.last_find = name
        if name == "":
            return ""
        return self._key

    def set_key_state(self, name, state):
        key = self._find_key(name)
        if key == "":
            return
        key.config(state=state)

    def set_sustain(self, pressed):
        state = fake_tkinter.ACTIVE if pressed else fake_tkinter.NORMAL
        self.sustain.config(state=state)


class FakeUiDispatcher:
    def __init__(self):
        self._registry = {}
        self.calls = []
    def register(self, name, widget):
        self._registry[name] = widget
    def unregister(self, name):
        self._registry.pop(name, None)
    def post_to(self, name, method_name, *args, **kwargs):
        self.calls.append((name, method_name, args, kwargs))
        widget = self._registry.get(name)
        if widget is None:
            return
        func = getattr(widget, method_name, None)
        if func is None:
            return
        return func(*args, **kwargs)


@pytest.fixture
def fake_dispatcher():
    return FakeUiDispatcher()


@pytest.fixture
def handler(fake_dispatcher):
    return MidiHandler(
        event_queue=None,
        lock=None,
        end_flag_getter=lambda: False,
        dispatcher=fake_dispatcher
    )


def test__get_key_name_returns_first_note(handler):
    # Arrange / Act
    result = handler._get_key_name(0)
    # Assert
    assert result == handler.NOTE_NAME[0]


def test__get_key_name_returns_C4_for_index(handler):
    # Arrange
    idx_c4 = handler.NOTE_NAME.index("C4")
    # Act
    result = handler._get_key_name(idx_c4)
    # Assert
    assert result == "C4"


def test__get_key_name_returns_empty_for_invalid_indices(handler):
    # Arrange / Act / Assert
    assert handler._get_key_name(-1) == ""
    assert handler._get_key_name(128) == ""


def test_handler_note_on_updates_midiout_and_key_state(handler, fake_dispatcher):
    # Arrange
    kb = FakeKeyboard()
    handler.set_keyboard(kb)
    fake_dispatcher.register('keyboard', kb)
    midiout = mock.Mock()
    handler.set_output_device(midiout)
    note_name = "C4"
    note_num = handler.NOTE_NAME.index(note_name)
    velocity = 77
    on_event = ([0x90, note_num, velocity, 0], 0)
    # Act
    handler._handler(on_event)
    # Assert
    midiout.note_on.assert_called_with(note=note_num, velocity=velocity)
    assert kb._key.last_state == fake_tkinter.ACTIVE


def test_handler_note_off_updates_midiout_and_key_state(handler, fake_dispatcher):
    # Arrange
    kb = FakeKeyboard()
    handler.set_keyboard(kb)
    fake_dispatcher.register('keyboard', kb)
    midiout = mock.Mock()
    handler.set_output_device(midiout)
    note_name = "C4"
    note_num = handler.NOTE_NAME.index(note_name)
    off_event = ([0x80, note_num, 0, 0], 0)
    # Act
    handler._handler(off_event)
    # Assert
    midiout.note_off.assert_called_with(note=note_num)
    assert kb._key.last_state == fake_tkinter.NORMAL


def test_handler_sustain_on_writes_midiout_and_updates_sustain(handler, fake_dispatcher):
    # Arrange
    kb = FakeKeyboard()
    handler.set_keyboard(kb)
    fake_dispatcher.register('keyboard', kb)
    midiout = mock.Mock()
    handler.set_output_device(midiout)
    status = 0xB0
    cc_on_event = ([status, 0x40, 127, 0], 0)
    # Act
    handler._handler(cc_on_event)
    # Assert
    midiout.write_short.assert_called_with(status, 0x40, 127)
    assert kb.sustain.last_state == fake_tkinter.ACTIVE


def test_handler_sustain_off_writes_midiout_and_updates_sustain(handler, fake_dispatcher):
    # Arrange
    kb = FakeKeyboard()
    handler.set_keyboard(kb)
    fake_dispatcher.register('keyboard', kb)
    midiout = mock.Mock()
    handler.set_output_device(midiout)
    status = 0xB0
    cc_off_event = ([status, 0x40, 0, 0], 0)
    # Act
    handler._handler(cc_off_event)
    # Assert
    midiout.write_short.assert_called_with(status, 0x40, 0)
    assert kb.sustain.last_state == fake_tkinter.NORMAL
