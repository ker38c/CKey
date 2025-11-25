import tkinter
import tkinter.ttk
from tkinter import filedialog
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting
from midi.MidiController import MidiController

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, midi: MidiController, file_player=None, dispatcher=None):
        self.frame = tkinter.Frame(root)

        self.keyboard = KeyBoard(master=self.frame, setting=setting, midi=midi)
        self.keyboard.grid(row=0, column=0)
        # File playback controls placed under the keyboard
        self._selected_file = None
        self.file_player = file_player
        self.midi = midi

        controls_frame = tkinter.Frame(self.frame)
        controls_frame.grid(row=1, column=0, pady=8)

        self.file_label = tkinter.Label(controls_frame, text="No file")
        self.file_label.grid(row=0, column=0, columnspan=3, sticky='w')

        self.btn_choose = tkinter.Button(controls_frame, text="Choose MIDI file", command=self._choose_file)
        self.btn_choose.grid(row=1, column=0, padx=4)

        self.btn_play = tkinter.Button(controls_frame, text="Play", command=self._play_file)
        self.btn_play.grid(row=1, column=1, padx=4)

        self.btn_stop = tkinter.Button(controls_frame, text="Stop", command=self._stop_file)
        self.btn_stop.grid(row=1, column=2, padx=4)
        # Register keyboard with dispatcher for name-based calls
        if dispatcher is not None:
            try:
                dispatcher.register('keyboard', self.keyboard)
            except Exception:
                pass

    def _choose_file(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid;*.midi"), ("All files", "*")])
            if path:
                self._selected_file = path
                self.file_label.config(text=path)
                if self.file_player is not None:
                    try:
                        self.file_player.set_file(path)
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error choosing file: {e}")

    def _play_file(self):
        if not self._selected_file:
            return
        # ensure file_player knows the file
        if self.file_player is not None:
            try:
                self.file_player.set_file(self._selected_file)
                self.file_player.play()
            except Exception:
                pass

    def _stop_file(self):
        if self.file_player is not None:
            try:
                self.file_player.stop()
            except Exception:
                pass
