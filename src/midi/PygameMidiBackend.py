import pygame.midi
from typing import Any
from midi.MidiBackend import MidiBackend


class PygameMidiBackend(MidiBackend):
    """
    Concrete MidiBackend implementation using pygame.midi.
    
    This is the default backend used in production.
    """

    def init(self) -> None:
        pygame.midi.init()

    def quit(self) -> None:
        pygame.midi.quit()

    def get_count(self) -> int:
        return pygame.midi.get_count()

    def get_default_input_id(self) -> int:
        return pygame.midi.get_default_input_id()

    def get_default_output_id(self) -> int:
        return pygame.midi.get_default_output_id()

    def get_device_info(self, device_id: int) -> tuple:
        return pygame.midi.get_device_info(device_id)

    def create_input(self, device_id: int) -> Any:
        return pygame.midi.Input(device_id)

    def create_output(self, device_id: int) -> Any:
        return pygame.midi.Output(device_id)
