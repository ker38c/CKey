"""
Shared fixtures and test doubles for MIDI tests.
"""
import sys
import os
import types
import pytest

from src.midi.MidiBackend import MidiBackend

# Add src to path for gui module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Provide comprehensive fake tkinter before importing any modules that depend on it
class FakeTkButton:
    def __init__(self, master=None, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def bind(self, *args, **kwargs):
        pass
    def place(self, **kwargs):
        pass

class FakeTkFrame:
    def __init__(self, master=None, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def pack(self, **kwargs):
        pass

class FakeTkCanvas:
    def __init__(self, master=None, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def bind(self, *args, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def delete(self, *args):
        pass
    def create_oval(self, *args, **kwargs):
        pass
    def winfo_width(self):
        return 100
    def winfo_height(self):
        return 100

fake_tkinter = types.SimpleNamespace(
    ACTIVE="active",
    NORMAL="normal",
    BOTH="both",
    Button=FakeTkButton,
    Frame=FakeTkFrame,
    Canvas=FakeTkCanvas,
)
sys.modules["tkinter"] = fake_tkinter

# Minimal pygame.midi stub (required for PygameMidiBackend import)
_fake_pygame_midi = types.SimpleNamespace(
    init=lambda: None,
    quit=lambda: None,
    get_count=lambda: 0,
    get_default_input_id=lambda: -1,
    get_default_output_id=lambda: -1,
    get_device_info=lambda i: (b"Fake", b"Device", 0, 0, 0),
    Input=type("Input", (), {"__init__": lambda s, i: None}),
    Output=type("Output", (), {"__init__": lambda s, i: None}),
)
sys.modules.setdefault("pygame", types.SimpleNamespace(midi=_fake_pygame_midi))
sys.modules.setdefault("pygame.midi", _fake_pygame_midi)


# Test Doubles

class FakeMidiInput:
    """Fake MIDI input device for testing."""
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.closed = False
        self._events = []

    def poll(self) -> bool:
        return len(self._events) > 0

    def read(self, num_events: int) -> list:
        events = self._events[:num_events]
        self._events = self._events[num_events:]
        return events

    def close(self):
        self.closed = True

    def add_test_event(self, event):
        """Helper method to inject test events."""
        self._events.append(event)


class FakeMidiOutput:
    """Fake MIDI output device for testing."""
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.closed = False
        self.notes_on = []
        self.notes_off = []
        self.control_changes = []

    def note_on(self, note: int, velocity: int, channel: int = 0):
        self.notes_on.append((note, velocity, channel))

    def note_off(self, note: int, velocity: int = 0, channel: int = 0):
        self.notes_off.append((note, velocity, channel))

    def write_short(self, status: int, data1: int, data2: int):
        self.control_changes.append((status, data1, data2))

    def close(self):
        self.closed = True


class FakeMidiBackend(MidiBackend):
    """
    Fake MidiBackend implementation for testing.
    Allows complete control over MIDI behavior without real hardware.
    """
    def __init__(self):
        self._initialized = False
        self._devices = []
        self._default_input_id = -1
        self._default_output_id = -1
        self._created_inputs = []
        self._created_outputs = []

    def init(self) -> None:
        self._initialized = True

    def quit(self) -> None:
        self._initialized = False

    def get_count(self) -> int:
        return len(self._devices)

    def get_default_input_id(self) -> int:
        return self._default_input_id

    def get_default_output_id(self) -> int:
        return self._default_output_id

    def get_device_info(self, device_id: int) -> tuple:
        if 0 <= device_id < len(self._devices):
            return self._devices[device_id]
        return (b"Unknown", b"Unknown", 0, 0, 0)

    def create_input(self, device_id: int):
        inp = FakeMidiInput(device_id)
        self._created_inputs.append(inp)
        return inp

    def create_output(self, device_id: int):
        out = FakeMidiOutput(device_id)
        self._created_outputs.append(out)
        return out

    # Test helper methods
    def add_device(self, interface: bytes, name: bytes, is_input: int, is_output: int, opened: int = 0):
        """Add a fake MIDI device for testing."""
        self._devices.append((interface, name, is_input, is_output, opened))

    def set_default_input(self, device_id: int):
        self._default_input_id = device_id

    def set_default_output(self, device_id: int):
        self._default_output_id = device_id


class FakeUiDispatcher:
    """Fake UiDispatcher for testing."""
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


# Pytest Fixtures

@pytest.fixture
def fake_dispatcher():
    return FakeUiDispatcher()


@pytest.fixture
def fake_backend():
    """Create a FakeMidiBackend for testing."""
    return FakeMidiBackend()


@pytest.fixture
def fake_backend_with_devices():
    """Create a FakeMidiBackend with pre-configured devices."""
    backend = FakeMidiBackend()
    backend.add_device(b"USB", b"Test Input", is_input=1, is_output=0)
    backend.add_device(b"USB", b"Test Output", is_input=0, is_output=1)
    backend.set_default_input(0)
    backend.set_default_output(1)
    return backend
