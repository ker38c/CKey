import tkinter
import tkinter.ttk
import os
import pygame
from version import __version__

class AboutTab:
    def __init__(self, root: tkinter.ttk.Notebook):
        self.frame = tkinter.Frame(root)

        # Title with version
        self.title_label = tkinter.Label(
            self.frame,
            text=f"CKey v{__version__}",
            font=("Helvetica", 18, "bold")
        )
        self.title_label.pack(pady=20)

        # Copyright and Version
        self.copyright_label = tkinter.Label(
            self.frame,
            text="Copyright (c) 2025 ker38c",
            font=("Helvetica", 10)
        )
        self.copyright_label.pack(pady=5)

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
            command=self.show_license_popup,
            font=("Helvetica", 10)
        )
        self.license_button.pack(pady=10)

    def show_license_popup(self):
        # Create popup window
        popup = tkinter.Toplevel(self.frame)
        popup.title("License")
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
            license_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'LICENSE')
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