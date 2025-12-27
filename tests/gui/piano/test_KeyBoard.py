import sys
import types
import pytest

# Arrange: provide a safe fake tkinter before importing modules under test
class _FakeFrame:
    def __init__(self, *args, **kwargs):
        pass
    def config(self, **kwargs):
        # Accept any config calls
        pass
    def place(self, **kwargs):
        # Will be monkeypatched in tests
        pass


class _FakeButton(_FakeFrame):
    def bind(self, *args, **kwargs):
        pass


class _FakeCanvas(_FakeFrame):
    def pack(self, **kwargs):
        pass
    def bind(self, *args, **kwargs):
        pass
    def delete(self, *args, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def winfo_width(self):
        return 100
    def winfo_height(self):
        return 100
    def create_oval(self, *args, **kwargs):
        pass


fake_tkinter = types.SimpleNamespace(
    ACTIVE="active",
    NORMAL="normal",
    BOTH="both",
    Frame=_FakeFrame,
    Button=_FakeButton,
    Canvas=_FakeCanvas,
)
sys.modules.setdefault("tkinter", fake_tkinter)

from src.config.Setting import Setting
from src.gui.piano.KeyBoard import KeyBoard


@pytest.fixture
def setting():
    s = Setting()
    s.gui.Width = 1000
    s.gui.Height = 600
    s.gui.KeyPushedColor = "lightblue"
    return s


@pytest.fixture
def keyboard(setting):
    # Act: create keyboard with fake tkinter backend
    kb = KeyBoard(master=None, setting=setting, midi=None)
    return kb


def test__get_white_key_num_counts_all_white_keys(keyboard):
    # Arrange
    expected = sum(len(o) for o in keyboard.WHITE_KEY_NAME)
    # Act
    actual = keyboard._get_white_key_num()
    # Assert
    assert actual == expected


def test__find_key_returns_key_when_exists(keyboard):
    # Arrange
    name = keyboard.white_keys[0].name
    # Act
    key = keyboard._find_key(name)
    # Assert
    assert key is keyboard.white_keys[0]


def test__find_key_returns_none_for_empty_or_unknown(keyboard):
    # Arrange
    # Act & Assert: empty string -> None
    assert keyboard._find_key("") is None
    # Act & Assert: unknown -> None
    assert keyboard._find_key("NoSuchKey") is None


def test_set_key_state_calls_config_on_found_key(keyboard, monkeypatch):
    # Arrange
    target = keyboard.white_keys[1]
    called = {}
    def fake_config(**kwargs):
        called.update(kwargs)
    monkeypatch.setattr(target, "config", fake_config)
    # Act
    keyboard.set_key_state(target.name, "disabled")
    # Assert
    assert called.get("state") == "disabled"


def test_set_key_state_ignores_empty_name(keyboard, capsys):
    # Arrange
    # Act
    keyboard.set_key_state("", "disabled")
    # Assert
    # No exception and no output indicating config call
    captured = capsys.readouterr()
    assert captured.out == ""


def test_set_sustain_sets_active_and_normal(keyboard, monkeypatch):
    # Arrange
    states = []
    def fake_config(**kwargs):
        states.append(kwargs.get("state"))
    monkeypatch.setattr(keyboard.sustain, "config", fake_config)
    # Act
    keyboard.set_sustain(True)
    keyboard.set_sustain(False)
    # Assert
    assert states == [fake_tkinter.ACTIVE, fake_tkinter.NORMAL]


def test_calculate_dimensions_sets_expected_sizes(keyboard):
    # Arrange
    width = 1280
    # Act
    keyboard._calculate_dimensions(width)
    # Assert
    num_white = keyboard._get_white_key_num()
    assert keyboard.KEY_WIDTH == int(width / num_white)
    assert keyboard.KEY_HEIGHT == keyboard.KEY_WIDTH * 5
    assert keyboard.PEDAL_WIDTH == keyboard.KEY_WIDTH * 3
    assert keyboard.PEDAL_HEIGHT == keyboard.KEY_WIDTH * 3
    assert keyboard.BLACK_KEY_WIDTH == keyboard.KEY_WIDTH / 2
    assert keyboard.BLACK_KEY_HEIGHT == keyboard.KEY_HEIGHT * 0.6
    assert keyboard.width == width
    assert keyboard.height == keyboard.KEY_HEIGHT + keyboard.PEDAL_HEIGHT


def test_place_keyboard_places_white_keys_sequentially(keyboard, monkeypatch):
    # Arrange
    calls = []
    for i, key in enumerate(keyboard.white_keys):
        def _mk(idx):
            def _place(**kwargs):
                calls.append((idx, kwargs))
            return _place
        monkeypatch.setattr(key, "place", _mk(i))
    # Ensure dimensions are up-to-date
    keyboard._calculate_dimensions(keyboard.setting.gui.Width)
    # Act
    keyboard._place_keyboard()
    # Assert
    for idx, kwargs in calls:
        assert kwargs["x"] == idx * keyboard.KEY_WIDTH
        assert kwargs["y"] == 0
        assert kwargs["width"] == keyboard.KEY_WIDTH
        assert kwargs["height"] == keyboard.KEY_HEIGHT


def test_place_keyboard_places_non_empty_black_keys_with_offset(keyboard, monkeypatch):
    # Arrange
    calls = []
    for i, key in enumerate(keyboard.black_keys):
        def _mk(idx, name):
            def _place(**kwargs):
                calls.append((idx, name, kwargs))
            return _place
        monkeypatch.setattr(key, "place", _mk(i, key.name))
    keyboard._calculate_dimensions(keyboard.setting.gui.Width)
    # Act
    keyboard._place_keyboard()
    # Assert
    for idx, name, kwargs in calls:
        if name == "":
            # Empty black keys should not be placed; no call recorded for them
            continue
        assert kwargs["x"] == idx * keyboard.KEY_WIDTH + keyboard.BLACK_KEY_WIDTH * 1.5
        assert kwargs["y"] == 0
        assert kwargs["width"] == keyboard.BLACK_KEY_WIDTH
        assert kwargs["height"] == keyboard.BLACK_KEY_HEIGHT


def test_place_keyboard_places_sustain_centered_below_keys(keyboard, monkeypatch):
    # Arrange
    placed = {}
    def fake_place(**kwargs):
        placed.update(kwargs)
    monkeypatch.setattr(keyboard.sustain, "place", fake_place)
    keyboard._calculate_dimensions(keyboard.setting.gui.Width)
    # Act
    keyboard._place_keyboard()
    # Assert
    assert placed["x"] == keyboard.setting.gui.Width / 2
    assert placed["y"] == keyboard.KEY_HEIGHT
    assert placed["width"] == keyboard.PEDAL_WIDTH
    assert placed["height"] == keyboard.PEDAL_HEIGHT
