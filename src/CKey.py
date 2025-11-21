import threading
from gui.MainWindow import MainWindow
from config.Setting import Setting
from midi.MidiController import MidiController

def main():
    setting = Setting()
    midi = MidiController()
    window = MainWindow(setting, midi)

    # Pass dispatcher to MidiController for UI updates
    midi.dispatcher = window.dispatcher
    midi.handler.set_dispatcher(window.dispatcher)
    midi.init_keyboard(window.piano_tab.keyboard)

    # MIDI receive thread
    midi_recv_thread = threading.Thread(target=midi.receiver.run)
    midi_recv_thread.start()

    # MIDI process thread (handler thread)
    midi_proc_thread = threading.Thread(target=midi.handler.run)
    midi_proc_thread.start()

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
        print("CKey exit")


if __name__ == "__main__":
    main()