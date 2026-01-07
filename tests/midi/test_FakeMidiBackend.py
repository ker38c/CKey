import sys
import os
import pytest

# Import test doubles directly from conftest definitions
sys.path.insert(0, os.path.dirname(__file__))

from conftest import FakeMidiBackend, FakeMidiInput, FakeMidiOutput


class TestFakeMidiBackend:
    """Tests for FakeMidiBackend itself to ensure it's a valid test double."""

    def test_fake_backend_init_quit(self):
        backend = FakeMidiBackend()
        assert backend._initialized is False

        backend.init()
        assert backend._initialized is True

        backend.quit()
        assert backend._initialized is False

    def test_fake_backend_device_management(self):
        backend = FakeMidiBackend()
        backend.add_device(b"USB", b"Piano", is_input=1, is_output=0)
        backend.add_device(b"USB", b"Synth", is_input=0, is_output=1)

        assert backend.get_count() == 2
        assert backend.get_device_info(0) == (b"USB", b"Piano", 1, 0, 0)
        assert backend.get_device_info(1) == (b"USB", b"Synth", 0, 1, 0)

    def test_fake_input_device(self):
        inp = FakeMidiInput(0)
        assert inp.poll() is False

        inp.add_test_event(([0x90, 60, 100, 0], 0))
        assert inp.poll() is True

        events = inp.read(10)
        assert len(events) == 1
        assert inp.poll() is False

    def test_fake_output_device(self):
        out = FakeMidiOutput(0)
        out.note_on(60, 100)
        out.note_off(60)
        out.write_short(0xB0, 0x40, 127)

        assert out.notes_on == [(60, 100, 0)]
        assert out.notes_off == [(60, 0, 0)]
        assert out.control_changes == [(0xB0, 0x40, 127)]

    def test_fake_backend_input_creation(self):
        """Backend should create FakeMidiInput instances."""
        backend = FakeMidiBackend()
        inp1 = backend.create_input(0)
        inp2 = backend.create_input(1)

        assert isinstance(inp1, FakeMidiInput)
        assert isinstance(inp2, FakeMidiInput)
        assert inp1.device_id == 0
        assert inp2.device_id == 1
        assert len(backend._created_inputs) == 2

    def test_fake_backend_output_creation(self):
        """Backend should create FakeMidiOutput instances."""
        backend = FakeMidiBackend()
        out1 = backend.create_output(0)
        out2 = backend.create_output(1)

        assert isinstance(out1, FakeMidiOutput)
        assert isinstance(out2, FakeMidiOutput)
        assert out1.device_id == 0
        assert out2.device_id == 1
        assert len(backend._created_outputs) == 2

    def test_fake_backend_default_ids(self):
        """Backend should track default input/output device IDs."""
        backend = FakeMidiBackend()
        assert backend.get_default_input_id() == -1
        assert backend.get_default_output_id() == -1

        backend.set_default_input(0)
        backend.set_default_output(1)

        assert backend.get_default_input_id() == 0
        assert backend.get_default_output_id() == 1
