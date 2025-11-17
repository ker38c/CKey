import pygame.midi
import time
from threading import Lock
from queue import Queue


class MidiReceiver:
    """Handles MIDI device input in a separate thread."""
    
    def __init__(self, event_queue: Queue, lock: Lock, start_flag_getter, end_flag_getter):
        """
        Initialize MidiReceiver.
        
        Args:
            event_queue: Queue to put received MIDI events into
            lock: Threading lock for accessing shared state
            start_flag_getter: Callable that returns the current start flag value
            end_flag_getter: Callable that returns the current end flag value
        """
        self.event_queue = event_queue
        self.lock = lock
        self.get_start_flag = start_flag_getter
        self.get_end_flag = end_flag_getter
        self.midiin = None
        self.midi_in_id = pygame.midi.get_default_input_id()

    def run(self):
        """
        Main receive loop. Polls the MIDI input device for events and puts them in the queue.
        """
        try:
            while True:
                with self.lock:
                    if self.get_end_flag():
                        break

                self.wait_connect()

                if self.midiin is not None:
                    if self.midiin.poll():
                        recv = self.midiin.read(1)
                        for event in recv:
                            self.event_queue.put(event)

                time.sleep(0.001)

        finally:
            if self.midiin is not None:
                try:
                    self.midiin.close()
                except:
                    pass

            print("MIDI receive thread exit")

    def wait_connect(self):
        """Wait for the start flag to be set or end flag to be set."""
        while True:
            with self.lock:
                if self.get_start_flag() or self.get_end_flag():
                    return
            time.sleep(0.1)

    def set_input_device(self, midiin):
        """Set the MIDI input device."""
        self.midiin = midiin
