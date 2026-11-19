
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# -----------------------------
# GAME SETTINGS
# -----------------------------

root = tk.Tk()
root.title("Hardware Randomness Testing Playground")
root.geometry("700x500")
root.configure(bg="#202030")
root.resizable(False, False)

# Current scene
current_scene = "start"
history = []

# -----------------------------
# SCENES
# -----------------------------

scenes = {
    "start": {
        "title": "Your Intro to Hardware Randomness",
        "text": "Welcome to the hardware randomness testing challenge!\n\nLearn to find common weaknesses in pseudorandom numbers to prevent attacks.",
        "choices": [
            ("Next", "WhatIsRandomness"),
        ]
    },

    "WhatIsRandomness": {
        "title": "What are random numbers?",
        "text": "Text about what security puposes are used for random numbers are used for",
        "choices": [
            ("Next", "HowIsRandomness"),
        ]
    },

    "HowIsRandomness": {
        "title": "How are random numbers created?",
        "text": "Short overview of how random numbers are created",
        "choices": [
            ("Next", "HowToCheck"),
        ]
    },


    "HowToCheck": {
        "title": "How do we evaluate the randomness of numbers from PRNGs?",
        "text": "Overview of NIST test suite",
        "choices": [
            ("Open the red door", "red"),
            ("Open the blue door", "blue")
        ]
    },

    "GameIntro": {
        "title": "NIST Randomness Tests",
        "text": "Describe how you can evaluate numbers or code and what the desired outputs are for each\nThere are five required tests and 6 optional tests.",
        "choices": [
            ("Analyze python code", "freq_test"),
            ("Analyze bitstreams", "binary_one"),
        ]
    },

    "freq_test": {
        "title": "Frequency Test",
        "text": "Explain frequency test",
        "choices": [
            ("Analyze PRNG", "freq_python")
        ]
    },

    "freq_python": {
        "title": "Generator Name",
        "text": "Explain generator and show code",
        "choices": [
            ("Analyze PRNG", "freq_test")
        ]
    },

    "binary_one": {
        "title": "Random number 1",
        "text": "Show binary value, have downloadable value, and five buttons for each of the tests",
        "choices": [
            ("Analyze PRNG", "freq_test")
        ]
    }

}

# ==========================================
# 3. POPUP FUNCTIONS
# ==========================================

def binary_info_popup():

    # Create popup window
    popup = tk.Toplevel(root)

    popup.title("Binary Information")
    popup.geometry("400x300")
    popup.configure(bg="#202030")

    # Popup heading
    popup_title = tk.Label(
        popup,
        text="Binary Number Information",
        font=("Arial", 18, "bold"),
        fg="white",
        bg="#202030"
    )
    popup_title.pack(pady=20)

    # Popup content
    popup_text = tk.Label(
        popup,
        text="This window contains information about the binary value.\n\nYou can put explanations, results, or instructions here.",
        font=("Arial", 12),
        fg="white",
        bg="#202030",
        wraplength=350,
        justify="center"
    )
    popup_text.pack(pady=20)

    # Close popup button
    close_button = tk.Button(
        popup,
        text="Close",
        command=popup.destroy
    )
    close_button.pack(pady=10)


# ==========================================
# 4. MAIN WINDOW DESIGN
# ==========================================

# Page title
title_label = tk.Label(
    root,
    text="",
    font=("Arial", 22, "bold"),
    fg="black",
    bg="#E9F7F7"
)
title_label.pack(pady=20)


# Main display box
display_box = tk.Frame(
    root,
    bg="#B3C9C9",
    width=600,
    height=250
)
display_box.pack(pady=10)
display_box.pack_propagate(False)


# Main page text
text_label = tk.Label(
    display_box,
    text="",
    font=("Arial", 14),
    fg="black",
    bg="#E9F7F7",
    wraplength=550,
    justify="center"
)
text_label.pack(expand=True, padx=20, pady=20)


# Button area
button_frame = tk.Frame(
    root,
    bg="#202030"
)
button_frame.pack(pady=20)


# ==========================================
# 5. PAGE SWITCHING FUNCTION
# ==========================================

def show_scene(scene_name):

    global current_scene

    current_scene = scene_name

    scene = scenes[scene_name]

    # Update page title
    title_label.config(text=scene["title"])

    # Update page text
    text_label.config(text=scene["text"])

    # Remove previous buttons
    for widget in button_frame.winfo_children():
        widget.destroy()


    # --------------------------------------
    # SPECIAL POPUP BUTTONS
    # --------------------------------------

    if scene_name == "binary_one":

        info_button = tk.Button(
            button_frame,
            text="Binary Information",
            font=("Arial", 12, "bold"),
            bg="#56568a",
            fg="white",
            command=binary_info_popup
        )

        info_button.pack(pady=5)


    # --------------------------------------
    # NORMAL NAVIGATION BUTTONS
    # --------------------------------------

    for button_text, destination in scene["choices"]:

        button = tk.Button(
            button_frame,
            text=button_text,
            font=("Arial", 12, "bold"),
            bg="#56568a",
            fg="white",
            command=lambda d=destination: show_scene(d)
        )

        button.pack(pady=5)


# ==========================================
# 6. START GAME
# ==========================================

show_scene("binary_one")

root.mainloop()
