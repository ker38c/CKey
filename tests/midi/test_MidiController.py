import pytest
from queue import Empty
from src.midi.MidiController import MidiController


class TestMidiControllerInitialization:
    """Tests for MidiController initialization and setup."""

    def test_controller_accepts_custom_backend(self, fake_backend, fake_dispatcher):
        """MidiController should accept a custom MidiBackend via constructor."""
        # Act
        controller = MidiController(dispatcher=fake_dispatcher, midi_backend=fake_backend)

        # Assert
        assert controller.midi_backend is fake_backend
        assert fake_backend._initialized is True

    def test_controller_initialization_with_no_devices(self, fake_backend, fake_dispatcher):
        """Controller should initialize safely when no MIDI devices are available."""
        # Arrange - backend has no devices

        # Act
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend
        )

        # Assert
        assert controller.midi_in_id == -1
        assert controller.midi_out_id == -1
        assert controller.midiin is None
        assert controller.midiout is None


class TestMidiControllerDeviceDiscovery:
    """Tests for device discovery and connection."""

    def test_queries_devices_from_backend(self, fake_backend_with_devices, fake_dispatcher):
        """MidiController should query device info from the injected backend."""
        # Act
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend_with_devices
        )

        # Assert
        assert controller.midi_in_id == 0
        assert controller.midi_out_id == 1
        assert len(controller.midi_info) == 2

    def test_connect_creates_input_from_backend(self, fake_backend_with_devices, fake_dispatcher):
        """connect() should use backend.create_input() to create input device."""
        # Act
        MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend_with_devices
        )

        # Assert
        assert len(fake_backend_with_devices._created_inputs) == 1
        assert fake_backend_with_devices._created_inputs[0].device_id == 0

    def test_connect_creates_output_from_backend(self, fake_backend_with_devices, fake_dispatcher):
        """connect() should use backend.create_output() to create output device."""
        # Act
        MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend_with_devices
        )

        # Assert
        assert len(fake_backend_with_devices._created_outputs) == 1
        assert fake_backend_with_devices._created_outputs[0].device_id == 1

    def test_reconnect_reinitializes_backend(self, fake_backend_with_devices, fake_dispatcher):
        """Reconnecting should quit and reinit the backend."""
        # Arrange
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend_with_devices
        )
        controller.start = True  # Simulate running state

        # Act
        controller.connect()

        # Assert - backend should have been reinitialized
        assert fake_backend_with_devices._initialized is True


class TestMidiControllerEventQueue:
    """Tests for MIDI event queue management."""

    def test_event_queue_exists(self, fake_dispatcher, fake_backend):
        """Controller should have an event queue for MIDI events."""
        # Act
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend
        )

        # Assert
        assert controller.event_queue is not None
        assert hasattr(controller.event_queue, 'get')
        assert hasattr(controller.event_queue, 'put')

    def test_event_queue_starts_empty(self, fake_dispatcher, fake_backend):
        """Event queue should be empty on initialization."""
        # Act
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend
        )

        # Assert
        with pytest.raises(Empty):
            controller.event_queue.get_nowait()


class TestMidiControllerKeyEvents:
    """Tests for key event handling."""

    @pytest.fixture
    def controller(self, fake_dispatcher, fake_backend):
        return MidiController(dispatcher=fake_dispatcher, midi_backend=fake_backend)

    def test_add_key_event_enqueues_note_on(self, controller):
        """add_key_event with pressed=True should enqueue a Note On message."""
        # Arrange
        note_name = "C4"
        note_num = controller.handler.NOTE_NAME.index(note_name)
        velocity = 64

        # Act
        controller.add_key_event(note_name, True, velocity)

        # Assert
        event = controller.event_queue.get(timeout=1.0)
        expected = ([0x90, note_num, velocity, 0], 0)
        assert event == expected

    def test_add_key_event_enqueues_note_off(self, controller):
        """add_key_event with pressed=False should enqueue a Note Off message."""
        # Arrange
        note_name = "C4"
        note_num = controller.handler.NOTE_NAME.index(note_name)

        # Act
        controller.add_key_event(note_name, False, 0)

        # Assert
        event_off = controller.event_queue.get(timeout=1.0)
        expected_off = ([0x80, note_num, 0, 0], 0)
        assert event_off == expected_off

    def test_add_key_event_multiple_notes(self, controller):
        """Multiple key events should all be queued."""
        # Arrange
        notes = ["C4", "D4", "E4"]
        velocities = [64, 80, 100]

        # Act
        for note, velocity in zip(notes, velocities):
            controller.add_key_event(note, True, velocity)

        # Assert
        for note, velocity in zip(notes, velocities):
            event = controller.event_queue.get(timeout=1.0)
            note_num = controller.handler.NOTE_NAME.index(note)
            expected = ([0x90, note_num, velocity, 0], 0)
            assert event == expected

    def test_add_key_event_enqueues_on_then_off(self, controller):
        """Key press followed by release should produce both messages."""
        # Arrange
        note_name = "G4"
        note_num = controller.handler.NOTE_NAME.index(note_name)
        velocity = 80

        # Act
        controller.add_key_event(note_name, True, velocity)
        controller.add_key_event(note_name, False, 0)

        # Assert - Note On
        event_on = controller.event_queue.get(timeout=1.0)
        expected_on = ([0x90, note_num, velocity, 0], 0)
        assert event_on == expected_on

        # Assert - Note Off
        event_off = controller.event_queue.get(timeout=1.0)
        expected_off = ([0x80, note_num, 0, 0], 0)
        assert event_off == expected_off

    def test_add_key_event_with_edge_case_notes(self, controller):
        """Key events for first and last notes should work correctly."""
        # Arrange
        first_note = controller.handler.NOTE_NAME[0]
        last_note = controller.handler.NOTE_NAME[-1]

        # Act
        controller.add_key_event(first_note, True, 100)
        controller.add_key_event(last_note, True, 100)

        # Assert
        event1 = controller.event_queue.get(timeout=1.0)
        event2 = controller.event_queue.get(timeout=1.0)

        assert event1[0][1] == 0  # First note = index 0
        assert event2[0][1] == len(controller.handler.NOTE_NAME) - 1  # Last note


class TestMidiControllerDependencyInjection:
    """Tests for the dependency injection pattern."""

    def test_di_pattern_allows_backend_testing(self, fake_backend, fake_dispatcher):
        """DI pattern should allow easy testing with fake backend."""
        # Arrange
        fake_backend.add_device(b"Test", b"Device", 1, 1)

        # Act
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend
        )

        # Assert
        assert controller.midi_backend is fake_backend
        assert controller.midi_info[0] == (b"Test", b"Device", 1, 1, 0)

    def test_di_allows_dispatcher_testing(self, fake_backend, fake_dispatcher):
        """DI pattern should allow easy testing with fake dispatcher."""
        # Act
        controller = MidiController(
            dispatcher=fake_dispatcher,
            midi_backend=fake_backend
        )

        # Assert
        assert controller.dispatcher is fake_dispatcher

