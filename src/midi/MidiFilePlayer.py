import time
from threading import Lock
from queue import Queue
import mido

class MidiFilePlayer:
    """
    Plays MIDI files and emits events into the shared event queue.

    This class mirrors the abstraction level of `MidiReceiver` so it can be
    used interchangeably by code that expects an external MIDI source.
    """

    def __init__(self, event_queue: Queue, lock: Lock, start_flag_getter, end_flag_getter):
        """
        Args:
            event_queue: Queue to put parsed MIDI events into
            lock: Lock for coordinating access to start/end flags
            start_flag_getter: Callable that returns whether playback should start
            end_flag_getter: Callable that returns whether the app is shutting down
        """
        self.event_queue = event_queue
        self.lock = lock
        self.get_start_flag = start_flag_getter
        self.get_end_flag = end_flag_getter

        self._file_path = None
        self._loop = False
        self._playing = False

    def run(self):
        """
        Main loop: wait for start flag, then play the configured MIDI file.
        After playback finishes (or start flag is cleared), return to waiting.
        """
        try:
            while True:
                with self.lock:
                    if self.get_end_flag():
                        break

                # if no file configured or playback not requested, wait briefly
                if not self._file_path or not self._playing:
                    time.sleep(0.1)
                    continue

                # Play the configured file (handles looping internally)
                self._play_file()

        finally:
            # nothing special to clean up
            print("MIDI file player thread exit")

    def _load_midi(self):
        """Load the configured MIDI file, returning a MidiFile or None."""
        try:
            return mido.MidiFile(self._file_path)
        except Exception as e:
            print(f"Failed to open MIDI file '{self._file_path}': {e}")
            return None

    def _collect_events(self, mid):
        """Collect and return a sorted list of (abs_tick, msg) and ticks_per_beat."""
        events = []
        for track in mid.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += getattr(msg, 'time', 0)
                events.append((abs_tick, msg))
        events.sort(key=lambda x: x[0])
        ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
        return events, ticks_per_beat

    def _play_file(self):
        """Play the currently configured file once or repeatedly while _playing/_loop are set."""
        while True:
            with self.lock:
                if self.get_end_flag() or not self._playing:
                    break

            mid = self._load_midi()
            if mid is None:
                break

            events, ticks_per_beat = self._collect_events(mid)

            # playback state
            current_tempo = 500000
            prev_tick = 0

            for abs_tick, msg in events:
                # stop if playback or system state changed
                with self.lock:
                    if not self._playing or self.get_end_flag():
                        return

                delta_ticks = abs_tick - prev_tick
                if delta_ticks > 0:
                    try:
                        seconds = mido.tick2second(delta_ticks, ticks_per_beat, current_tempo)
                    except Exception:
                        seconds = delta_ticks * 0.001
                    if seconds > 0:
                        time.sleep(seconds)
                prev_tick = abs_tick

                # handle tempo changes
                if getattr(msg, 'type', None) == 'set_tempo':
                    current_tempo = getattr(msg, 'tempo', current_tempo)
                    continue

                # translate messages to event queue
                if getattr(msg, 'type', None) in ('note_on', 'note_off'):
                    note = getattr(msg, 'note', None)
                    velocity = getattr(msg, 'velocity', 0)
                    channel = getattr(msg, 'channel', 0)
                    if note is None:
                        continue
                    if msg.type == 'note_off' or (msg.type == 'note_on' and velocity == 0):
                        status = 0x80 | (channel & 0x0F)
                        data1 = note
                        data2 = 0
                    else:
                        status = 0x90 | (channel & 0x0F)
                        data1 = note
                        data2 = velocity
                    self.event_queue.put(([status, data1, data2, 0], time.time()))

                elif getattr(msg, 'type', None) == 'control_change':
                    channel = getattr(msg, 'channel', 0)
                    control = getattr(msg, 'control', 0)
                    value = getattr(msg, 'value', 0)
                    status = 0xB0 | (channel & 0x0F)
                    self.event_queue.put(([status, control, value, 0], time.time()))

            # finished one pass over the file
            with self.lock:
                if not self._loop:
                    self._playing = False
                    break
                if not self._playing:
                    break

    def set_file(self, file_path: str):
        """Set the path to the MIDI file to play."""
        self._file_path = file_path

    def set_loop(self, loop: bool):
        """Set whether to loop playback while the start flag remains set."""
        self._loop = bool(loop)

    def play(self):
        """Request playback start. Returns True if playback was requested."""
        with self.lock:
            if not self._file_path:
                return False
            self._playing = True
            return True

    def stop(self):
        """Request playback stop."""
        with self.lock:
            self._playing = False

    def is_playing(self) -> bool:
        with self.lock:
            return bool(self._playing)
