import tkinter
import tkinter.ttk
from tkinter import filedialog
import os
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting
from midi.MidiController import MidiController
try:
    from PIL import Image, ImageTk, ImageOps
except ImportError as e:
    Image = None
    ImageTk = None
    ImageOps = None
    print(f"Warning: Pillow (PIL) is not available. Image display will be disabled. ({e})")

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, midi: MidiController, file_player=None, dispatcher=None):
        self.frame = tkinter.Frame(root)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_rowconfigure(2, weight=0)

        self.image_frame = tkinter.Frame(self.frame)
        self.image_frame.grid(row=0, column=0, sticky='nsew')

        self.image_canvas = tkinter.Canvas(self.image_frame, highlightthickness=0)
        self.image_canvas.pack(fill=tkinter.BOTH, expand=True)
        self.image_canvas.bind('<Configure>', self._redraw_image)

        self._image_original = None
        self._image_tk = None

        self.keyboard_frame = tkinter.Frame(self.frame)
        self.keyboard_frame.grid(row=1, column=0, sticky='ew')

        self.keyboard = KeyBoard(master=self.keyboard_frame, setting=setting, midi=midi)
        self.keyboard.pack(fill=tkinter.BOTH, expand=True)

        # File playback controls placed under the keyboard
        self._selected_file = None
        self.file_player = file_player
        self.midi = midi
        self.setting = setting

        self.controls_frame = tkinter.Frame(self.frame)
        self.controls_frame.grid(row=2, column=0, pady=8)

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
        self.update_midi_file_visibility()

        # Load initial image if configured
        self.update_image_from_setting()

        # Register keyboard with dispatcher for name-based calls
        if dispatcher is not None:
            try:
                dispatcher.register('keyboard', self.keyboard)
            except Exception:
                pass

    def resize_keyboard(self, width: int, height: int):
        """Resize the keyboard based on window dimensions."""
        self.keyboard.resize_keyboard(width, height)

    def update_image_from_setting(self):
        path = None
        try:
            path = self.setting.gui.ImagePath
        except Exception:
            path = None

        if not path or not os.path.isfile(path) or Image is None:
            self._image_original = None
            self._image_tk = None
            try:
                self.image_canvas.delete('all')
                w = max(1, self.image_canvas.winfo_width())
                h = max(1, self.image_canvas.winfo_height())
                msg = "Install Pillow to show images" if Image is None else "No image selected"
                self.image_canvas.create_text(w // 2, h // 2, text=msg, fill='gray')
            except Exception:
                pass
            return

        try:
            self._image_original = Image.open(path)
        except Exception:
            self._image_original = None
        self._redraw_image(None)

    def _redraw_image(self, event):
        if self._image_original is None or ImageOps is None or ImageTk is None:
            try:
                self.image_canvas.delete('all')
                w = max(1, self.image_canvas.winfo_width())
                h = max(1, self.image_canvas.winfo_height())
                msg = "Install Pillow to show images" if (ImageOps is None or ImageTk is None) else "No image"
                self.image_canvas.create_text(w // 2, h // 2, text=msg, fill='gray')
            except Exception:
                pass
            return

        w = max(1, self.image_canvas.winfo_width())
        h = max(1, self.image_canvas.winfo_height())
        # Provide a small margin so the image doesn't touch edges
        pad = 8
        target_w = max(1, w - pad * 2)
        target_h = max(1, h - pad * 2)
        try:
            fitted = ImageOps.contain(self._image_original, (target_w, target_h))
            self._image_tk = ImageTk.PhotoImage(fitted)
            self.image_canvas.delete('all')
            self.image_canvas.create_image(w // 2, h // 2, image=self._image_tk, anchor='center')
        except Exception:
            try:
                self.image_canvas.delete('all')
            except Exception:
                pass

    def refresh_image(self):
        """Force a redraw of the image (e.g., when tab becomes visible)."""
        try:
            self._redraw_image(None)
        except Exception:
            pass

    def update_midi_file_visibility(self):
        """Update the visibility of MIDI file controls based on settings"""
        try:
            if self.setting.gui.EnableMidiFile:
                self.controls_frame.grid(row=2, column=0, pady=8)
            else:
                self.controls_frame.grid_remove()
        except Exception as e:
            print(f"Error updating MIDI file visibility: {e}")
            # If setting doesn't exist, show controls by default
            self.controls_frame.grid(row=2, column=0, pady=8)

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
