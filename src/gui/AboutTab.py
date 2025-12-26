import tkinter
import tkinter.ttk
import os
import pygame
import mido
try:
    from PIL import __version__ as pillow_version
except Exception:
    pillow_version = "not installed"
from version import __version__

class AboutTab:
    def __init__(self, root: tkinter.ttk.Notebook):
        self.frame = tkinter.Frame(root)

        # CKey version
        self.title_label = tkinter.Label(
            self.frame,
            text=f"CKey v{__version__}",
            font=("Helvetica", 18, "bold")
        )
        self.title_label.pack(pady=20)

        # CKey URL
        self.url_label = tkinter.Label(
            self.frame,
            text="https://github.com/ker38c/CKey",
            font=("Helvetica", 10)
        )
        self.url_label.pack(pady=5)

        # License Button
        self.license_button = tkinter.Button(
            self.frame,
            text="View License",
            command=lambda: self._show_license_popup("CKey license", "LICENSE"),
            font=("Helvetica", 10)
        )
        self.license_button.pack(pady=10)

        # Used Libraries
        self.libs_label = tkinter.Label(
            self.frame,
            text="CKey uses libraries below:",
            font=("Helvetica", 12, "bold")
        )
        self.libs_label.pack(pady=(10, 5))

        # pygame
        self.pygame_label = tkinter.Label(
            self.frame,
            text=f"Pygame v{pygame.__version__}",
            font=("Helvetica", 10)
        )
        self.pygame_label.pack(pady=2)

        # pygame URL
        self.pygame_url_label = tkinter.Label(
            self.frame,
            text="https://www.pygame.org/",
            font=("Helvetica", 10)
        )
        self.pygame_url_label.pack(pady=2)

        self.pygame_license_button = tkinter.Button(
            self.frame,
            text="View License",
            command=lambda: self._show_license_popup("Pygame license", "docs/license/pygame/LGPL.txt"),
            font=("Helvetica", 10)
        )
        self.pygame_license_button.pack(pady=5)

        # mido
        self.mido_label = tkinter.Label(
            self.frame,
            text=f"Mido v{mido.version.__version__}",
            font=("Helvetica", 10)
        )
        self.mido_label.pack(pady=2)

        # mido URL
        self.mido_url_label = tkinter.Label(
            self.frame,
            text="https://mido.readthedocs.io/",
            font=("Helvetica", 10)
        )
        self.mido_url_label.pack(pady=2)

        self.mido_license_button = tkinter.Button(
            self.frame,
            text="View License",
            command=lambda: self._show_license_popup("Mido license", "docs/license/mido/LICENSE"),
            font=("Helvetica", 10)
        )
        self.mido_license_button.pack(pady=5)

        # pillow
        self.pillow_label = tkinter.Label(
            self.frame,
            text=f"Pillow v{pillow_version}",
            font=("Helvetica", 10)
        )
        self.pillow_label.pack(pady=2)

        # pillow URL
        self.pillow_url_label = tkinter.Label(
            self.frame,
            text="https://python-pillow.org/",
            font=("Helvetica", 10)
        )
        self.pillow_url_label.pack(pady=2)

        self.pillow_license_button = tkinter.Button(
            self.frame,
            text="View License",
            command=lambda: self._show_license_popup("Pillow license", "docs/license/pillow/LICENSE"),
            font=("Helvetica", 10)
        )
        self.pillow_license_button.pack(pady=5)


    def _get_basedir(self):
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def _show_license_popup(self, title: str, license_path: str):
        # Create popup window
        popup = tkinter.Toplevel(self.frame)
        popup.title(title)
        popup.geometry("600x400")

        # Make the popup modal
        popup.grab_set()

        # Create frame for license text
        license_frame = tkinter.Frame(popup)
        license_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create text widget
        license_text = tkinter.Text(
            license_frame,
            height=15,
            width=70,
            wrap=tkinter.WORD,
            font=("Helvetica", 10)
        )
        license_text.pack(side=tkinter.LEFT, fill="both", expand=True)

        # Add scrollbar
        scrollbar = tkinter.Scrollbar(license_frame)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        license_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=license_text.yview)

        # Read and display license text
        try:
            license_path = os.path.join(self._get_basedir(), license_path)
            with open(license_path, 'r', encoding='utf-8') as f:
                license_content = f.read()
            license_text.insert(tkinter.END, license_content)
        except Exception as e:
            license_text.insert(tkinter.END, "Error: Could not load LICENSE file.\n" + str(e))
        license_text.config(state=tkinter.DISABLED)

        # Add close button
        close_button = tkinter.Button(
            popup,
            text="Close",
            command=popup.destroy,
            font=("Helvetica", 10)
        )
        close_button.pack(pady=10)