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
        self._paused = False
        self._paused_tick = 0
        self._paused_tempo = 500000

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

    def play(self):
        """Request playback start. Returns True if playback was requested."""
        with self.lock:
            if not self._file_path:
                return False
            self._playing = True
            return True

    def pause(self):
        """Request playback pause. Can be resumed from the paused position."""
        with self.lock:
            if self._playing and not self._paused:
                self._paused = True
                self._playing = False

    def resume(self):
        """Resume playback from paused position."""
        with self.lock:
            if self._paused and not self._playing:
                # Reset pause position since we're resuming from the saved tick
                # The next iteration of _play_file will use _paused_tick/tempo
                self._paused = False
                self._playing = True

    def stop(self):
        """Request playback stop and reset paused state."""
        with self.lock:
            self._playing = False
            self._paused = False
            self._paused_tick = 0
            self._paused_tempo = 500000

    def is_playing(self) -> bool:
        with self.lock:
            return bool(self._playing)

    def is_paused(self) -> bool:
        """Check if playback is paused."""
        with self.lock:
            return bool(self._paused)

    def set_file(self, file_path: str):
        """Set the path to the MIDI file to play."""
        self._file_path = file_path

    def set_loop(self, loop: bool):
        """Set whether to loop playback while the start flag remains set."""
        self._loop = bool(loop)

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
            if self._should_stop_playback():
                break

            mid = self._load_midi()
            if mid is None:
                break

            events, ticks_per_beat = self._collect_events(mid)

            # Determine starting position (resume from pause or from beginning)
            with self.lock:
                if self._paused:
                    current_tempo = self._paused_tempo
                    start_tick = self._paused_tick
                    # Clear pause flags for this iteration
                    self._paused = False
                else:
                    current_tempo = 500000
                    start_tick = 0

            prev_tick = start_tick

            for abs_tick, msg in events:
                if self._should_stop_playback():
                    return

                # Skip events before resume point
                if abs_tick < start_tick:
                    continue

                delta_ticks = abs_tick - prev_tick
                self._sleep_for_delta(delta_ticks, ticks_per_beat, current_tempo)
                prev_tick = abs_tick

                # Store current position before emitting message in case of pause
                with self.lock:
                    self._paused_tick = abs_tick
                    self._paused_tempo = current_tempo

                current_tempo = self._emit_message(msg, current_tempo)

            if self._post_file_pass():
                break

    def _should_stop_playback(self) -> bool:
        with self.lock:
            return self.get_end_flag() or (not self._playing)

    def _sleep_for_delta(self, delta_ticks: int, ticks_per_beat: int, tempo: int) -> None:
        if delta_ticks <= 0:
            return
        try:
            seconds = mido.tick2second(delta_ticks, ticks_per_beat, tempo)
        except Exception:
            seconds = delta_ticks * 0.001
        if seconds > 0:
            time.sleep(seconds)

    def _emit_message(self, msg, current_tempo: int) -> int:
        msg_type = getattr(msg, 'type', None)
        if msg_type == 'set_tempo':
            return getattr(msg, 'tempo', current_tempo)

        if msg_type in ('note_on', 'note_off'):
            note = getattr(msg, 'note', None)
            velocity = getattr(msg, 'velocity', 0)
            channel = getattr(msg, 'channel', 0)
            if note is None:
                return current_tempo
            if msg_type == 'note_off' or (msg_type == 'note_on' and velocity == 0):
                status = 0x80 | (channel & 0x0F)
                data1 = note
                data2 = 0
            else:
                status = 0x90 | (channel & 0x0F)
                data1 = note
                data2 = velocity
            self.event_queue.put(([status, data1, data2, 0], time.time()))
            return current_tempo

        if msg_type == 'control_change':
            channel = getattr(msg, 'channel', 0)
            control = getattr(msg, 'control', 0)
            value = getattr(msg, 'value', 0)
            status = 0xB0 | (channel & 0x0F)
            self.event_queue.put(([status, control, value, 0], time.time()))
        return current_tempo

    def _post_file_pass(self) -> bool:
        """Update loop/playback flags after one pass. Return True to break outer loop."""
        with self.lock:
            if not self._loop:
                self._playing = False
                return True
            return not self._playing
