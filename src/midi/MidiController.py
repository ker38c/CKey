from threading import Lock
from queue import Queue
from gui.piano.KeyBoard import KeyBoard
from enum import IntEnum
from midi.MidiReceiver import MidiReceiver
from midi.MidiHandler import MidiHandler
from midi.MidiBackend import MidiBackend


class MidiDeviceInfo(IntEnum):
    """MIDI device information indices"""
    INTERFACE = 0
    NAME = 1
    INPUT = 2
    OUTPUT = 3
    OPENED = 4


class MidiController:
    """
    Manager class for MIDI device I/O and event handling.
    
    Coordinates MidiReceiver (input thread) and MidiHandler (processing thread)
    while managing MIDI device connections and dispatching UI updates.
    """
    
    def __init__(self, dispatcher, midi_backend: MidiBackend):
        self.midi_backend = midi_backend
        self.midi_backend.init()

        self.dispatcher = dispatcher
        self.lock = Lock()
        self.event_queue = Queue()
        self.start = False
        self.end = False
        self.midiin = None
        self.midiout = None

        self.midi_in_id = self.midi_backend.get_default_input_id()
        self.midi_out_id = self.midi_backend.get_default_output_id()
        midi_count = self.midi_backend.get_count()
        self.midi_info = []

        for i in range(midi_count):
            info = self.midi_backend.get_device_info(i)
            self.midi_info.append(info)

        # Create MidiReceiver and MidiHandler with closures to access self.start and self.end
        self.receiver = MidiReceiver(
            event_queue=self.event_queue,
            lock=self.lock,
            start_flag_getter=lambda: self.start,
            end_flag_getter=lambda: self.end
        )
        
        self.handler = MidiHandler(
            event_queue=self.event_queue,
            lock=self.lock,
            end_flag_getter=lambda: self.end,
            dispatcher=self.dispatcher
        )

        self.connect()

    def init_keyboard(self, keyboard: KeyBoard):
        """Forward keyboard to the handler; controller does not keep it as a member."""
        try:
            self.handler.set_keyboard(keyboard)
        except Exception:
            pass

    def connect(self) -> bool:
        """Connect to MIDI input and output devices and hand them to subcomponents."""
        with self.lock:
            if self.start:
                # reinitialize
                self.start = False
                self.midiin = None
                self.midiout = None
                try:
                    self.midi_backend.quit()
                except Exception:
                    pass
                self.midi_backend.init()
                print("MidiController restart.")

            try:
                if self.midi_in_id != -1:
                    self.midiin = self.midi_backend.create_input(self.midi_in_id)
                if self.midi_out_id != -1:
                    self.midiout = self.midi_backend.create_output(self.midi_out_id)

                # Pass devices to receiver and handler
                try:
                    self.receiver.set_input_device(self.midiin)
                except Exception:
                    pass
                try:
                    self.handler.set_output_device(self.midiout)
                except Exception:
                    pass

                self.start = True
                return True
            except Exception:
                return False

    def set_dispatcher(self, dispatcher):
        """Update dispatcher reference for manager and handler."""
        self.dispatcher = dispatcher
        try:
            self.handler.set_dispatcher(dispatcher)
        except Exception:
            pass

    def add_key_event(self, key_name: str, is_note_on: bool, velocity: int = 100):
        """
        Add a key event to the event queue (for testing or manual key presses).
        """
        # Find the MIDI note number for the key name using handler mapping
        try:
            note_num = self.handler.NOTE_NAME.index(key_name)
        except Exception:
            return

        status = 0x90 if is_note_on else 0x80
        data2 = velocity if is_note_on else 0

        event = ([status, note_num, data2, 0], 0)
        self.event_queue.put(event)
