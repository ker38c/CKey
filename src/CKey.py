import threading
import tkinter
from gui.MainWindow import MainWindow
from gui.UiDispatcher import UiDispatcher
from config.Setting import Setting
from midi.MidiController import MidiController
from midi.MidiFilePlayer import MidiFilePlayer
from midi.PygameMidiBackend import PygameMidiBackend

def main():
    setting = Setting()
    backend = PygameMidiBackend()
    midi = MidiController(dispatcher=None, midi_backend=backend)

    root = tkinter.Tk()
    dispatcher = UiDispatcher(root)
    dispatcher.start()
    
    # Create MidiFilePlayer for file playback (system start/end separate)
    file_player = MidiFilePlayer(
        event_queue=midi.event_queue,
        lock=midi.lock,
        start_flag_getter=lambda: midi.start,
        end_flag_getter=lambda: midi.end
    )
    
    window = MainWindow(root, setting, midi, file_player, dispatcher)

    # Pass dispatcher to MidiController for UI updates
    midi.dispatcher = dispatcher
    midi.handler.set_dispatcher(dispatcher)
    midi.init_keyboard(window.piano_tab.keyboard)

    # MIDI receive thread
    midi_recv_thread = threading.Thread(target=midi.receiver.run)
    midi_recv_thread.start()

    # MIDI process thread (handler thread)
    midi_proc_thread = threading.Thread(target=midi.handler.run)
    midi_proc_thread.start()

    # MIDI file player thread
    midi_file_thread = threading.Thread(target=file_player.run)
    midi_file_thread.start()

    try:
        # gui
        window.start()
    except KeyboardInterrupt:
        print("User requested exit.")
    finally:
        # exit
        with midi.lock:
            midi.end = True
        midi_recv_thread.join(timeout=2.0)
        midi_proc_thread.join(timeout=2.0)
        if midi_file_thread is not None:
            midi_file_thread.join(timeout=2.0)
        print("CKey exit")


if __name__ == "__main__":
    main()