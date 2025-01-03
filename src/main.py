import threading
from gui.MainWindow import MainWindow
from config.Setting import Setting
from midi.MidiController import MidiController

def main():
    setting = Setting()
    window = MainWindow(setting)
    midi = MidiController(window.piano_tab.keyboard)

    if midi.connect():
        # MIDI thread
        midi_thread = threading.Thread(target=midi.receive)
        midi_thread.start()

    else:
        print("midi device is not connected.")

    # gui
    window.start()

    if midi.start:
        midi.start = False
        midi_thread.join()
    print("CKey exit")


if __name__ == "__main__":
    main()