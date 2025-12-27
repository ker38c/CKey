import sys
import types
import threading
import unittest
from queue import Queue
from unittest import mock

# Provide safe fake tkinter and pygame.midi before importing MidiReceiver
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

    class Input:
        def __init__(self, id):
            pass
        def poll(self):
            return False
        def read(self, n):
            return []
        def close(self):
            pass

fake_pygame = types.SimpleNamespace(midi=FakeMidiModule())
sys.modules.setdefault("pygame", types.SimpleNamespace(midi=fake_pygame.midi))
sys.modules.setdefault("pygame.midi", fake_pygame.midi)

# Import the class under test after fakes are in place
from src.midi.MidiReceiver import MidiReceiver


class TestMidiReceiver(unittest.TestCase):
    """Tests for MidiReceiver. Each test follows Arrange-Act-Assert pattern."""

    def test_wait_connect_returns_when_start_true(self):
        # Arrange
        flags = {"start": True, "end": False}
        q = Queue()
        receiver = MidiReceiver(
            event_queue=q,
            lock=threading.Lock(),
            start_flag_getter=lambda: flags["start"],
            end_flag_getter=lambda: flags["end"]
        )

        # Act: call wait_connect (should return quickly because start flag is True)
        receiver._wait_connect()

        # Assert: if we reached here, the function returned (no explicit state change expected)
        self.assertTrue(flags["start"])  # sanity assertion

    def test_wait_connect_returns_when_end_true(self):
        # Arrange
        flags = {"start": False, "end": True}
        q = Queue()
        receiver = MidiReceiver(
            event_queue=q,
            lock=threading.Lock(),
            start_flag_getter=lambda: flags["start"],
            end_flag_getter=lambda: flags["end"]
        )

        # Act: call wait_connect (should return quickly because end flag is True)
        receiver._wait_connect()

        # Assert: function returned; flags unchanged
        self.assertTrue(flags["end"])  # sanity assertion

    def test_run_puts_events_into_queue(self):
        # Arrange
        flags = {"start": True, "end": False}
        q = Queue()

        class FakeInputDevice:
            def __init__(self):
                self._calls = 0
            def poll(self):
                self._calls += 1
                # Return True only on the first call, then False
                return self._calls == 1
            def read(self, n):
                return [([0x90, 60, 100, 0], 0)]
            def close(self):
                pass

        receiver = MidiReceiver(
            event_queue=q,
            lock=threading.Lock(),
            start_flag_getter=lambda: flags["start"],
            end_flag_getter=lambda: flags["end"]
        )
        receiver.set_input_device(FakeInputDevice())

        # Act: run receiver.run() in background thread to simulate live polling
        t = threading.Thread(target=receiver.run)
        t.start()

        # Assert: an event should appear on the queue
        evt = q.get(timeout=1.0)
        self.assertIsNotNone(evt)

        # Cleanup: signal end and join thread
        flags["end"] = True
        t.join(timeout=1.0)
        self.assertFalse(t.is_alive())


if __name__ == "__main__":
    unittest.main()
