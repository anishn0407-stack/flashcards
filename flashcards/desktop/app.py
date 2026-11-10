import tkinter as tk
from tkinter import ttk

from core.deck import Deck
from core.generator import CardGenerator
from core.scheduler import Scheduler

DECK_NAME = "My Deck"

BG = "#1e1e2e"
PANEL = "#313244"
PANEL_ANSWER = "#3b4a5a"
TEXT = "#cdd6f4"
MUTED = "#a6adc8"
BLUE = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
DARK = "#11111b"
FONT = "Segoe UI"

SAMPLE_NOTES = (
    "A stack is a linear data structure that follows the LIFO principle. "
    "A queue is a linear data structure that follows the FIFO principle. "
    "A linked list is a collection of nodes connected by pointers. "
    "Recursion is a technique where a function calls itself. "
    "Inheritance is a feature of OOP that lets a class reuse the properties of another class. "
    "Encapsulation is the practice of bundling data and methods inside one class. "
    "A primary key is a column that uniquely identifies each row in a table. "
    "Binary search runs in logarithmic time on sorted data. "
    "SQLite stores the entire database inside a single file."
)


class HoverButton(tk.Button):
    def __init__(self, parent, hover_color, **kwargs):
        super().__init__(parent, **kwargs)
        self.normal_color = kwargs.get("bg", BG)
        self.hover_color = hover_color
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_color)

    def on_leave(self, event):
        self.config(bg=self.normal_color)


def make_button(parent, text, bg, hover, command, width=14):
    return HoverButton(
        parent,
        hover_color=hover,
        text=text,
        command=command,
        bg=bg,
        fg=DARK,
        activebackground=hover,
        activeforeground=DARK,
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        font=(FONT, 11, "bold"),
        width=width,
        pady=8,
    )


class NotesFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        tk.Label(
            self, text="Paste your notes", font=(FONT, 16, "bold"), bg=BG, fg=TEXT
        ).pack(anchor="w", padx=20, pady=(10, 0))
        tk.Label(
            self,
            text='Sentences like "X is Y" become Q&A cards. Others become fill-in-the-blanks.',
            font=(FONT, 9),
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 8))

        self.text = tk.Text(
            self,
            height=12,
            width=62,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief=tk.FLAT,
            font=(FONT, 11),
            padx=10,
            pady=10,
            wrap=tk.WORD,
        )
        self.text.pack(padx=20)

        self.status_label = tk.Label(self, text="", font=(FONT, 10), bg=BG, fg=GREEN)
        self.status_label.pack(pady=8)

        button_row = tk.Frame(self, bg=BG)
        button_row.pack(pady=4)
        make_button(button_row, "Generate Cards", BLUE, "#b4d0ff", self.on_generate).pack(
            side=tk.LEFT, padx=6
        )
        make_button(button_row, "Start Studying", GREEN, "#c6f0c2", self.app.show_study).pack(
            side=tk.LEFT, padx=6
        )

        tk.Button(
            self,
            text="Load sample notes",
            command=self.on_sample,
            bg=BG,
            fg=MUTED,
            activebackground=BG,
            activeforeground=TEXT,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            font=(FONT, 9, "underline"),
        ).pack(pady=6)

    def set_status(self, message, color):
        self.status_label.config(text=message, fg=color)

    def on_sample(self):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", SAMPLE_NOTES)
        self.set_status("Sample notes loaded. Click Generate Cards.", MUTED)

    def on_generate(self):
        notes = self.text.get("1.0", tk.END).strip()
        if not notes:
            self.set_status("Paste some notes first.", RED)
            return
        count = self.app.generate_cards(notes)
        self.set_status(f"{count} cards created. Ready to study!", GREEN)
        self.text.delete("1.0", tk.END)


class StudyFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.queue = []
        self.current = None
        self.flipped = False
        self.total = 0
        self.done = 0

        self.progress = ttk.Progressbar(
            self, style="Flash.Horizontal.TProgressbar", length=560, mode="determinate"
        )
        self.progress.pack(pady=(10, 2))
        self.progress_label = tk.Label(self, text="", font=(FONT, 9), bg=BG, fg=MUTED)
        self.progress_label.pack()

        self.card_frame = tk.Frame(self, bg=PANEL, width=560, height=250)
        self.card_frame.pack(pady=12)
        self.card_frame.pack_propagate(False)

        self.tag_label = tk.Label(
            self.card_frame, text="QUESTION", font=(FONT, 9, "bold"), bg=PANEL, fg=BLUE
        )
        self.tag_label.pack(anchor="w", padx=16, pady=(12, 0))

        self.question_label = tk.Label(
            self.card_frame, text="", font=(FONT, 15), bg=PANEL, fg=TEXT, wraplength=520
        )
        self.question_label.pack(expand=True, padx=16)

        self.answer_label = tk.Label(
            self.card_frame, text="", font=(FONT, 15, "bold"), bg=PANEL, fg=GREEN, wraplength=520
        )
        self.answer_label.pack(expand=True, padx=16)

        self.box_label = tk.Label(
            self.card_frame, text="", font=(FONT, 9), bg=PANEL, fg=MUTED
        )
        self.box_label.pack(anchor="e", padx=16, pady=(0, 10))

        self.actions = tk.Frame(self, bg=BG, height=50)
        self.actions.pack()

        self.flip_row = tk.Frame(self.actions, bg=BG)
        make_button(self.flip_row, "Show Answer", BLUE, "#b4d0ff", self.on_flip, width=20).pack()

        self.rate_row = tk.Frame(self.actions, bg=BG)
        make_button(self.rate_row, "Hard", RED, "#f7a8bd", self.on_hard).pack(
            side=tk.LEFT, padx=8
        )
        make_button(self.rate_row, "Easy", GREEN, "#c6f0c2", self.on_easy).pack(
            side=tk.LEFT, padx=8
        )

        tk.Button(
            self,
            text="Back to notes",
            command=self.app.show_notes,
            bg=BG,
            fg=MUTED,
            activebackground=BG,
            activeforeground=TEXT,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            font=(FONT, 9, "underline"),
        ).pack(pady=16)

    def set_card_color(self, color):
        widgets = (
            self.card_frame,
            self.tag_label,
            self.question_label,
            self.answer_label,
            self.box_label,
        )
        for widget in widgets:
            widget.config(bg=color)

    def show_flip_row(self):
        self.rate_row.pack_forget()
        self.flip_row.pack()

    def show_rate_row(self):
        self.flip_row.pack_forget()
        self.rate_row.pack()

    def hide_rows(self):
        self.flip_row.pack_forget()
        self.rate_row.pack_forget()

    def update_progress(self):
        percent = 100 * self.done / self.total if self.total else 0
        self.progress["value"] = percent
        self.progress_label.config(text=f"{self.done} / {self.total} reviewed")

    def refresh(self):
        self.queue = self.app.deck.due_cards()
        self.total = len(self.queue)
        self.done = 0
        self.next_card()

    def show_finished(self):
        self.current = None
        self.set_card_color(PANEL)
        self.tag_label.config(text="DONE", fg=GREEN)
        self.question_label.config(text="All caught up!", fg=TEXT, font=(FONT, 15))
        self.answer_label.config(
            text="No more cards due today.\nAdd more notes or come back tomorrow."
        )
        self.box_label.config(text="")
        self.hide_rows()

    def next_card(self):
        self.flipped = False
        self.update_progress()

        if not self.queue:
            self.show_finished()
            return

        self.current = self.queue.pop(0)
        self.set_card_color(PANEL)
        self.tag_label.config(text="QUESTION", fg=BLUE)
        self.question_label.config(text=self.current.question, fg=TEXT, font=(FONT, 15))
        self.answer_label.config(text="")
        self.box_label.config(text=f"Box {self.current.box} of 3")
        self.show_flip_row()

    def on_flip(self):
        if self.current is None or self.flipped:
            return
        self.flipped = True
        self.set_card_color(PANEL_ANSWER)
        self.tag_label.config(text="ANSWER", fg=GREEN)
        self.question_label.config(fg=MUTED, font=(FONT, 10))
        self.answer_label.config(text=self.current.answer)
        self.show_rate_row()

    def rate(self, easy):
        if self.current is None or not self.flipped:
            return
        self.app.scheduler.review(self.current, easy)
        self.app.deck.update_card(self.current)
        self.done += 1
        self.next_card()

    def on_easy(self):
        self.rate(True)

    def on_hard(self):
        self.rate(False)


class App:
    def __init__(self, root):
        self.root = root
        self.deck = Deck(DECK_NAME)
        self.generator = CardGenerator()
        self.scheduler = Scheduler()

        self.setup_style()
        self.build_header()

        self.container = tk.Frame(root, bg=BG)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.notes_frame = NotesFrame(self.container, self)
        self.study_frame = StudyFrame(self.container, self)

        self.show_notes()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Flash.Horizontal.TProgressbar",
            troughcolor=PANEL,
            background=GREEN,
            bordercolor=BG,
            lightcolor=GREEN,
            darkcolor=GREEN,
        )

    def build_header(self):
        header = tk.Frame(self.root, bg=DARK)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="Smart Flashcards", font=(FONT, 18, "bold"), bg=DARK, fg=BLUE
        ).pack(side=tk.LEFT, padx=20, pady=12)

    def show_notes(self):
        self.study_frame.pack_forget()
        self.notes_frame.pack(fill=tk.BOTH, expand=True)

    def show_study(self):
        self.notes_frame.pack_forget()
        self.study_frame.refresh()
        self.study_frame.pack(fill=tk.BOTH, expand=True)

    def generate_cards(self, notes):
        cards = self.generator.generate(notes)
        for card in cards:
            self.deck.add_card(card)
        return len(cards)


def main():
    root = tk.Tk()
    root.title("Smart Flashcards")
    root.geometry("640x620")
    root.resizable(False, False)
    root.configure(bg=BG)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()