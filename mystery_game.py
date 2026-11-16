
import tkinter as tk
from tkinter import messagebox
import threading
import json
import urllib.request
import urllib.error
import os
import re

# ==================== COLORS ====================

BG = "#100D24"
PANEL = "#1D1838"
CARD = "#292148"
PURPLE = "#A78BFA"
PINK = "#F0ABFC"
WHITE = "#F8F5FF"
MUTED = "#C4B9E8"
GREEN = "#86EFAC"
RED = "#FDA4AF"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

CUSTOM_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "custom_mysteries.json"
)

# ==================== MYSTERIES ====================

LEVELS = [
    {
        "title": "The Missing Moon Crystal",
        "location": "The Enchanted Library",
        "difficulty": "EASY",
        "story": (
            "At midnight, the Moon Crystal disappears.\n\n"
            "Mira says she was reading a book.\n"
            "Leo says he was sleeping beside the window.\n"
            "Nora says she was watering the plants.\n\n"
            "The detective notices that the plants are completely dry."
        ),
        "puzzle": "Who is most suspicious, and what is the clue?",
        "answers": ["nora"],
        "hints": [
            "One person's statement does not match the evidence.",
            "Think about the person who said they watered the plants."
        ],
        "solution": (
            "Nora is suspicious because she said she watered the plants, "
            "but they are dry. This does not prove she stole the crystal."
        )
    },
    {
        "title": "The Locked Room",
        "location": "Blackthorn Mansion",
        "difficulty": "EASY",
        "story": (
            "A priceless ring disappears from a locked study.\n\n"
            "The door is locked, but the window is open. The butler heard "
            "a bird, and the gardener saw feathers near the window."
        ),
        "puzzle": "What is one possible explanation for the missing ring?",
        "answers": ["a bird took it", "bird", "a bird carried it away"],
        "hints": [
            "The door is locked, but another opening exists.",
            "Think about the feathers and the open window."
        ],
        "solution": (
            "A bird may have carried the ring out through the open window. "
            "More evidence would be needed to prove this."
        )
    },
    {
        "title": "The Secret Number",
        "location": "The Clockwork Tower",
        "difficulty": "EASY",
        "story": "A mechanical door needs a number code.\n\n2, 4, 6, 8, __",
        "puzzle": "What number comes next?",
        "answers": ["10", "ten"],
        "hints": [
            "Look at how much each number increases.",
            "Each number increases by two."
        ],
        "solution": "The answer is 10 because each number increases by 2."
    },
    {
        "title": "The Vanishing Footprints",
        "location": "Whispering Woods",
        "difficulty": "MEDIUM",
        "story": (
            "A messenger disappears in a snowy forest. Footprints lead to "
            "a large tree and then stop.\n\n"
            "A low branch hangs over the path, and a rope is tied to it."
        ),
        "puzzle": "What should the detective investigate next?",
        "answers": ["tree", "branch", "rope", "tree and rope"],
        "hints": [
            "Do not only look at the ground.",
            "Inspect the branch and the rope."
        ],
        "solution": (
            "The detective should inspect the tree, branch and rope. "
            "The messenger may have climbed away from the path."
        )
    },
    {
        "title": "The Midnight Alibi",
        "location": "The Royal Museum",
        "difficulty": "MEDIUM",
        "story": (
            "A painting disappears between 9:00 and 9:30 PM.\n\n"
            "Arin has a cafe receipt from 9:10 PM.\n"
            "A gardener saw Bella in the garden at 9:20 PM.\n"
            "Cyrus says he was in the office, but nobody confirms it."
        ),
        "puzzle": "Whose alibi needs the most verification?",
        "answers": ["cyrus", "cyrus's alibi", "cyrus alibi"],
        "hints": [
            "Two people have evidence about where they were.",
            "One person's whereabouts have not been confirmed."
        ],
        "solution": (
            "Cyrus's alibi needs more verification because nobody confirms "
            "where he was. This does not prove he took the painting."
        )
    },
    {
        "title": "The Potion Puzzle",
        "location": "The Witch's Workshop",
        "difficulty": "MEDIUM",
        "story": (
            "Three bottles are on a table.\n\n"
            "Blue contains water.\n"
            "Red contains fire.\n"
            "Green contains a sleeping spell."
        ),
        "puzzle": "Which bottle contains ordinary water?",
        "answers": ["blue", "blue bottle", "the blue bottle", "water"],
        "hints": [
            "Look at the information given for each colour.",
            "Which bottle is described as containing water?"
        ],
        "solution": "The blue bottle contains water."
    },
    {
        "title": "The Silent Witness",
        "location": "The Forgotten Theatre",
        "difficulty": "HARD",
        "story": (
            "A golden mask is stolen during a theatre performance.\n\n"
            "The lights go dark at 8:15 PM. A visitor sees someone cross "
            "the stage but cannot see their face. The theatre log shows "
            "that a side door opened at 8:16 PM."
        ),
        "puzzle": "Which clue should the detective investigate first?",
        "answers": ["side door", "door", "door log", "the side door"],
        "hints": [
            "Look at what happened just after the blackout.",
            "The log records a door opening at 8:16 PM."
        ],
        "solution": (
            "Investigate the side door and check who opened it. "
            "The timing is suspicious but does not prove who stole the mask."
        )
    },
    {
        "title": "The Three Keys",
        "location": "The Crystal Dungeon",
        "difficulty": "HARD",
        "story": (
            "Three keys are labelled SUN, MOON and STAR.\n\n"
            "A message says the correct symbol appears after sunset. "
            "The SUN key has a golden sun."
        ),
        "puzzle": "Which key is the best choice from these clues?",
        "answers": ["moon", "moon key", "the moon key"],
        "hints": [
            "Think about what appears in the night sky.",
            "Which symbol is associated with the night?"
        ],
        "solution": (
            "The Moon key is the best choice because the clue points "
            "toward something associated with the night."
        )
    },
    {
        "title": "The Frozen Hour",
        "location": "The Ice Palace",
        "difficulty": "HARD",
        "story": (
            "The palace clock is frozen at 6:30 PM. A guard claims the "
            "treasure disappeared at 7:00 PM because the clock told him so.\n\n"
            "Another guard remembers hearing the palace bell ring twice."
        ),
        "puzzle": "Can a frozen clock prove the exact time of the theft?",
        "answers": ["no", "no it cannot"],
        "hints": [
            "A stopped clock cannot track changing time accurately.",
            "Find another reliable source for the time."
        ],
        "solution": (
            "No. A frozen clock cannot prove the exact time. "
            "The detective should check a working clock or other evidence."
        )
    },
    {
        "title": "The Final Mystery",
        "location": "The Hidden Kingdom",
        "difficulty": "FINAL",
        "story": (
            "Three chests are labelled RUBY, SAPPHIRE and EMERALD. "
            "One contains the crown.\n\n"
            "RUBY says: The crown is not in the Ruby chest.\n"
            "SAPPHIRE says: The crown is in the Ruby chest.\n"
            "EMERALD says: The crown is not in the Sapphire chest.\n\n"
            "Exactly ONE statement is true."
        ),
        "puzzle": "Which chest contains the crown?",
        "answers": ["sapphire", "sapphire chest", "the sapphire chest"],
        "hints": [
            "Test each chest and count how many statements are true.",
            "Only one statement can be true."
        ],
        "solution": (
            "The Sapphire chest. Ruby's statement is true, while "
            "Sapphire's and Emerald's statements are false."
        )
    }
]


# ==================== MAIN GAME ====================

class DreamQuestGame:

    def __init__(self, root):
        self.root = root
        self.root.title("DreamQuest AI - The 10 Mysteries")
        self.root.configure(bg=BG)
        self.root.geometry("1150x760")
        self.root.minsize(850, 600)

        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

        self.active_levels = LEVELS
        self.level_index = 0
        self.completed = set()
        self.hint_index = 0
        self.chat_busy = False
        self.custom_levels = self.load_custom_levels()

        self.build_welcome()

    # ---------------- UI HELPERS ----------------

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def make_label(self, parent, text, size=12, color=WHITE,
                   bold=False, bg=None):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            fg=color,
            bg=bg or parent.cget("bg"),
            justify="left",
            wraplength=650
        )

    def make_button(self, parent, text, command,
                    bg=PURPLE, fg=BG):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=PINK,
            activeforeground=BG,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=9
        )

    # ---------------- WELCOME SCREEN ----------------

    def build_welcome(self):
        self.clear_window()

        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        top = tk.Frame(outer, bg="#0B0920", height=48)
        top.pack(fill="x")
        top.pack_propagate(False)

        self.make_label(
            top, "✦ DREAMQUEST AI", 15, PINK, True, "#0B0920"
        ).pack(side="left", padx=24, pady=8)

        self.make_label(
            top, "YOUR ADVENTURE • YOUR MYSTERIES",
            10, MUTED, False, "#0B0920"
        ).pack(side="right", padx=24)

        content = tk.Frame(outer, bg=BG)
        content.pack(fill="both", expand=True, padx=25, pady=20)

        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=20)

        self.make_label(
            left, "☾  ✦  ♛  ✦  ☽", 24, PINK, True, BG
        ).pack(pady=(35, 8))

        self.make_label(
            left, "DREAMQUEST AI", 30, PINK, True, BG
        ).pack()

        self.make_label(
            left, "THE 10 MYSTERIES", 17, PURPLE, True, BG
        ).pack(pady=(4, 10))

        self.make_label(
            left,
            "A dreamy fantasy adventure full of puzzles,\n"
            "secrets, and magical discoveries.",
            13, WHITE, False, BG
        ).pack(pady=(0, 24))

        self.make_button(
            left, "▶  START ADVENTURE",
            lambda: self.start_game(LEVELS)
        ).pack(fill="x", padx=40, pady=7, ipady=4)

        self.make_button(
            left, "✎  CUSTOMIZE MYSTERIES",
            self.open_customizer, "#4B287D", WHITE
        ).pack(fill="x", padx=40, pady=7, ipady=4)

        self.make_button(
            left, "▣  HOW TO PLAY",
            self.show_instructions, CARD, WHITE
        ).pack(fill="x", padx=40, pady=7, ipady=4)

        self.make_label(
            left, "✦  Puzzles  •  Hints  •  Solutions  •  AI Chat  ✦",
            10, MUTED, False, BG
        ).pack(pady=20)

        right = tk.Frame(
            content, bg=PANEL,
            highlightbackground="#8154C7",
            highlightthickness=1
        )
        right.pack(side="right", fill="y", padx=12, pady=25)

        self.make_label(
            right, "✧ CREATE YOUR OWN QUIZ", 16, PINK, True, PANEL
        ).pack(anchor="w", padx=22, pady=(28, 10))

        self.make_label(
            right, "Turn your ideas into a mystery!",
            11, MUTED, False, PANEL
        ).pack(anchor="w", padx=22, pady=(0, 15))

        for number, title, description in [
            ("1", "Add your question", "Write a question or riddle."),
            ("2", "Add the answer", "Enter its correct answer."),
            ("3", "Ask the AI", "Chat about your mystery.")
        ]:
            row = tk.Frame(right, bg=PANEL)
            row.pack(fill="x", padx=18, pady=12)

            self.make_label(
                row, number, 15, PURPLE, True, PANEL
            ).pack(side="left", padx=(0, 12))

            details = tk.Frame(row, bg=PANEL)
            details.pack(side="left", fill="x")

            self.make_label(
                details, title, 11, WHITE, True, PANEL
            ).pack(anchor="w")

            self.make_label(
                details, description, 9, MUTED, False, PANEL
            ).pack(anchor="w", pady=3)

        self.make_button(
            right, "✦ CREATE MY OWN QUIZ",
            self.open_customizer, "#8B35D1", WHITE
        ).pack(fill="x", padx=20, pady=(18, 25))

    def show_instructions(self):
        messagebox.showinfo(
            "How to Play",
            "1. Click Start Adventure.\n\n"
            "2. Read the mystery and enter your answer.\n\n"
            "3. Click Get Hint when you need help.\n\n"
            "4. Click Show Solution to reveal the explanation.\n\n"
            "5. Ask the AI Companion about the mystery.\n\n"
            "6. Use Customize Mysteries to create your own quiz."
        )

    # ---------------- CUSTOM MYSTERIES ----------------

    def load_custom_levels(self):
        try:
            with open(CUSTOM_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save_custom_levels(self):
        with open(CUSTOM_FILE, "w", encoding="utf-8") as file:
            json.dump(
                self.custom_levels, file,
                ensure_ascii=False, indent=2
            )

    def open_customizer(self):
        self.clear_window()

        page = tk.Frame(self.root, bg=BG)
        page.pack(fill="both", expand=True, padx=28, pady=18)

        self.make_label(
            page, "✧ CUSTOMIZE YOUR MYSTERIES ✧",
            23, PINK, True, BG
        ).pack(pady=(5, 8))

        self.make_label(
            page, "Create and save your own quiz questions.",
            11, MUTED, False, BG
        ).pack(pady=(0, 15))

        form = tk.Frame(page, bg=PANEL)
        form.pack(fill="x", padx=55, pady=5)

        self.make_label(
            form, "QUESTION / RIDDLE", 10, MUTED, True, PANEL
        ).pack(anchor="w", padx=16, pady=(15, 5))

        self.custom_question = tk.Text(
            form, height=4, wrap="word",
            bg=CARD, fg=WHITE, insertbackground=WHITE,
            font=("Segoe UI", 11), relief="flat"
        )
        self.custom_question.pack(fill="x", padx=16)

        self.make_label(
            form, "CORRECT ANSWER", 10, MUTED, True, PANEL
        ).pack(anchor="w", padx=16, pady=(12, 5))

        self.custom_answer = tk.Entry(
            form, bg=CARD, fg=WHITE,
            insertbackground=WHITE,
            font=("Segoe UI", 11), relief="flat"
        )
        self.custom_answer.pack(fill="x", padx=16, ipady=7)

        self.make_label(
            form, "OPTIONAL HINT", 10, MUTED, True, PANEL
        ).pack(anchor="w", padx=16, pady=(12, 5))

        self.custom_hint = tk.Entry(
            form, bg=CARD, fg=WHITE,
            insertbackground=WHITE,
            font=("Segoe UI", 11), relief="flat"
        )
        self.custom_hint.pack(
            fill="x", padx=16, ipady=7, pady=(0, 15)
        )

        self.custom_status = self.make_label(
            page, f"Saved custom questions: {len(self.custom_levels)}",
            10, MUTED, False, BG
        )
        self.custom_status.pack(pady=8)

        buttons = tk.Frame(page, bg=BG)
        buttons.pack(pady=8)

        self.make_button(
            buttons, "+ ADD QUESTION", self.add_custom_question
        ).pack(side="left", padx=5)

        self.make_button(
            buttons, "PLAY MY CUSTOM QUIZ",
            self.play_custom_quiz, "#8B35D1", WHITE
        ).pack(side="left", padx=5)

        self.make_button(
            buttons, "MAIN MENU", self.build_welcome, CARD, WHITE
        ).pack(side="left", padx=5)

    def add_custom_question(self):
        question = self.custom_question.get("1.0", "end").strip()
        answer = self.custom_answer.get().strip()
        hint = self.custom_hint.get().strip()

        if not question or not answer:
            self.custom_status.config(
                text="Please enter both the question and the answer.",
                fg=RED
            )
            return

        if not hint:
            hint = "Read the question carefully and look for its key clue."

        item = {
            "title": f"Custom Mystery {len(self.custom_levels) + 1}",
            "location": "Your Custom Realm",
            "difficulty": "CUSTOM",
            "story": question,
            "puzzle": question,
            "answers": [answer.lower()],
            "hints": [hint],
            "solution": f"The correct answer is: {answer}"
        }

        self.custom_levels.append(item)

        try:
            self.save_custom_levels()
        except OSError as error:
            self.custom_levels.pop()
            self.custom_status.config(
                text=f"Could not save question: {error}", fg=RED
            )
            return

        self.custom_question.delete("1.0", "end")
        self.custom_answer.delete(0, "end")
        self.custom_hint.delete(0, "end")

        self.custom_status.config(
            text=f"Question saved! Total: {len(self.custom_levels)}",
            fg=GREEN
        )

    def play_custom_quiz(self):
        if not self.custom_levels:
            self.custom_status.config(
                text="Add at least one question first.", fg=RED
            )
            return
        self.start_game(self.custom_levels)

    # ---------------- GAME SCREEN ----------------

    def start_game(self, levels=None):
        self.active_levels = levels if levels is not None else LEVELS
        self.level_index = 0
        self.completed = set()
        self.hint_index = 0
        self.chat_busy = False

        self.clear_window()

        self.game_frame = tk.Frame(self.root, bg=BG)
        self.game_frame.pack(fill="both", expand=True, padx=16, pady=12)

        header = tk.Frame(self.game_frame, bg=BG)
        header.pack(fill="x", pady=(0, 10))

        self.make_label(
            header, "✦ DREAMQUEST AI", 19, PINK, True, BG
        ).pack(side="left")

        self.progress_label = self.make_label(
            header, "", 11, MUTED, True, BG
        )
        self.progress_label.pack(side="right")

        self.progress = tk.Canvas(
            self.game_frame, height=8, bg=CARD, highlightthickness=0
        )
        self.progress.pack(fill="x", pady=(0, 12))

        body = tk.Frame(self.game_frame, bg=BG)
        body.pack(fill="both", expand=True)

        self.story_panel = tk.Frame(body, bg=PANEL)
        self.story_panel.pack(
            side="left", fill="both", expand=True, padx=(0, 10)
        )

        self.story_title = self.make_label(
            self.story_panel, "", 17, PINK, True, PANEL
        )
        self.story_title.pack(anchor="w", padx=15, pady=(12, 5))

        self.location_label = self.make_label(
            self.story_panel, "", 10, PURPLE, True, PANEL
        )
        self.location_label.pack(anchor="w", padx=15, pady=3)

        self.story_text = tk.Text(
            self.story_panel, height=10, wrap="word",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 11),
            relief="flat", padx=15, pady=8
        )
        self.story_text.pack(fill="x", padx=4, pady=3)
        self.story_text.config(state="disabled")

        self.puzzle_label = self.make_label(
            self.story_panel, "", 12, WHITE, True, PANEL
        )
        self.puzzle_label.pack(anchor="w", padx=15, pady=(8, 5))

        self.answer_entry = tk.Entry(
            self.story_panel, font=("Segoe UI", 12),
            bg=CARD, fg=WHITE, insertbackground=WHITE,
            relief="flat"
        )
        self.answer_entry.pack(fill="x", padx=15, ipady=8)
        self.answer_entry.bind(
            "<Return>", lambda event: self.check_answer()
        )

        actions = tk.Frame(self.story_panel, bg=PANEL)
        actions.pack(fill="x", padx=12, pady=8)

        self.make_button(
            actions, "CHECK ANSWER", self.check_answer
        ).pack(side="left", padx=3)

        self.make_button(
            actions, "GET HINT", self.get_hint, "#D8B4FE", BG
        ).pack(side="left", padx=3)

        self.make_button(
            actions, "SHOW SOLUTION", self.show_solution,
            "#F9A8D4", BG
        ).pack(side="left", padx=3)

        self.feedback_label = self.make_label(
            self.story_panel, "Read the clues and enter your answer.",
            11, MUTED, False, PANEL
        )
        self.feedback_label.pack(
            anchor="w", padx=15, pady=(5, 15)
        )

        # AI COMPANION

        self.chat_panel = tk.Frame(body, bg=PANEL, width=340)
        self.chat_panel.pack(side="right", fill="both", padx=(5, 0))
        self.chat_panel.pack_propagate(False)

        self.make_label(
            self.chat_panel, "✧ AI COMPANION", 15, PINK, True, PANEL
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.make_label(
            self.chat_panel, "Ask about the current mystery.",
            9, MUTED, False, PANEL
        ).pack(anchor="w", padx=12, pady=(0, 8))

        self.chat_display = tk.Text(
            self.chat_panel, wrap="word",
            bg="#15112B", fg=WHITE,
            font=("Segoe UI", 10), relief="flat",
            padx=10, pady=10
        )
        self.chat_display.pack(
            fill="both", expand=True, padx=10, pady=(0, 8)
        )
        self.chat_display.config(state="disabled")

        self.add_chat(
            "AI", "Hello, explorer! Ask me for a hint or explanation."
        )

        self.chat_entry = tk.Entry(
            self.chat_panel, font=("Segoe UI", 10),
            bg=CARD, fg=WHITE, insertbackground=WHITE,
            relief="flat"
        )
        self.chat_entry.pack(fill="x", padx=10, ipady=8)
        self.chat_entry.bind(
            "<Return>", lambda event: self.ask_ai()
        )

        self.chat_send_button = self.make_button(
            self.chat_panel, "ASK AI", self.ask_ai
        )
        self.chat_send_button.pack(fill="x", padx=10, pady=8)

        navigation = tk.Frame(self.game_frame, bg=BG)
        navigation.pack(fill="x", pady=(8, 0))

        self.make_button(
            navigation, "MAIN MENU", self.build_welcome, CARD, WHITE
        ).pack(side="left")

        self.next_button = self.make_button(
            navigation, "NEXT MYSTERY →", self.next_level
        )
        self.next_button.pack(side="right")
        self.next_button.config(state="disabled")

        self.load_level()

    # ---------------- MYSTERY LOGIC ----------------

    def load_level(self):
        level = self.active_levels[self.level_index]
        self.hint_index = 0

        self.story_title.config(
            text=f"Mystery {self.level_index + 1}: {level['title']}"
        )

        self.location_label.config(
            text=f"LOCATION: {level.get('location', 'Unknown Realm')}  •  "
                 f"{level.get('difficulty', 'CUSTOM')}"
        )

        self.story_text.config(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.insert("1.0", level.get("story", ""))
        self.story_text.config(state="disabled")

        puzzle = level.get("puzzle", "").strip()
        story = level.get("story", "").strip()

        # Fix: do not display the same question twice.
        if puzzle and puzzle != story:
            self.puzzle_label.config(text=puzzle)
            self.puzzle_label.pack(
                anchor="w", padx=15, pady=(8, 5)
            )
        else:
            self.puzzle_label.config(text="")
            self.puzzle_label.pack_forget()

        self.answer_entry.delete(0, "end")
        self.feedback_label.config(
            text="Read the clues and enter your answer.", fg=MUTED
        )
        self.progress_label.config(
            text=f"Mystery {self.level_index + 1} / "
                 f"{len(self.active_levels)}"
        )

        self.next_button.config(
            state="normal" if self.level_index in self.completed
            else "disabled"
        )

        self.update_progress()

        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.config(state="disabled")
        self.add_chat(
            "AI", f"Welcome to {level['title']}! Ask me for a hint."
        )

    def normalize(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.split())

    def check_answer(self):
        level = self.active_levels[self.level_index]
        answer = self.normalize(self.answer_entry.get())

        if not answer:
            self.feedback_label.config(
                text="Please enter an answer first.", fg=RED
            )
            return

        accepted = [
            self.normalize(a) for a in level.get("answers", [])
        ]

        correct = any(
            answer == a or (len(a) > 3 and a in answer)
            for a in accepted
        )

        if correct:
            self.feedback_label.config(
                text="✦ Correct! You solved the mystery!",
                fg=GREEN
            )
            self.completed.add(self.level_index)
            self.next_button.config(state="normal")
            self.update_progress()
        else:
            self.feedback_label.config(
                text="Not quite! Read the clues and try again.",
                fg=RED
            )

    def get_hint(self):
        level = self.active_levels[self.level_index]
        hints = level.get("hints") or [
            "Read the story carefully and look for an important clue."
        ]

        hint = hints[min(self.hint_index, len(hints) - 1)]
        self.hint_index = min(self.hint_index + 1, len(hints) - 1)

        self.feedback_label.config(
            text="💡 Hint: " + hint, fg=PINK
        )

    def show_solution(self):
        level = self.active_levels[self.level_index]

        self.feedback_label.config(
            text="📖 Solution: " + level.get(
                "solution", "Review the clues carefully."
            ),
            fg=PINK
        )

        self.completed.add(self.level_index)
        self.next_button.config(state="normal")
        self.update_progress()

    def update_progress(self):
        if not hasattr(self, "progress"):
            return

        self.progress.delete("all")
        self.progress.update_idletasks()

        width = max(self.progress.winfo_width(), 100)
        fraction = len(self.completed) / max(len(self.active_levels), 1)

        self.progress.create_rectangle(
            0, 0, width * fraction, 8,
            fill=PURPLE, outline=""
        )

    def next_level(self):
        if self.level_index < len(self.active_levels) - 1:
            self.level_index += 1
            self.load_level()
        else:
            self.show_ending()

    def show_ending(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True)

        self.make_label(
            frame, "✦ ADVENTURE COMPLETE ✦",
            28, PINK, True, BG
        ).pack(pady=(120, 20))

        self.make_label(
            frame,
            f"You explored all {len(self.active_levels)} mysteries!\n\n"
            f"Mysteries completed: {len(self.completed)} / "
            f"{len(self.active_levels)}",
            16, WHITE, False, BG
        ).pack(pady=15)

        self.make_button(
            frame, "PLAY AGAIN",
            lambda: self.start_game(self.active_levels)
        ).pack(pady=10)

        self.make_button(
            frame, "MAIN MENU", self.build_welcome, CARD, WHITE
        ).pack(pady=8)

    # ---------------- AI CHAT ----------------

    def add_chat(self, speaker, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(
            "end", f"{speaker}: {message}\n\n"
        )
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")

    def ask_ai(self):
        question = self.chat_entry.get().strip()

        if not question or self.chat_busy:
            return

        self.chat_entry.delete(0, "end")
        self.add_chat("You", question)

        level = self.active_levels[self.level_index]
        lower = question.lower()

        # Local hints always work, even if Ollama is offline.
        hint_words = ("hint", "clue", "help me solve")

        if any(word in lower for word in hint_words):
            hints = level.get("hints") or [
                "Read the story carefully and look for an important clue."
            ]

            hint = hints[min(self.hint_index, len(hints) - 1)]
            self.hint_index = min(self.hint_index + 1, len(hints) - 1)

            self.add_chat("AI", hint)
            return

        # Use the built-in solution when the player asks for it.
        if any(word in lower for word in (
            "show solution", "give me the answer",
            "tell me the answer", "correct answer"
        )):
            self.add_chat(
                "AI", level.get("solution", "Review the clues carefully.")
            )
            return

        self.chat_busy = True
        self.chat_send_button.config(
            state="disabled", text="THINKING..."
        )

        prompt = (
            "You are a friendly fantasy mystery tutor for a student. "
            "Use simple English and answer in 2 to 4 short sentences. "
            "Explain the clues clearly. Do not invent facts. "
            "Do not reveal the full solution unless directly requested.\n\n"
            f"Mystery title: {level['title']}\n"
            f"Story: {level['story']}\n"
            f"Question: {level.get('puzzle', '')}\n"
            f"Hints: {' | '.join(level.get('hints', []))}\n"
            f"Solution: {level.get('solution', '')}\n"
            f"Student's message: {question}"
        )

        threading.Thread(
            target=self.ai_worker,
            args=(prompt,),
            daemon=True
        ).start()

    def ai_worker(self, prompt):
        response = None

        try:
            payload = json.dumps({
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }).encode("utf-8")

            request = urllib.request.Request(
                OLLAMA_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(request, timeout=25) as result:
                data = json.loads(result.read().decode("utf-8"))
                response = data.get("response", "").strip()

        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            response = self.fallback_ai(prompt)

        try:
            self.root.after(
                0, lambda msg=response: self.finish_ai(msg)
            )
        except tk.TclError:
            pass

    def fallback_ai(self, prompt):
        lower = prompt.lower()

        if "python" in lower:
            return (
                "Python is a programming language used to create games, "
                "apps, websites, and helpful tools."
            )

        if "explain" in lower or "why" in lower:
            return (
                "Look at the clues in the story and connect them step by "
                "step. Think about which detail supports your answer."
            )

        return (
            "I'm here to help! Read the mystery carefully and think about "
            "the important clues. You can also ask me for a hint."
        )

    def finish_ai(self, response):
        try:
            if not self.root.winfo_exists():
                return

            self.add_chat(
                "AI", response or "Let's try that question again."
            )

            self.chat_busy = False
            self.chat_send_button.config(
                state="normal", text="ASK AI"
            )
        except tk.TclError:
            pass


# ==================== RUN PROGRAM ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = DreamQuestGame(root)
    root.mainloop()
