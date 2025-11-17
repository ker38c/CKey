import tkinter
from queue import Queue, Empty
from threading import Lock


class MidiHandler:
    """Handles MIDI event processing in a separate thread."""
    
    def __init__(self, event_queue: Queue, lock: Lock, end_flag_getter, dispatcher=None):
        """
        Initialize MidiHandler.
        
        Args:
            event_queue: Queue to get MIDI events from
            lock: Threading lock for accessing shared state
            end_flag_getter: Callable that returns the current end flag value
            dispatcher: Optional UiDispatcher for thread-safe UI updates
        """
        self.event_queue = event_queue
        self.lock = lock
        self.get_end_flag = end_flag_getter
        self.dispatcher = dispatcher
        self.midiout = None
        self.keyboard = None
        
        # NOTE_NAME mapping for MIDI key number to note name conversion
        self.NOTE_NAME = [
            "C-2","C#-2","D-2","D#-2","E-1","F-1","F#-1","G-2","G#-2","A-2","A#-2","B-2",
            "C-1","C#-1","D-1","D#-1","E-1","F-1","F#-1","G-1","G#-1",
            # 88-key piano begin
            "A-1", "A#-1", "B-1",
            "C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
            "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
            "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
            "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
            "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
            "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
            "C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6",
            "C7",
            # 88-key piano end
            "C#7", "D7", "D#7", "E7", "F7", "F#7", "G7", "G#7", "A7", "A#7", "B7",
            "C8", "C#8", "D8", "D#8", "E8", "F8", "F#8", "G8"
        ]

    def run(self):
        """
        Main handler loop. Processes events from the queue.
        """
        while True:
            try:
                event = self.event_queue.get(timeout=1.0)
                self.handler(event)
            except Empty:
                with self.lock:
                    if self.get_end_flag():
                        print("midi process thread exit")
                        return
            except Exception:
                with self.lock:
                    if self.get_end_flag():
                        print("midi process thread exit")
                        return

    def handler(self, recv: list):
        """
        Process a MIDI event.
        
        Args:
            recv: MIDI event tuple ([status, data1, data2, extra], timestamp)
        """
        [status, data1, data2, _], _ = recv

        # Note Off
        if (status & 0xF0) == 0x80:
            self.note_off(key_name=data1)

        # Note On
        elif (status & 0xF0) == 0x90:
            self.note_on(key_name=data1, velocity=data2)

        # Control Change
        elif (status & 0xF0) == 0xB0:
            # Sustain On/Off
            if data1 == 0x40:
                self.sustain_change(status=status, value=data2)

    def note_on(self, key_name: int, velocity: int):
        """
        Handle Note On event.
        
        Args:
            key_name: MIDI note number
            velocity: Note velocity (0-127)
        """
        key_name_str = self.get_key_name(key_name)
        if key_name_str == "":
            return
        if self.midiout is not None:
            self.midiout.note_on(note=key_name, velocity=velocity)

        if self.dispatcher:
            self.dispatcher.post_to('keyboard', 'set_key_state', key_name_str, tkinter.ACTIVE)

    def note_off(self, key_name: int):
        """
        Handle Note Off event.
        
        Args:
            key_name: MIDI note number
        """
        key_name_str = self.get_key_name(key_name)
        if key_name_str == "":
            return
        if self.midiout is not None:
            self.midiout.note_off(note=key_name)

        if self.dispatcher:
            self.dispatcher.post_to('keyboard', 'set_key_state', key_name_str, tkinter.NORMAL)

    def sustain_change(self, status: int, value: int):
        """
        Handle Sustain (Control Change) event.
        
        Args:
            status: MIDI status byte
            value: Control value (0-127)
        """
        if self.midiout is not None:
            self.midiout.write_short(status, 0x40, value)

        if self.dispatcher:
            self.dispatcher.post_to('keyboard', 'set_sustain', value > 0)

    def get_key_name(self, key_num: int) -> str:
        """Get the note name for a given MIDI key number."""
        if (key_num < 0) or (key_num >= 128):
            return ""
        return self.NOTE_NAME[key_num]

    def set_output_device(self, midiout):
        """Set the MIDI output device."""
        self.midiout = midiout

    def set_keyboard(self, keyboard):
        """Set the keyboard for UI updates."""
        self.keyboard = keyboard

    def set_dispatcher(self, dispatcher):
        """Set the UI dispatcher for thread-safe UI updates."""
        self.dispatcher = dispatcher
