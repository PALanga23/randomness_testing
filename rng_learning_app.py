"""
Interactive RNG / NIST-style learning app
-----------------------------------------
Requirements:
    pip install pillow

Uses only:
    tkinter, tkinter.messagebox, PIL (Pillow), plus Python standard library.

This is an educational simulator. Its compact tests are inspired by concepts in
NIST SP 800-22; it is NOT a validated implementation of the complete NIST STS.
Run with: python rng_learning_app.py
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import random
import math
import time
import threading
import secrets
from pathlib import Path


# ----------------------------- Test material -----------------------------

MANDATORY_TESTS = [
    {
        "name": "Frequency (Monobit) Test",
        "short": "Checks whether the numbers of 0s and 1s are approximately balanced.",
        "detail": (
            "The Frequency (Monobit) Test examines the proportion of ones and "
            "zeros in the entire bit sequence. A sequence with a large imbalance "
            "may indicate bias. Passing this test does not prove that a sequence "
            "is random; it only means this particular check did not find a "
            "statistically unusual imbalance."
        ),
        "metric": "ones",
    },
    {
        "name": "Runs Test",
        "short": "Checks the number of uninterrupted runs of identical bits.",
        "detail": (
            "A run is a maximal sequence of consecutive identical bits. For "
            "example, 0011100 contains three runs: 00, 111, and 00. Too many or "
            "too few runs can indicate that bits switch values at an unusual rate."
        ),
        "metric": "runs",
    },
    {
        "name": "Longest Run of Ones",
        "short": "Looks for unusually long stretches of consecutive 1 bits.",
        "detail": (
            "This test measures the longest run of ones in a sequence (the full "
            "NIST test uses block-based categories). An unusually long run can "
            "be a sign of structure or bias. This app reports the longest run "
            "as an educational diagnostic rather than a full NIST p-value."
        ),
        "metric": "longest",
    },
    {
        "name": "Block Frequency Test",
        "short": "Checks the balance of ones within smaller blocks.",
        "detail": (
            "The sequence is divided into equal-sized blocks and the fraction "
            "of ones is calculated in each block. This can reveal local bias "
            "that may be hidden by a balanced overall count."
        ),
        "metric": "blocks",
    },
    {
        "name": "Serial / Pattern Test",
        "short": "Looks at the distribution of short bit patterns.",
        "detail": (
            "Short patterns such as 00, 01, 10, and 11 are counted. If some "
            "patterns occur much more or less often than expected, the sequence "
            "may contain detectable structure. This simplified version counts "
            "overlapping pairs."
        ),
        "metric": "pairs",
    },
]

OPTIONAL_TESTS = [
    ("Poker Test", "Counts fixed-length patterns and compares how evenly they occur."),
    ("Cumulative Sums Test", "Tracks the cumulative walk formed by mapping 1 to +1 and 0 to -1."),
    ("Approximate Entropy", "Compares the frequency of overlapping patterns of adjacent lengths."),
    ("Linear Complexity", "Estimates the length of a shortest LFSR that can reproduce blocks."),
    ("Maurer's Universal Test", "Uses repeated pattern distances to look for compressible structure."),
    ("Random Excursions", "Studies visits to states in a cumulative-sum random walk."),
]

PYTHON_CASES = [
    {
        "name": "Python Mersenne Twister",
        "generator": "Python's random module uses the Mersenne Twister (MT19937) PRNG by default. It has a large period and is designed for simulation, but it is not cryptographically secure.",
        "code": """import random

# Reproducible pseudorandom values
random.seed(2026)
values = [random.getrandbits(1) for _ in range(256)]
bitstream = ''.join(map(str, values))
print(bitstream)
""",
    },
    {
        "name": "Linear Congruential Generator (LCG)",
        "generator": "An LCG updates its state with X(n+1) = (aX(n) + c) mod m. It is simple and fast, but poor parameter choices can create visible patterns and correlations.",
        "code": """def lcg(seed, count):
    a, c, m = 1664525, 1013904223, 2**32
    state = seed
    output = []
    for _ in range(count):
        state = (a * state + c) % m
        output.append(state & 1)
    return ''.join(map(str, output))

print(lcg(42, 256))
""",
    },
    {
        "name": "Xorshift32",
        "generator": "Xorshift generators use XOR and bit-shift operations to transform a state. Xorshift32 is compact and fast, but its output is not suitable for cryptographic use.",
        "code": """def xorshift32(seed, count):
    x = seed & 0xFFFFFFFF
    bits = []
    for _ in range(count):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        bits.append(str(x & 1))
    return ''.join(bits)

print(xorshift32(2463534242, 256))
""",
    },
    {
        "name": "Linear Feedback Shift Register",
        "generator": "An LFSR shifts its state and inserts a feedback bit computed from selected positions (taps). It can produce long sequences, but the output is deterministic and has linear structure.",
        "code": """def lfsr(seed, count):
    state = seed & 0x1F or 1
    bits = []
    for _ in range(count):
        bits.append(str(state & 1))
        feedback = ((state >> 0) ^ (state >> 2)) & 1
        state = (state >> 1) | (feedback << 4)
    return ''.join(bits)

print(lfsr(0b10101, 256))
""",
    },
    {
        "name": "Cryptographic System RNG",
        "generator": "Python's secrets module draws from the operating system's cryptographically secure randomness source. It is intended for security-sensitive tokens, unlike simulation-focused PRNGs.",
        "code": """import secrets

# Generate bits from the operating system's secure RNG
bits = ''.join(str(secrets.randbits(1)) for _ in range(256))
print(bits)
""",
    },
]


OPTIONAL_PYTHON_CASES = [
    {
        "name": "Python SystemRandom",
        "generator": "random.SystemRandom obtains random values from the operating system rather than Python's deterministic Mersenne Twister state. It is useful when OS-backed randomness is desired.",
        "code": """import random

rng = random.SystemRandom()
bits = ''.join(str(rng.getrandbits(1)) for _ in range(512))
print(bits)
""",
    },
    {
        "name": "Middle-Square Generator",
        "generator": "The middle-square method squares its current state and extracts middle digits for the next state. It is historically important but often falls into short cycles or zero states.",
        "code": """def middle_square(seed, count):
    state = seed % 10000
    bits = []
    for _ in range(count):
        square = state * state
        state = (square // 100) % 10000
        bits.append(str(state & 1))
    return ''.join(bits)

print(middle_square(6759, 256))
""",
    },
    {
        "name": "Park-Miller Minimal Standard",
        "generator": "The Park-Miller generator is a multiplicative linear congruential generator with carefully selected parameters. It is compact and reproducible, but remains a deterministic, non-cryptographic PRNG.",
        "code": """def park_miller(seed, count):
    state = seed % 2147483647
    bits = []
    for _ in range(count):
        state = (16807 * state) % 2147483647
        bits.append(str(state & 1))
    return ''.join(bits)

print(park_miller(12345, 256))
""",
    },
    {
        "name": "Additive Fibonacci Generator",
        "generator": "An additive lagged-Fibonacci generator combines earlier state values to create new values. Its quality depends on the lags, arithmetic, and initialization; it is not a cryptographic generator.",
        "code": """def additive_fibonacci(seed, count):
    state = [(seed + i * 7919) % 256 for i in range(17)]
    bits = []
    for i in range(count):
        value = (state[-17] + state[-5]) % 256
        state.append(value)
        bits.append(str(value & 1))
    return ''.join(bits)

print(additive_fibonacci(37, 256))
""",
    },
    {
        "name": "Python Random Float Conversion",
        "generator": "This example uses random.random(), which returns a floating-point value in [0, 1). Comparing each value with 0.5 converts it into a bit, illustrating how a sampling rule affects the resulting sequence.",
        "code": """import random

random.seed(2026)
bits = ''.join(
    '1' if random.random() >= 0.5 else '0'
    for _ in range(512)
)
print(bits)
""",
    },
    {
        "name": "Seeded Byte Generator",
        "generator": "This example generates bytes from a seeded PRNG and expands each byte into eight bits. It highlights the distinction between byte-oriented output and bit-oriented analysis.",
        "code": """import random

random.seed(8675309)
data = bytes(random.getrandbits(8) for _ in range(64))
bitstream = ''.join(f'{byte:08b}' for byte in data)
print(bitstream)
""",
    },
]


# Optional tests are shared by both paths.
ALL_TESTS = MANDATORY_TESTS + [
    {"name": name, "short": desc, "detail": desc, "metric": "optional"}
    for name, desc in OPTIONAL_TESTS
]


# ----------------------------- Main application -----------------------------

class RNGApp:
    BG = "#101827"
    PANEL = "#19263a"
    PANEL2 = "#22334b"
    TEXT = "#edf3fb"
    MUTED = "#a9bad0"
    ACCENT = "#57d6c5"
    ACCENT2 = "#83a8ff"
    GOOD = "#76d7a5"
    WARN = "#ffca75"

    def __init__(self, root):
        self.root = root
        self.root.title("RNG Lab | Randomness Explorer")
        self.root.geometry("1080x760")
        self.root.minsize(850, 620)
        self.responses = []
        self.path_choice = None
        self.stage_index = 0
        self.optional_mode = False
        self.optional_index = 0
        self.bitstreams = [self.make_bitstream(i) for i in range(5)]
        self.current_python = 0
        self.current_bit = 0
        self.active_test = 0
        self._image_refs = []
        self.configure_style()
        self.show_intro()

    def configure_style(self):
        self.root.configure(bg=self.BG)
        self.default_font = ("Segoe UI", 10)
        self.title_font = ("Segoe UI", 25, "bold")
        self.heading_font = ("Segoe UI", 16, "bold")
        self.root.option_add("*Font", self.default_font)

    def make_bitstream(self, index):
        # Deterministic demonstration streams, each with a different character.
        rng = random.Random(7301 + index * 91)
        if index == 0:
            return "01" * 512
        if index == 1:
            return "0" * 400 + "1" * 624
        if index == 2:
            return "".join(str(rng.getrandbits(1)) for _ in range(1024))
        if index == 3:
            # Repeating four-bit pattern.
            return ("0011" * 256)
        return "".join(str(rng.getrandbits(1)) for _ in range(1024))

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def header(self, eyebrow="RNG LEARNING LAB", title="", subtitle=""):
        top = tk.Frame(self.root, bg=self.BG)
        top.pack(fill="x", padx=30, pady=(22, 10))
        tk.Label(top, text=eyebrow, fg=self.ACCENT, bg=self.BG,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(top, text=title, fg=self.TEXT, bg=self.BG,
                 font=self.title_font).pack(anchor="w", pady=(3, 2))
        if subtitle:
            tk.Label(top, text=subtitle, fg=self.MUTED, bg=self.BG,
                     wraplength=950, justify="left").pack(anchor="w")

    def panel(self, parent, padx=20, pady=16):
        frame = tk.Frame(parent, bg=self.PANEL, padx=padx, pady=pady,
                         highlightthickness=1, highlightbackground="#2d405a")
        return frame

    def label(self, parent, text, **kwargs):
        opts = dict(bg=self.PANEL, fg=self.TEXT, justify="left",
                    wraplength=900, anchor="w")
        opts.update(kwargs)
        return tk.Label(parent, text=text, **opts)

    def button(self, parent, text, command, primary=False, **kwargs):
        bg = self.ACCENT if primary else self.PANEL2
        fg = "#10202a" if primary else self.TEXT
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=self.ACCENT2, activeforeground="#10202a",
                         relief="flat", bd=0, padx=16, pady=10,
                         cursor="hand2", font=("Segoe UI", 10, "bold"),
                         **kwargs)

    def content_area(self):
        outer = tk.Frame(self.root, bg=self.BG)
        outer.pack(fill="both", expand=True, padx=30, pady=(8, 25))
        canvas = tk.Canvas(outer, bg=self.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=980)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return inner

    def show_intro(self):
        self.clear()
        self.header(title="Explore the science of randomness",
                    subtitle="An interactive walkthrough of random number generators, bitstreams, and statistical testing.")
        body = self.content_area()
        card = self.panel(body, padx=26, pady=24)
        card.pack(fill="x", pady=10)
        # Create a small decorative PIL banner, then display it with ImageTk.
        image = Image.new("RGB", (900, 110), "#22334b")
        draw = ImageDraw.Draw(image)
        for x in range(0, 900, 18):
            height = 18 + ((x * 7) % 70)
            draw.rounded_rectangle((x, 100-height, x+9, 100), radius=3, fill="#57d6c5")
        photo = ImageTk.PhotoImage(image)
        self._image_refs.append(photo)
        tk.Label(card, image=photo, bg=self.PANEL).pack(fill="x", pady=(0, 18))
        self.label(card, "What is a random number?", font=self.heading_font).pack(anchor="w")
        self.label(card,
            "A random number is a value selected without a predictable pattern. "
            "Randomness is useful in simulations, scientific sampling, games, and security. "
            "A sequence can look random while still containing hidden structure.",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(8, 16))
        self.label(card, "What is an RNG?", font=self.heading_font).pack(anchor="w")
        self.label(card,
            "A random number generator (RNG) produces values that are intended to be "
            "unpredictable or statistically well-behaved. A pseudorandom number generator "
            "(PRNG) computes a deterministic sequence from an initial state or seed. "
            "A cryptographically secure RNG is designed to resist prediction by an attacker.",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(8, 16))
        self.label(card, "Why test a sequence?", font=self.heading_font).pack(anchor="w")
        self.label(card,
            "Statistical tests can identify certain patterns or biases. Passing a test "
            "does not prove true randomness, and failing one does not by itself identify "
            "the cause. Test results must be interpreted in context.",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(8, 0))
        self.button(body, "Continue to NIST overview  →", self.show_nist, primary=True).pack(anchor="e", pady=18)

    def show_nist(self):
        self.clear()
        self.header(title="The NIST Statistical Test Suite",
                    subtitle="A guided introduction to statistical tests for binary sequences.")
        body = self.content_area()
        card = self.panel(body, padx=25, pady=22)
        card.pack(fill="x", pady=10)
        self.label(card, "NIST SP 800-22", font=self.heading_font).pack(anchor="w")
        self.label(card,
            "NIST Special Publication 800-22 describes statistical tests for evaluating "
            "the randomness of binary sequences. The suite includes tests for frequency, "
            "runs, patterns, spectral characteristics, complexity, and other properties.",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(8, 14))
        self.label(card, "What this lab covers", font=self.heading_font).pack(anchor="w")
        self.label(card,
            "The five mandatory activities in this learning app are an educational subset "
            "inspired by NIST test concepts: Frequency (Monobit), Runs, Longest Run of Ones, "
            "Block Frequency, and Serial / Pattern. Six additional activities are available "
            "as optional concept demonstrations.",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(8, 14))
        note = tk.Label(card,
            text="Important: this app uses simplified demonstrations, not the official NIST STS "
                "implementation. Its displayed outcomes are learning aids, not certification.",
            bg="#3a3022",
            fg=self.WARN,
            padx=12,
            pady=12,
            wraplength=900,
            justify="left"
        )
        note.pack(fill="x")
        self.button(body, "Choose an analysis path  →", self.show_choice, primary=True).pack(anchor="e", pady=18)

    def show_choice(self):
        self.clear()
        self.header(title="Choose your analysis path",
                    subtitle="Both paths contain five required stages, followed by six optional test activities.")
        body = self.content_area()
        row = tk.Frame(body, bg=self.BG)
        row.pack(fill="x", pady=12)
        for title, desc, choice in [
            ("Analyze Python code", "Inspect five Python examples that emulate different random number generators. Download each code sample and record your observations.", "python"),
            ("Analyze bitstreams", "Explore five binary sequences. Download each full stream, open test explanations, and run simplified statistical checks.", "bits"),
        ]:
            card = self.panel(row, padx=22, pady=22)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            self.label(card, title, font=self.heading_font).pack(anchor="w")
            self.label(card, desc, bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(10, 20))
            self.button(card, "Select this path  →",
                        lambda c=choice: self.start_path(c), primary=True).pack(anchor="w")
        self.button(body, "Back", self.show_nist).pack(anchor="w", pady=10)

    def start_path(self, choice):
        self.path_choice = choice
        self.stage_index = 0
        self.optional_mode = False
        if choice == "python":
            self.show_python_stage()
        else:
            self.show_bit_stage()

    def add_response_box(self, parent, test_name):
        self.label(parent, "Your observations / interpretation", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(14, 5))
        text = tk.Text(parent, height=4, wrap="word", bg="#0e1725", fg=self.TEXT,
                       insertbackground=self.TEXT, relief="flat", padx=10, pady=8)
        text.pack(fill="x")
        existing = next((r["response"] for r in self.responses if r["test"] == test_name), "")
        if existing:
            text.insert("1.0", existing)
        return text

    def save_response(self, test_name, widget):
        value = widget.get("1.0", "end").strip()
        found = False
        for record in self.responses:
            if record["test"] == test_name:
                record["response"] = value
                found = True
                break
        if not found:
            self.responses.append({"test": test_name, "response": value})

    def show_python_stage(self):
        self.clear()
        case = PYTHON_CASES[self.stage_index]
        self.header(eyebrow=f"PYTHON CODE PATH  •  REQUIRED STAGE {self.stage_index + 1} OF 5",
                    title=case["name"], subtitle="Read the generator description, inspect the sample, and record what you notice.")
        body = self.content_area()
        card = self.panel(body, padx=22, pady=20)
        card.pack(fill="x", pady=8)
        self.label(card, "Generator overview", font=self.heading_font).pack(anchor="w")
        self.label(card, case["generator"], bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(7, 14))
        self.label(card, "Python example", font=self.heading_font).pack(anchor="w")
        code_box = tk.Text(card, height=13, wrap="none", bg="#0b1320", fg="#b8e7df",
                           insertbackground=self.TEXT, relief="flat", padx=12, pady=10,
                           font=("Consolas", 10))
        code_box.pack(fill="x", pady=(8, 8))
        code_box.insert("1.0", case["code"])
        code_box.configure(state="disabled")
        self.button(card, "Download this .py sample", lambda: self.download_text(
            case["code"], case["name"].lower().replace(" ", "_") + ".py")).pack(anchor="w")
        response = self.add_response_box(card, case["name"])
        controls = tk.Frame(body, bg=self.BG)
        controls.pack(fill="x", pady=15)
        self.button(controls, "Save response", lambda: self.save_response(case["name"], response)).pack(side="left")
        if self.stage_index > 0:
            self.button(controls, "← Previous", self.previous_python).pack(side="left", padx=8)
        next_text = "Next stage  →" if self.stage_index < 4 else "Complete required stages  →"
        self.button(controls, next_text, lambda: self.advance_python(response), primary=True).pack(side="right")

    def previous_python(self):
        self.stage_index -= 1
        self.show_python_stage()

    def advance_python(self, response):
        case = PYTHON_CASES[self.stage_index]
        self.save_response(case["name"], response)
        if self.stage_index < 4:
            self.stage_index += 1
            self.show_python_stage()
        else:
            self.show_checkpoint()

    def show_bit_stage(self):
        self.clear()
        stream = self.bitstreams[self.stage_index]
        name = f"Bitstream {self.stage_index + 1}"
        self.header(eyebrow=f"BITSTREAM PATH  •  REQUIRED STAGE {self.stage_index + 1} OF 5",
                    title=name, subtitle="Inspect the beginning of the sequence, download the complete stream, and run the test activities.")
        body = self.content_area()
        card = self.panel(body, padx=22, pady=18)
        card.pack(fill="x", pady=8)
        self.label(card, "First 100 bits", font=self.heading_font).pack(anchor="w")
        preview = tk.Text(card, height=4, wrap="char", bg="#0b1320", fg="#b8e7df",
                          relief="flat", padx=10, pady=10, font=("Consolas", 11))
        preview.pack(fill="x", pady=8)
        preview.insert("1.0", stream[:100])
        preview.configure(state="disabled")
        self.label(card, f"Full stream length: {len(stream):,} bits", bg=self.PANEL, fg=self.MUTED).pack(anchor="w")
        self.button(card, "Download full bitstream (.txt)",
                    lambda: self.download_text(stream, f"bitstream_{self.stage_index + 1}.txt")).pack(anchor="w", pady=8)

        test_area = self.panel(card, padx=15, pady=14)
        test_area.pack(fill="x", pady=(12, 5))
        self.label(test_area, "Five required tests", font=self.heading_font).pack(anchor="w", pady=(0, 8))
        btnrow = tk.Frame(test_area, bg=self.PANEL)
        btnrow.pack(fill="x")
        for i, test in enumerate(MANDATORY_TESTS):
            self.button(btnrow, f"{i+1}. {test['name']}",
                        lambda idx=i: self.explain_test(idx)).pack(fill="x", pady=3)
        self.label(test_area, "SELECT A TEST TO RUN", font=("Segoe UI", 11, "bold"),
                   fg=self.ACCENT).pack(anchor="w", pady=(12, 5))
        runrow = tk.Frame(test_area, bg=self.PANEL)
        runrow.pack(fill="x", anchor="w")
        self.run_choice = tk.StringVar(value=MANDATORY_TESTS[0]["name"])
        menu = tk.OptionMenu(runrow, self.run_choice, *[t["name"] for t in MANDATORY_TESTS])
        menu.configure(bg="#304765", fg=self.TEXT, activebackground=self.ACCENT2,
                       activeforeground="#10202a", highlightthickness=1,
                       highlightbackground=self.ACCENT2, relief="flat",
                       font=("Segoe UI", 11, "bold"), padx=12, pady=7,
                       indicatoron=True, width=28)
        menu["menu"].configure(bg=self.PANEL2, fg=self.TEXT,
                               activebackground=self.ACCENT2, activeforeground="#10202a",
                               font=("Segoe UI", 10))
        menu.pack(side="left", padx=(0, 10))
        self.button(runrow, "▶  RUN SELECTED TEST", lambda: self.run_bit_test(stream),
                    primary=True).pack(side="left")
        tk.Label(test_area, text="TEST RESULT  •  Select and copy the text below",
                 bg=self.PANEL, fg=self.ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 4))
        self.output_label = tk.Text(test_area, height=4, wrap="word", bg="#0b1320",
                                    fg=self.TEXT, insertbackground=self.TEXT,
                                    relief="flat", padx=12, pady=10,
                                    font=("Segoe UI", 10), selectbackground="#365a80")
        self.output_label.pack(fill="x", pady=(0, 8))
        self.output_label.insert("1.0", "Choose a test from the drop-down menu, then select RUN SELECTED TEST.")
        self.output_label.configure(state="disabled")
        response = self.add_response_box(card, name)
        controls = tk.Frame(body, bg=self.BG)
        controls.pack(fill="x", pady=15)
        self.button(controls, "Save response", lambda: self.save_response(name, response)).pack(side="left")
        if self.stage_index > 0:
            self.button(controls, "← Previous", self.previous_bit).pack(side="left", padx=8)
        next_text = "Next bitstream  →" if self.stage_index < 4 else "Complete required stages  →"
        self.button(controls, next_text, lambda: self.advance_bit(response), primary=True).pack(side="right")

    def previous_bit(self):
        self.stage_index -= 1
        self.show_bit_stage()

    def advance_bit(self, response):
        name = f"Bitstream {self.stage_index + 1}"
        self.save_response(name, response)
        if self.stage_index < 4:
            self.stage_index += 1
            self.show_bit_stage()
        else:
            self.show_checkpoint()

    def themed_popup(self, title, detail):
        """Show a themed in-app explanation window instead of a system error-style dialog."""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=self.BG)
        popup.transient(self.root)
        popup.grab_set()
        popup.geometry("560x300")
        popup.minsize(420, 240)

        outer = tk.Frame(popup, bg=self.PANEL, padx=24, pady=22,
                         highlightthickness=1, highlightbackground="#2d405a")
        outer.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(outer, text="TEST EXPLANATION", bg=self.PANEL, fg=self.ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(outer, text=title, bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 17, "bold"), wraplength=490,
                 justify="left").pack(anchor="w", pady=(5, 12))
        tk.Label(outer, text=detail, bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 10), wraplength=490,
                 justify="left").pack(anchor="w", fill="x", expand=True)
        self.button(outer, "Close", popup.destroy, primary=True).pack(anchor="e", pady=(18, 0))

    def explain_test(self, index):
        test = MANDATORY_TESTS[index]
        self.themed_popup(test["name"], test["detail"])

    def run_bit_test(self, stream):
        name = self.run_choice.get()
        test = next(t for t in MANDATORY_TESTS if t["name"] == name)
        self.set_test_output("Running test: [                    ] 0%")
        self.root.update_idletasks()
        self.animate_test(stream, test, 0)

    def animate_test(self, stream, test, progress):
        if progress < 100:
            filled = progress // 5
            bar = "█" * filled + "░" * (20 - filled)
            self.set_test_output(f"Running {test['name']}: [{bar}] {progress}%")
            self.root.after(45, lambda: self.animate_test(stream, test, progress + 10))
            return
        result = self.calculate_test(stream, test["metric"])
        self.set_test_output(result)

    def set_test_output(self, text):
        self.output_label.configure(state="normal")
        self.output_label.delete("1.0", "end")
        self.output_label.insert("1.0", text)
        self.output_label.configure(state="disabled")

    def calculate_test(self, bits, metric):
        n = len(bits)
        ones = bits.count("1")
        zeros = n - ones
        if metric == "ones":
            ratio = ones / n
            verdict = "near balance" if abs(ratio - 0.5) < 0.06 else "noticeable imbalance"
            return f"Result: {ones:,} ones and {zeros:,} zeros ({ratio:.3f} ones fraction). This sample shows {verdict}. Educational diagnostic only; not an official NIST p-value."
        if metric == "runs":
            runs = 1 + sum(bits[i] != bits[i-1] for i in range(1, n))
            expected = 1 + (2 * ones * zeros / n)
            return f"Result: {runs:,} runs observed; a rough balance-based expectation is about {expected:,.1f}. Compare the values as a descriptive check, not a formal pass/fail."
        if metric == "longest":
            longest = max((len(x) for x in bits.split("0")), default=0)
            return f"Result: longest run of ones = {longest} bit(s). The official NIST test uses block categories and a statistical reference distribution."
        if metric == "blocks":
            block_size = 64
            fractions = [bits[i:i+block_size].count("1") / len(bits[i:i+block_size])
                         for i in range(0, n, block_size) if bits[i:i+block_size]]
            mean = sum(fractions) / len(fractions)
            spread = math.sqrt(sum((x-mean)**2 for x in fractions) / len(fractions))
            return f"Result: {len(fractions)} blocks of up to 64 bits; mean one-fraction = {mean:.3f}; standard deviation across blocks = {spread:.3f}."
        if metric == "pairs":
            pairs = {"00": 0, "01": 0, "10": 0, "11": 0}
            for i in range(n - 1):
                pairs[bits[i:i+2]] += 1
            return "Overlapping pair counts: " + ", ".join(f"{k}: {v}" for k, v in pairs.items()) + ". Similar counts are not proof of randomness."
        return "This optional activity is a concept demonstration; see its explanation."

    def show_checkpoint(self):
        self.clear()
        self.header(title="Five required stages complete",
                    subtitle="Choose what you would like to do next.")
        body = self.content_area()
        card = self.panel(body, padx=26, pady=24)
        card.pack(fill="x", pady=12)
        self.label(card, "Your progress is saved in this session.", font=self.heading_font).pack(anchor="w")
        self.label(card,
            "You can explore the other analysis path, try six optional test concepts, "
            "or finish and download your written observations.",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(8, 18))
        self.button(card, "Restart and choose the other path", self.restart_other).pack(fill="x", pady=5)
        self.button(card, "Explore 6 optional tests", self.show_optional).pack(fill="x", pady=5)
        self.button(card, "Finish and download responses", self.show_finish, primary=True).pack(fill="x", pady=5)

    def restart_other(self):
        other = "bits" if self.path_choice == "python" else "python"
        self.start_path(other)

    def show_optional(self):
        """Start six optional stages matching the selected analysis path."""
        self.optional_index = 0
        self.show_optional_stage()

    def show_optional_stage(self):
        self.clear()
        total = 6
        if self.path_choice == "python":
            case = OPTIONAL_PYTHON_CASES[self.optional_index]
            self.header(eyebrow=f"PYTHON CODE PATH  •  OPTIONAL STAGE {self.optional_index + 1} OF {total}",
                        title=case["name"],
                        subtitle="Inspect this additional generator example, download the code, and record your analysis.")
            body = self.content_area()
            card = self.panel(body, padx=22, pady=20)
            card.pack(fill="x", pady=8)
            self.label(card, "Generator overview", font=self.heading_font).pack(anchor="w")
            self.label(card, case["generator"], bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(7, 14))
            self.label(card, "Python example", font=self.heading_font).pack(anchor="w")
            code_box = tk.Text(card, height=13, wrap="none", bg="#0b1320", fg="#b8e7df",
                               insertbackground=self.TEXT, relief="flat", padx=12, pady=10,
                               font=("Consolas", 10))
            code_box.pack(fill="x", pady=(8, 8))
            code_box.insert("1.0", case["code"])
            code_box.configure(state="disabled")
            self.button(card, "Download this .py sample",
                        lambda: self.download_text(case["code"],
                            case["name"].lower().replace(" ", "_") + ".py")).pack(anchor="w")
            response = self.add_response_box(card, case["name"])
            controls = tk.Frame(body, bg=self.BG)
            controls.pack(fill="x", pady=15)
            self.button(controls, "Save response",
                        lambda: self.save_response(case["name"], response)).pack(side="left")
            if self.optional_index > 0:
                self.button(controls, "← Previous",
                            self.previous_optional).pack(side="left", padx=8)
            next_label = "Next optional example  →" if self.optional_index < 5 else "Finish optional tests  →"
            self.button(controls, next_label,
                        lambda: self.advance_optional(response, case["name"]),
                        primary=True).pack(side="right")
        else:
            test = OPTIONAL_TESTS[self.optional_index]
            name, description = test
            self.header(eyebrow=f"BITSTREAM PATH  •  OPTIONAL TEST {self.optional_index + 1} OF {total}",
                        title=name,
                        subtitle="Read what this test investigates, run its educational demonstration, and record your interpretation.")
            body = self.content_area()
            card = self.panel(body, padx=22, pady=20)
            card.pack(fill="x", pady=8)
            self.label(card, "What does this test examine?", font=self.heading_font).pack(anchor="w")
            self.label(card, description, bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(7, 12))
            self.button(card, "Read test explanation",
                        lambda n=name, d=description: self.themed_popup(n, d)).pack(anchor="w")
            self.label(card, "Run this test on the current bitstream", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(18, 5))
            stream = self.bitstreams[self.stage_index]
            self.optional_output = tk.Text(card, height=4, wrap="word", bg="#0b1320",
                                           fg=self.TEXT, insertbackground=self.TEXT,
                                           relief="flat", padx=12, pady=10,
                                           font=("Segoe UI", 10), selectbackground="#365a80")
            self.optional_output.pack(fill="x", pady=8)
            self.optional_output.insert("1.0", "Select Run optional test to display the result. You can select and copy the result text.")
            self.optional_output.configure(state="disabled")
            self.button(card, "▶  RUN OPTIONAL TEST",
                        lambda: self.run_optional_bit_test(stream, self.optional_index),
                        primary=True).pack(anchor="w")
            response = self.add_response_box(card, name)
            controls = tk.Frame(body, bg=self.BG)
            controls.pack(fill="x", pady=15)
            self.button(controls, "Save response",
                        lambda: self.save_response(name, response)).pack(side="left")
            if self.optional_index > 0:
                self.button(controls, "← Previous",
                            self.previous_optional).pack(side="left", padx=8)
            next_label = "Next optional test  →" if self.optional_index < 5 else "Finish optional tests  →"
            self.button(controls, next_label,
                        lambda: self.advance_optional(response, name),
                        primary=True).pack(side="right")

    def previous_optional(self):
        self.optional_index = max(0, self.optional_index - 1)
        self.show_optional_stage()

    def advance_optional(self, response, name):
        self.save_response(name, response)
        if self.optional_index < 5:
            self.optional_index += 1
            self.show_optional_stage()
        else:
            self.show_finish()

    def run_optional_bit_test(self, stream, index):
        self.set_optional_output("Running optional test: [                    ] 0%", disabled=False)
        self.animate_optional_bit_test(stream, index, 0)

    def set_optional_output(self, text, disabled=True):
        self.optional_output.configure(state="normal")
        self.optional_output.delete("1.0", "end")
        self.optional_output.insert("1.0", text)
        if disabled:
            self.optional_output.configure(state="disabled")

    def animate_optional_bit_test(self, stream, index, progress):
        name, description = OPTIONAL_TESTS[index]
        if progress < 100:
            filled = progress // 5
            bar = "█" * filled + "░" * (20 - filled)
            self.set_optional_output(f"Running {name}: [{bar}] {progress}%", disabled=False)
            self.root.after(45, lambda: self.animate_optional_bit_test(stream, index, progress + 10))
            return
        result = self.calculate_optional_test(stream, index)
        self.set_optional_output(result, disabled=True)

    def calculate_optional_test(self, bits, index):
        n = len(bits)
        if index == 0:  # Poker: four-bit word counts
            words = [bits[i:i+4] for i in range(0, n - 3, 4)]
            counts = {format(i, "04b"): 0 for i in range(16)}
            for word in words:
                counts[word] += 1
            distinct = sum(value > 0 for value in counts.values())
            return f"Poker demonstration: {len(words)} non-overlapping 4-bit words; {distinct} of 16 possible patterns appeared. Pattern counts: " + ", ".join(f"{k}={v}" for k, v in counts.items()) + "."
        if index == 1:  # Cumulative sums
            walk = 0
            peak = 0
            for bit in bits:
                walk += 1 if bit == "1" else -1
                peak = max(peak, abs(walk))
            return f"Cumulative sums demonstration: final walk position = {walk}; maximum absolute distance from zero = {peak}. The formal test evaluates the walk statistic against a reference distribution."
        if index == 2:  # Approximate entropy, compare 2-bit and 3-bit frequencies
            def phi(m):
                counts = {}
                extended = bits + bits[:m-1]
                for i in range(n):
                    pattern = extended[i:i+m]
                    counts[pattern] = counts.get(pattern, 0) + 1
                return sum((c/n) * math.log(c/n) for c in counts.values() if c)
            value = phi(2) - phi(3)
            return f"Approximate entropy demonstration: phi(2) = {phi(2):.4f}; phi(3) = {phi(3):.4f}; approximate entropy = {value:.4f}. This compact estimate is descriptive, not the official NIST p-value."
        if index == 3:  # Linear complexity proxy
            runs = 1 + sum(bits[i] != bits[i-1] for i in range(1, n))
            transitions = sum(bits[i] != bits[i-1] for i in range(1, n))
            return f"Linear complexity concept check: {transitions} bit transitions were observed across {n} bits. This is not a Berlekamp–Massey linear-complexity calculation; it is a simple structural indicator only."
        if index == 4:  # Maurer-inspired repeated word distances
            width = 4
            seen = {}
            distances = []
            for i in range(0, n - width + 1, width):
                word = bits[i:i+width]
                if word in seen:
                    distances.append(i // width - seen[word])
                seen[word] = i // width
            avg = sum(distances) / len(distances) if distances else 0
            return f"Maurer-inspired demonstration: {len(distances)} repeated 4-bit word gaps were found; average gap = {avg:.2f} words. The official Universal test uses a more specific estimator and calibration."
        # Random excursions: visits to states in a cumulative walk
        walk = 0
        visits = {}
        for bit in bits:
            walk += 1 if bit == "1" else -1
            if walk == 0:
                visits[0] = visits.get(0, 0) + 1
            elif -4 <= walk <= 4:
                visits[walk] = visits.get(walk, 0) + 1
        summary = ", ".join(f"state {k}: {v}" for k, v in sorted(visits.items()))
        return f"Random excursions concept demonstration: visits to selected walk states: {summary or 'none'}. The formal NIST test has cycle-count and sample-size requirements."

    def show_finish(self):
        self.clear()
        self.header(title="Lab complete",
                    subtitle="Your written observations are collected. Download them as a text file.")
        body = self.content_area()
        card = self.panel(body, padx=26, pady=24)
        card.pack(fill="x", pady=12)
        self.label(card, f"Saved response entries: {len(self.responses)}",
                   font=self.heading_font).pack(anchor="w")
        self.label(card,
            "The output file uses one entry per activity in the format:\n"
            "<test name>, user response: <your text>",
            bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(10, 16))
        self.button(card, "Download all responses (.txt)", self.download_responses,
                    primary=True).pack(anchor="w")
        self.button(body, "Return to start", self.show_intro).pack(anchor="w", pady=12)

    def download_text(self, content, suggested_name):
        path = filedialog.asksaveasfilename(
            defaultextension=Path(suggested_name).suffix,
            initialfile=suggested_name,
            filetypes=[("Text / Python files", "*.txt *.py"), ("All files", "*.*")])
        if path:
            try:
                Path(path).write_text(content, encoding="utf-8")
                messagebox.showinfo("Download saved", f"File saved to:\n{path}")
            except OSError as exc:
                messagebox.showerror("Could not save file", str(exc))

    def download_responses(self):
        lines = [
            f"{record['test']}, user response: {record['response']}"
            for record in self.responses
        ]
        content = "\n".join(lines) if lines else "No responses were entered."
        self.download_text(content, "rng_lab_responses.txt")


def main():
    root = tk.Tk()
    RNGApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
