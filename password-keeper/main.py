import json
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
import pimoroni
from machine import ADC, Pin
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

vsys = ADC(Pin(29))                 # reads the system input voltage
charging_pin = Pin(24, Pin.IN)          # reading GP24 tells us whether or not USB power is connected
conversion_factor = 3 * 3.3 / 65535

full_battery = 4.2                  # reference voltages for a full/empty battery, in volts
empty_battery = 2.8                 # the values could vary by battery size/manufacturer so you might need to adjust them
mid_battery = (empty_battery + full_battery) / 2

RED    = (200,   0,   0)
YELLOW = (200, 200,   0)
GREEN  = (  0, 200,   0)

def read_battery_volts_percentage():
    # convert the raw ADC read into a voltage, and then a percentage
    voltage = vsys.read_u16() * conversion_factor
    percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
    if percentage > 100:
        percentage = 100
    return voltage, percentage

def lerp(color1, color2, t):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return int(r1 * (1 - t) + r2 * t), int(g1 * (1 - t) + g2 * t), int(b1 * (1 - t) + b2 * t)

def battery_color(percentage):
    if percentage < 50:
        return lerp(RED, YELLOW, 2 * percentage / 100)
    else:
        return lerp(YELLOW, GREEN, 2 * (percentage - 50) / 100)
    
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
    display.set_pen(WHITE_PEN)
    
    display.set_pen(WHITE_PEN if selected_index > 0 else GRAY_PEN)
    display.text("Up", 0, 15, WIDTH, 2)
    display.set_pen(WHITE_PEN if selected_index < len(current_items) - 1 else GRAY_PEN)
    display.text("Down", 0, 95, WIDTH, 2)
    display.set_pen(WHITE_PEN if isinstance(get_current_node(), dict) else GRAY_PEN)
    display.text("View", 200, 15, WIDTH, 2)
    display.set_pen(WHITE_PEN if len(path_stack) > 0 else GRAY_PEN)
    display.text("Back", 200, 95, WIDTH, 2)

    voltage, percentage = read_battery_volts_percentage()
    charging = " (charging)" if charging_pin() else ""
    
    color = battery_color(percentage)
    pen = display.create_pen(*color)
    display.set_pen(pen)

    battery_text = f"Bat: {voltage:.1f}V/{int(percentage)}%{charging}"
    width = display.measure_text(battery_text, scale=2)
    display.text(battery_text, (WIDTH - width) // 2, 115, WIDTH, 2)

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
        draw()
        
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

machine.freq(48_000_000)

main()
