import tkinter
import tkinter.ttk
from tkinter import filedialog
import os
from enum import Enum
from typing import Callable, List, Optional
from gui.piano.KeyBoard import KeyBoard
from gui.TrainingDisplay import TrainingDisplay
from config.Setting import Setting
from midi.MidiController import MidiController
try:
    from PIL import Image, ImageTk, ImageOps
except ImportError as e:
    Image = None
    ImageTk = None
    ImageOps = None
    print(f"Warning: Pillow (PIL) is not available. Image display will be disabled. ({e})")


class PlayButtonState(Enum):
    """Enum for play button state."""
    PLAY = 'play'
    PAUSE = 'pause'


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
        self._play_button_state = PlayButtonState.PLAY

        self.btn_stop = tkinter.Canvas(self.controls_frame, width=30, height=30, bg='SystemButtonFace', highlightthickness=0, relief='raised', borderwidth=2)
        self.btn_stop.create_rectangle(8, 8, 22, 22, fill='black', outline='black', tags='stop_icon')
        self.btn_stop.grid(row=1, column=2, padx=4)
        self.btn_stop.bind('<Button-1>', lambda e: self._on_stop_press(e))
        self.btn_stop.bind('<ButtonRelease-1>', lambda e: self._on_stop_release(e))

        # Training start/stop button (always visible on the right of controls)
        self._is_training: bool = False
        self._training_callback: Optional[Callable[[bool], None]] = None
        self.btn_training = tkinter.Button(
            self.controls_frame, text="Start Training", width=14,
            command=self._on_training_clicked)
        self.btn_training.grid(row=1, column=4, padx=(16, 4))

        # TrainingDisplay overlays image_frame during a training session (hidden initially)
        self._training_display = TrainingDisplay(self.image_frame)

        # Saved grid info for MIDI-file widgets so they can be restored after hide
        self._midi_file_widget_grid_info: dict = {}

        # Apply initial visibility based on settings
        self.update_midi_file_visibility()
        self.update_image_frame_visibility()

        # Load initial image if configured
        self.update_image_from_setting()

        # Register keyboard and piano_tab with dispatcher for name-based calls
        if dispatcher is not None:
            try:
                dispatcher.register('keyboard', self.keyboard)
            except Exception:
                pass
            try:
                dispatcher.register('piano_tab', self)
            except Exception:
                pass

    def resize_keyboard(self, width: int, height: int):
        """Resize the keyboard based on window dimensions."""
        self.keyboard.resize_keyboard(width, height)

    def update_image_from_setting(self):
        path = self._get_image_path()
        if not path or not os.path.isfile(path) or Image is None:
            self._image_original = None
            self._image_tk = None
            self._show_canvas_placeholder("No image selected")
            return
        try:
            self._image_original = Image.open(path)
        except Exception:
            self._image_original = None
        self._redraw_image(None)

    def refresh_image(self):
        """Force a redraw of the image (e.g., when tab becomes visible)."""
        try:
            self._redraw_image(None)
        except Exception:
            pass

    def update_midi_file_visibility(self):
        """Show or hide the MIDI file controls based on settings.

        The controls_frame itself is always kept visible because the
        Training start/stop button lives there regardless of this setting.
        """
        try:
            show = self.setting.gui.EnableMidiFile
        except Exception as e:
            print(f"Error reading MIDI file setting: {e}")
            show = True

        midi_widgets = [self.file_label, self.btn_choose, self.btn_play, self.btn_stop]
        if show:
            self._restore_midi_widgets(midi_widgets)
        else:
            self._save_and_hide_midi_widgets(midi_widgets)

        # Always keep the controls_frame in the layout
        self.controls_frame.grid(row=2, column=0, pady=8)

    def _restore_midi_widgets(self, midi_widgets: list) -> None:
        """Restore MIDI file widgets to their saved grid positions."""
        for widget in midi_widgets:
            saved = self._midi_file_widget_grid_info.get(id(widget))
            if saved:
                try:
                    widget.grid(**saved)
                except Exception:
                    pass

    def _save_and_hide_midi_widgets(self, midi_widgets: list) -> None:
        """Save grid positions of MIDI file widgets and remove them from the layout."""
        for widget in midi_widgets:
            try:
                info = widget.grid_info()
                if info:
                    self._midi_file_widget_grid_info[id(widget)] = {
                        k: v for k, v in info.items() if k != 'in'
                    }
                widget.grid_remove()
            except Exception:
                pass

    def update_image_frame_visibility(self):
        """Show or hide the image frame based on settings."""
        try:
            if self.setting.gui.ShowImageFrame:
                self.image_frame.grid(row=0, column=0, sticky='nsew')
                self.frame.grid_rowconfigure(0, weight=1)
                self.frame.grid_rowconfigure(1, weight=0)
            else:
                self.image_frame.grid_remove()
                self.frame.grid_rowconfigure(0, weight=0)
                self.frame.grid_rowconfigure(1, weight=1)
        except Exception as e:
            print(f"Error updating image frame visibility: {e}")
            self.image_frame.grid(row=0, column=0, sticky='nsew')
            self.frame.grid_rowconfigure(0, weight=1)
            self.frame.grid_rowconfigure(1, weight=0)

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
                if self._play_button_state == PlayButtonState.PLAY:
                    # Starting playback
                    self.file_player.set_file(self._selected_file)
                    self.file_player.play()
                    self._update_play_button(PlayButtonState.PAUSE)
                else:
                    # Pausing playback
                    self.file_player.pause()
                    self._update_play_button(PlayButtonState.PLAY)
            except Exception:
                pass

    def _update_play_button(self, state: PlayButtonState):
        """Update play button icon and state."""
        self._play_button_state = state
        self.btn_play.delete('all')
        if state == PlayButtonState.PLAY:
            self._draw_play_icon()
        else:
            self._draw_pause_icon()

    def _draw_play_icon(self):
        """Draw the play (triangle) icon on the play button canvas."""
        self.btn_play.create_polygon(10, 5, 10, 25, 25, 15, fill='black', outline='black', tags='play_icon')

    def _draw_pause_icon(self):
        """Draw the pause (two bars) icon on the play button canvas."""
        self.btn_play.create_rectangle(10, 5, 13, 25, fill='black', outline='black', tags='pause_icon')
        self.btn_play.create_rectangle(17, 5, 20, 25, fill='black', outline='black', tags='pause_icon')

    def _stop_file(self):
        if self.file_player is not None:
            try:
                self.file_player.stop()
                self._update_play_button(PlayButtonState.PLAY)
            except Exception:
                pass

    def _get_image_path(self) -> Optional[str]:
        """Return the configured image path, or None on error."""
        try:
            return self.setting.gui.ImagePath
        except Exception:
            return None

    def _show_canvas_placeholder(self, no_image_msg: str = "No image") -> None:
        """Display placeholder text on the image canvas."""
        try:
            self.image_canvas.delete('all')
            w = max(1, self.image_canvas.winfo_width())
            h = max(1, self.image_canvas.winfo_height())
            if ImageOps is None or ImageTk is None:
                msg = "Install Pillow to show images"
            else:
                msg = no_image_msg
            self.image_canvas.create_text(w // 2, h // 2, text=msg, fill='gray')
        except Exception:
            pass

    def _draw_image_on_canvas(self, w: int, h: int) -> None:
        """Fit and draw self._image_original onto the canvas."""
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

    def _redraw_image(self, event):
        if self._image_original is None or ImageOps is None or ImageTk is None:
            self._show_canvas_placeholder()
            return
        w = max(1, self.image_canvas.winfo_width())
        h = max(1, self.image_canvas.winfo_height())
        self._draw_image_on_canvas(w, h)

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

    # ------------------------------------------------------------------
    # Training mode helpers (called on main thread via UiDispatcher)
    # ------------------------------------------------------------------

    def set_training_callback(self, callback: Callable[[bool], None]) -> None:
        """Set the callback invoked when the training button is clicked.

        The callback receives ``True`` when starting training and ``False``
        when stopping.
        """
        self._training_callback = callback

    def set_training_button_mode(self, is_training: bool) -> None:
        """Switch the training button label between Start and Stop."""
        self._is_training = is_training
        label = "Stop Training" if is_training else "Start Training"
        self.btn_training.config(text=label)

    def update_training_button_visibility(self) -> None:
        """Show or hide the Training button based on settings."""
        try:
            show = self.setting.gui.EnableTraining
        except Exception:
            show = True
        if show:
            self.btn_training.grid(row=1, column=4, padx=(16, 4))
        else:
            self.btn_training.grid_remove()

    def show_training_display(self) -> None:
        """Replace the image canvas with the TrainingDisplay widget."""
        self.image_canvas.pack_forget()
        self._training_display.pack(fill=tkinter.BOTH, expand=True)

    def hide_training_display(self) -> None:
        """Restore the image canvas, hiding the TrainingDisplay."""
        self._training_display.pack_forget()
        self.image_canvas.pack(fill=tkinter.BOTH, expand=True)
        self.refresh_image()

    def highlight_answer_notes(self, key_names: List[str]) -> None:
        """Activate (highlight) a set of keyboard keys to show the answer."""
        for name in key_names:
            try:
                self.keyboard.set_key_state(name, tkinter.ACTIVE)
            except Exception:
                pass

    def clear_answer_highlights(self, key_names: List[str]) -> None:
        """Deactivate previously highlighted answer keys."""
        for name in key_names:
            try:
                self.keyboard.set_key_state(name, tkinter.NORMAL)
            except Exception:
                pass

    def set_midi_playback_enabled(self, enabled: bool) -> None:
        """Enable or visually disable the MIDI file play button."""
        icon_color = 'black' if enabled else '#aaaaaa'
        for tag in ('play_icon', 'pause_icon'):
            try:
                self.btn_play.itemconfigure(tag, fill=icon_color, outline=icon_color)
            except Exception:
                pass
        if enabled:
            self.btn_play.bind('<Button-1>', lambda e: self._on_play_press(e))
            self.btn_play.bind('<ButtonRelease-1>', lambda e: self._on_play_release(e))
        else:
            self.btn_play.unbind('<Button-1>')
            self.btn_play.unbind('<ButtonRelease-1>')

    def _on_training_clicked(self) -> None:
        if self._training_callback is not None:
            self._training_callback(not self._is_training)
