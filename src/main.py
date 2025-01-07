import threading
from gui.MainWindow import MainWindow
from config.Setting import Setting
from midi.MidiController import MidiController

def main():
    setting = Setting()
    midi = MidiController()
    window = MainWindow(setting, midi)
    midi.init_keyboard(window.piano_tab.keyboard)

    # MIDI thread
    midi_thread = threading.Thread(target=midi.receive)
    midi_thread.start()

    # gui
    window.start()

    midi.end = True
    midi_thread.join()
    print("CKey exit")


if __name__ == "__main__":
    main()