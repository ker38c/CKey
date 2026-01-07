from abc import ABC, abstractmethod
from typing import Any


class MidiBackend(ABC):
    """
    Abstract base class for MIDI backend implementations.
    
    This abstraction allows for dependency injection and easier testing
    by decoupling MidiController from the concrete pygame.midi implementation.
    """

    @abstractmethod
    def init(self) -> None:
        """Initialize the MIDI system."""
        pass

    @abstractmethod
    def quit(self) -> None:
        """Shutdown the MIDI system."""
        pass

    @abstractmethod
    def get_count(self) -> int:
        """Return the number of available MIDI devices."""
        pass

    @abstractmethod
    def get_default_input_id(self) -> int:
        """Return the default MIDI input device ID, or -1 if none."""
        pass

    @abstractmethod
    def get_default_output_id(self) -> int:
        """Return the default MIDI output device ID, or -1 if none."""
        pass

    @abstractmethod
    def get_device_info(self, device_id: int) -> tuple:
        """
        Return device info tuple: (interface, name, is_input, is_output, opened).
        All values are bytes or int.
        """
        pass

    @abstractmethod
    def create_input(self, device_id: int) -> Any:
        """Create and return a MIDI input device object."""
        pass

    @abstractmethod
    def create_output(self, device_id: int) -> Any:
        """Create and return a MIDI output device object."""
        pass
