import tkinter
import tkinter.ttk
from tkinter import filedialog
import os
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting
from midi.MidiController import MidiController

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, midi: MidiController, file_player=None, dispatcher=None):
        self.frame = tkinter.Frame(root)

        self.keyboard_frame = tkinter.Frame(self.frame)
        self.keyboard_frame.grid(row=0, column=0)

        self.keyboard = KeyBoard(master=self.keyboard_frame, setting=setting, midi=midi)
        self.keyboard.pack(fill=tkinter.BOTH, expand=True)

        # File playback controls placed under the keyboard
        self._selected_file = None
        self.file_player = file_player
        self.midi = midi
        self.setting = setting

        self.controls_frame = tkinter.Frame(self.frame)
        self.controls_frame.grid(row=1, column=0, pady=8)

        self.file_label = tkinter.Label(self.controls_frame, text="No file", width=40, anchor='w')
        self.file_label.grid(row=0, column=0, columnspan=3, sticky='w')

        self.btn_choose = tkinter.Button(self.controls_frame, text="Choose MIDI file", command=self._choose_file)
        self.btn_choose.grid(row=1, column=0, padx=4)

        self.btn_play = tkinter.Canvas(self.controls_frame, width=30, height=30, bg='SystemButtonFace', highlightthickness=0, relief='raised', borderwidth=2)
        self.btn_play.create_polygon(10, 5, 10, 25, 25, 15, fill='black', outline='black', tags='play_icon')
        self.btn_play.grid(row=1, column=1, padx=4)
        self.btn_play.bind('<Button-1>', lambda e: self._on_play_press(e))
        self.btn_play.bind('<ButtonRelease-1>', lambda e: self._on_play_release(e))

        self.btn_stop = tkinter.Canvas(self.controls_frame, width=30, height=30, bg='SystemButtonFace', highlightthickness=0, relief='raised', borderwidth=2)
        self.btn_stop.create_rectangle(8, 8, 22, 22, fill='black', outline='black', tags='stop_icon')
        self.btn_stop.grid(row=1, column=2, padx=4)
        self.btn_stop.bind('<Button-1>', lambda e: self._on_stop_press(e))
        self.btn_stop.bind('<ButtonRelease-1>', lambda e: self._on_stop_release(e))

        # Apply initial visibility based on settings
        self._update_midi_file_visibility()

        # Register keyboard with dispatcher for name-based calls
        if dispatcher is not None:
            try:
                dispatcher.register('keyboard', self.keyboard)
            except Exception:
                pass

    def resize_keyboard(self, width: int, height: int):
        """Resize the keyboard based on window dimensions."""
        self.keyboard.resize_keyboard(width, height)
        self.keyboard_frame.config(width=width, height=height)

    def _choose_file(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid;*.midi"), ("All files", "*")])
            if path:
                self._selected_file = path
                filename = os.path.basename(path)
                self.file_label.config(text=filename)
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

    def _on_play_press(self, event):
        self.btn_play.config(relief='sunken')

    def _on_play_release(self, event):
        self.btn_play.config(relief='raised')
        self._play_file()

    def _on_stop_press(self, event):
        self.btn_stop.config(relief='sunken')

    def _on_stop_release(self, event):
        self.btn_stop.config(relief='raised')
        self._stop_file()

    def _update_midi_file_visibility(self):
        """Update the visibility of MIDI file controls based on settings"""
        try:
            if self.setting.gui.EnableMidiFile:
                self.controls_frame.grid(row=1, column=0, pady=8)
            else:
                self.controls_frame.grid_remove()
        except Exception as e:
            print(f"Error updating MIDI file visibility: {e}")
            # If setting doesn't exist, show controls by default
            self.controls_frame.grid(row=1, column=0, pady=8)
