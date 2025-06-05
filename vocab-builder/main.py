import time
import ujson
import random

from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_INKY_PACK

VOCABULARY_FILE_NAME = "/vocab.json"

# Setup display
display = PicoGraphics(display=DISPLAY_INKY_PACK)
display.set_update_speed(2)

DISPLAY_WIDTH, DISPLAY_HEIGHT = display.get_bounds()
WIDTH, HEIGHT = DISPLAY_WIDTH - 6, DISPLAY_HEIGHT


# Setup buttons
button_a = Button(12)  # Next
button_b = Button(13)  # Define
button_c = Button(14)  # Sleep / Reset

# Load vocabulary
with open(VOCABULARY_FILE_NAME, "r") as f:
    vocab_list = ujson.load(f)

# Utility functions
def draw_ui_labels():
    display.set_pen(0)   # Black text
    display.set_font("bitmap6")
    display.text("Next", 290, 28, scale=1, angle=270)
    display.text("Define", 290, 75, scale=1, angle=270)
    display.text("Sleep", 290, 117, scale=1, angle=270)

def clear_screen():
    display.set_pen(15)  # White background
    display.clear()
    draw_ui_labels()
    display.set_font("bitmap8")

def show_word(entry):
    clear_screen()
    display.set_font("serif")
    display.set_thickness(2)
    width = display.measure_text(entry["word"], scale=1)
    display.text(entry["word"], (WIDTH - width) // 2, (HEIGHT - 8) // 2, wordwrap=290, scale=1)
    display.update()

def show_definition(entry):
    display.text(entry["definition"], 0, 0, wordwrap=290, scale=2)
    display.text(entry["example"], 0, 64, wordwrap=290, scale=1)
    display.update()

def wait_for_input():
    while True:
        if button_a.read():
            return "next"
        elif button_b.read():
            return "define"
        elif button_c.read():
            return "sleep"
        time.sleep(0.1)

# Main loop
while True:
    entry = random.choice(vocab_list)
    show_word(entry)
    showing_definition = False

    while True:
        action = wait_for_input()

        if action == "next":
            break

        elif action == "define":
            showing_definition = not showing_definition
            clear_screen()
            if showing_definition:
                show_definition(entry)
            else:
                show_word(entry)

        elif action == "sleep":
            clear_screen()
            display.update()
            break
