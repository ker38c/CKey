import tkinter
import tkinter.ttk
from typing import List


class TrainingDisplay(tkinter.Frame):
    """Widget that shows the current training question, score, and feedback.

    Displayed inside PianoTab's image_frame during a training session.
    All public methods are called on the main thread via UiDispatcher.
    """

    _BG_COLOR = '#1e1e2e'

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(bg=self._BG_COLOR)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)

        # --- Question label (large, centred) ---
        self._question_var = tkinter.StringVar(value="")
        self._question_label = tkinter.Label(
            self,
            textvariable=self._question_var,
            font=("Helvetica", 48, "bold"),
            fg='white',
            bg=self._BG_COLOR,
        )
        self._question_label.grid(row=0, column=0, sticky='nsew', pady=(20, 4))

        # --- Score label ---
        self._score_var = tkinter.StringVar(value="")
        self._score_label = tkinter.Label(
            self,
            textvariable=self._score_var,
            font=("Helvetica", 18),
            fg='#aaaaaa',
            bg=self._BG_COLOR,
        )
        self._score_label.grid(row=1, column=0, pady=4)

        # --- Listen Again button (hidden by default; Hearing mode only) ---
        self._listen_again_btn = tkinter.ttk.Button(
            self,
            text="\u266a Listen Again",
        )
        self._listen_again_btn.grid(row=2, column=0, pady=4)
        self._listen_again_btn.grid_remove()

        # --- Feedback label ---
        self._feedback_var = tkinter.StringVar(value="")
        self._feedback_label = tkinter.Label(
            self,
            textvariable=self._feedback_var,
            font=("Helvetica", 24, "bold"),
            fg='white',
            bg=self._BG_COLOR,
        )
        self._feedback_label.grid(row=3, column=0, sticky='nsew', pady=(4, 20))

    # ------------------------------------------------------------------
    # Public methods (called via UiDispatcher from background threads)
    # ------------------------------------------------------------------

    def show_question(self, display_name: str) -> None:
        """Display the chord name for the new question."""
        self._question_var.set(display_name)
        self._feedback_var.set("")
        self._feedback_label.configure(fg='white')

    def show_score(self, correct: int, total: int) -> None:
        """Update the score display."""
        if total == 0:
            self._score_var.set("0 / 0")
        else:
            pct = int(correct / total * 100)
            self._score_var.set(f"{correct} / {total}  ({pct}%)")

    def show_feedback_correct(self) -> None:
        """Display green 'Correct!' feedback."""
        self._feedback_var.set("Correct!")
        self._feedback_label.configure(fg='#00cc66')

    def show_feedback_wrong(self, note_names: List[str]) -> None:
        """Display red 'Wrong!' feedback with the correct answer."""
        answer_str = ",  ".join(note_names)
        self._feedback_var.set(f"Wrong!  Answer:  {answer_str}")
        self._feedback_label.configure(fg='#ff4444')

    def clear_feedback(self) -> None:
        """Clear the feedback message."""
        self._feedback_var.set("")
        self._feedback_label.configure(fg='white')

    def show_listen_prompt(self) -> None:
        """Display the listen prompt (Hearing mode: hides the chord name)."""
        self._question_var.set("\u266a Listen...")
        self._feedback_var.set("")
        self._feedback_label.configure(fg='white')

    def set_listen_again_visible(self, visible: bool) -> None:
        """Show or hide the Listen Again button."""
        if visible:
            self._listen_again_btn.grid()
        else:
            self._listen_again_btn.grid_remove()

    def set_listen_again_enabled(self, enabled: bool) -> None:
        """Enable or disable the Listen Again button."""
        self._listen_again_btn.configure(state='normal' if enabled else 'disabled')

    def set_listen_again_callback(self, callback) -> None:
        """Register the callback invoked when Listen Again is clicked."""
        self._listen_again_btn.configure(command=callback)

    def reset(self) -> None:
        """Clear all displayed text (call when a training session ends)."""
        self._question_var.set("")
        self._score_var.set("")
        self._feedback_var.set("")
        self._feedback_label.configure(fg='white')
