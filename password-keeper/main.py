import json
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
import pimoroni
import machine
import time

# Display setup
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=0)
WIDTH, HEIGHT = display.get_bounds()
display.set_font("bitmap8")

# Turn off the RGB LED
led = pimoroni.RGBLED(6, 7, 8)
led.set_rgb(0, 0, 0)

BLACK_PEN = display.create_pen(0, 0, 0)
GRAY_PEN = display.create_pen(100, 100, 100)
WHITE_PEN = display.create_pen(255, 255, 255)

# Button pin assignments
BUTTON_A = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
BUTTON_B = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
BUTTON_X = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
BUTTON_Y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# Globals for navigation
path_stack = []
current_items = []
selected_index = 0

# Load data
def load_data():
    with open("info.json", "r") as f:
        return json.load(f)

vault = load_data()

# Get current node from stack
def get_current_node():
    node = vault
    for key in path_stack:
        node = node[key]
    return node

# Update current list of keys/values
def update_items():
    global current_items
    node = get_current_node()
    if isinstance(node, dict):
        current_items = list(node.keys())
    else:
        current_items = [str(node)]  # leaf node value as single item

# Draw screen
def draw():
    display.set_pen(BLACK_PEN)
    display.clear()
    display.set_pen(display.create_pen(255, 255, 255))
    
    display.set_pen(WHITE_PEN if selected_index > 0 else GRAY_PEN)
    display.text("More", 0, 15, WIDTH, 2)
    display.set_pen(WHITE_PEN if selected_index < len(current_items) - 1 else GRAY_PEN)
    display.text("More", 0, 95, WIDTH, 2)
    display.set_pen(WHITE_PEN if isinstance(get_current_node(), dict) else GRAY_PEN)
    display.text("Select", 184, 15, WIDTH, 2)
    display.set_pen(WHITE_PEN if len(path_stack) > 0 else GRAY_PEN)
    display.text("Back", 200, 95, WIDTH, 2)

    display.set_pen(WHITE_PEN)

    if current_items:
        item = current_items[selected_index]
        width = display.measure_text(item, scale=3)
        display.text(item, (WIDTH - width) // 2, HEIGHT // 2 - 16, WIDTH, 3)  # Larger font size

    display.update()

# Button debouncer
def wait_for_button_release():
    while not (BUTTON_A.value() and BUTTON_B.value() and BUTTON_X.value() and BUTTON_Y.value()):
        time.sleep(0.01)

# Navigation loop
def main():
    global selected_index

    update_items()
    draw()

    while True:
        if not BUTTON_A.value():
            if selected_index > 0:
                selected_index -= 1
                draw()
            wait_for_button_release()

        elif not BUTTON_B.value():
            if selected_index < len(current_items) - 1:
                selected_index += 1 
                draw()
            wait_for_button_release()

        elif not BUTTON_X.value():
            node = get_current_node()
            key = current_items[selected_index]
            if isinstance(node, dict):
                path_stack.append(key)
                selected_index = 0
                update_items()
                draw()
            wait_for_button_release()

        elif not BUTTON_Y.value():
            if path_stack:
                previous_key = path_stack.pop()
                update_items()
                selected_index = current_items.index(previous_key)
                draw()
            wait_for_button_release()

        time.sleep(0.05)

main()
