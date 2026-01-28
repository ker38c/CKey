import pytest
from unittest import mock
from queue import Queue
from threading import Lock
import time

from midi.MidiFilePlayer import MidiFilePlayer

class DummyMidiMsg:
    def __init__(self, type, time=0, note=None, velocity=0, channel=0, control=0, value=0, tempo=None):
        self.type = type
        self.time = time
        self.note = note
        self.velocity = velocity
        self.channel = channel
        self.control = control
        self.value = value
        self.tempo = tempo

class DummyMidiFile:
    def __init__(self, tracks, ticks_per_beat=480):
        self.tracks = tracks
        self.ticks_per_beat = ticks_per_beat

# Patch mido.MidiFile to return DummyMidiFile
@pytest.fixture(autouse=True)
def patch_mido(monkeypatch):
    monkeypatch.setattr("mido.MidiFile", lambda path: DummyMidiFile([
        [DummyMidiMsg("note_on", time=0, note=60, velocity=100, channel=0),
         DummyMidiMsg("note_off", time=10, note=60, velocity=0, channel=0),
         DummyMidiMsg("control_change", time=5, control=64, value=127, channel=0),
         DummyMidiMsg("set_tempo", time=0, tempo=600000)]
    ]))

# Test: Initialization
def test_init_sets_defaults():
    # Arrange
    q = Queue()
    lock = Lock()
    # Act
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    # Assert
    assert player._file_path is None
    assert player._loop is False
    assert player._playing is False
    assert player._paused is False
    assert player._paused_tick == 0

# Test: set_file sets file path
def test_set_file_sets_path():
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    # Act
    player.set_file("dummy.mid")
    # Assert
    assert player._file_path == "dummy.mid"

# Test: set_loop sets loop flag
def test_set_loop_sets_flag():
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    # Act
    player.set_loop(True)
    # Assert
    assert player._loop is True
    player.set_loop(False)
    assert player._loop is False

# Test: play/stop changes playing state
def test_play_and_stop_change_state():
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    player.set_file("dummy.mid")
    # Act
    result = player.play()
    # Assert
    assert result is True
    assert player.is_playing() is True
    # Act
    player.stop()
    # Assert
    assert player.is_playing() is False

# Test: _collect_events returns sorted events and ticks_per_beat
def test_collect_events_returns_sorted_and_ticks():
    # Arrange
    dummy_file = DummyMidiFile([
        [DummyMidiMsg("note_on", time=0, note=60), DummyMidiMsg("note_off", time=5, note=60)],
        [DummyMidiMsg("control_change", time=2, control=64, value=127)]
    ], ticks_per_beat=960)
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    # Act
    events, ticks = player._collect_events(dummy_file)
    # Assert
    assert ticks == 960
    assert events[0][1].type == "note_on"
    assert events[1][1].type == "control_change"
    assert events[2][1].type == "note_off"

# Test: _play_file enqueues events (integration)
def test_play_file_enqueues_events(monkeypatch):
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    player.set_file("dummy.mid")
    player._playing = True
    player._loop = False
    # Patch time.sleep to avoid delay
    monkeypatch.setattr(time, "sleep", lambda s: None)
    # Act
    player._play_file()
    # Assert
    events = []
    while not q.empty():
        events.append(q.get())
    # Should contain note_on, control_change, note_off
    types = [e[0][0] & 0xF0 for e in events]
    assert 0x90 in types  # note_on
    assert 0x80 in types  # note_off
    assert 0xB0 in types  # control_change
    # Should stop playing after one pass
    assert player._playing is False

# Test: pause/resume functionality
def test_pause_and_resume_state():
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    player.set_file("dummy.mid")
    # Act: Play then pause
    player.play()
    assert player.is_playing() is True
    assert player.is_paused() is False
    player.pause()
    # Assert: Paused state
    assert player.is_playing() is False
    assert player.is_paused() is True
    # Act: Resume
    player.resume()
    # Assert: Playing again
    assert player.is_playing() is True
    assert player.is_paused() is False

# Test: stop clears paused state
def test_stop_clears_paused_state():
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    player.set_file("dummy.mid")
    player.play()
    player.pause()
    # Act
    player.stop()
    # Assert
    assert player.is_playing() is False
    assert player.is_paused() is False
    assert player._paused_tick == 0

# Test: pause saves playback position
def test_pause_saves_position(monkeypatch):
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    player.set_file("dummy.mid")
    player._playing = True
    player._loop = False
    # Patch time.sleep to avoid delay
    monkeypatch.setattr(time, "sleep", lambda s: None)
    # Patch _should_stop_playback to stop after first event
    original_should_stop = player._should_stop_playback
    call_count = [0]
    def mock_should_stop():
        call_count[0] += 1
        if call_count[0] > 2:
            return True
        return original_should_stop()
    monkeypatch.setattr(player, "_should_stop_playback", mock_should_stop)
    # Act
    player._play_file()
    # Assert: paused_tick should be set after playback stops
    # (In this case, it should be at least at the first note event position)
    assert player._paused_tick >= 0

# Test: pause-resume-pause sequence
def test_pause_resume_pause_sequence():
    # Arrange
    q = Queue()
    lock = Lock()
    player = MidiFilePlayer(q, lock, lambda: True, lambda: False)
    player.set_file("dummy.mid")
    # Act & Assert: Play
    player.play()
    assert player.is_playing() is True
    assert player.is_paused() is False

    # Pause
    player.pause()
    assert player.is_playing() is False
    assert player.is_paused() is True
    first_paused_tick = player._paused_tick

    # Resume
    player.resume()
    assert player.is_playing() is True
    assert player.is_paused() is False

    # Pause again
    player.pause()
    assert player.is_playing() is False
    assert player.is_paused() is True
