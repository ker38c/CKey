import tkinter
from tkinter import Canvas
from config.Setting import Setting


class CatPawPedalButton(tkinter.Frame):
    """Sustain pedal button shaped like a cat paw print"""
    def __init__(self, master=None, setting: Setting=None, **kargs):
        super().__init__(master=master, **kargs)
        self.setting = setting
        self.is_pressed = False

        # Draw paw print with canvas
        self.canvas = Canvas(self)
        self.canvas.config(highlightthickness=1)
        self.canvas.config(highlightbackground="black")
        self.canvas.config(bg="white")
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Configure>', self.on_configure)

        self._draw_paw()

    def _draw_paw(self):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            width = 100
            height = 100

        # Determine the color of paw print
        color = self.setting.gui.KeyPushedColor if self.is_pressed else "white"
        outline_color = "black"

        # Large paw pad (Center)
        pad_size = min(width, height) / 3
        pad_rad = pad_size / 2
        center_x = width / 2
        center_y = height / 2

        self.canvas.create_oval(
            center_x - pad_rad,
            center_y - pad_rad,
            center_x + pad_rad,
            center_y + pad_rad,
            fill=color,
            outline=None,
            width=0
        )
        self.canvas.create_oval(
            center_x + pad_size,
            center_y + pad_size,
            center_x,
            center_y,
            fill=color,
            outline=None,
            width=0
        )
        self.canvas.create_oval(
            center_x,
            center_y + pad_size,
            center_x - pad_size,
            center_y,
            fill=color,
            outline=None,
            width=0
        )


        # Small paw pad (Left)
        self.canvas.create_oval(
            pad_rad,
            pad_size,
            0,
            center_y + pad_rad,
            fill=color,
            outline=outline_color,
            width=0
        )

        # Small paw pad (Left Top)
        self.canvas.create_oval(
            center_x - pad_rad / 2,
            0,
            pad_rad * 1.5,
            pad_size,
            fill=color,
            outline=outline_color,
            width=0
        )

        # Small paw pad (Right Top)
        self.canvas.create_oval(
            center_x + 1.5 * pad_rad,
            0,
            center_x + pad_rad / 2,
            pad_size,
            fill=color,
            outline=outline_color,
            width=0
        )

        # Small paw pad (Right)
        self.canvas.create_oval(
            center_x + pad_size * 1.5,
            pad_size,
            center_x + pad_size,
            center_y + pad_rad,
            fill=color,
            outline=outline_color,
            width=0
        )

    def on_press(self, event):
        self.is_pressed = True
        self._draw_paw()

    def on_release(self, event):
        self.is_pressed = False
        self._draw_paw()

    def on_configure(self, event):
        """Redraw paw print when resizing button"""
        self._draw_paw()

    def config(self, **kwargs):
        """Override config to handle state changes"""
        if 'state' in kwargs:
            state = kwargs.pop('state')
            self.is_pressed = (state == tkinter.ACTIVE)
            self._draw_paw()
        super().config(**kwargs)
