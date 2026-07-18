from machine import RTC
from micropython import const
import ntptime
from presto import Presto
from time import sleep, sleep_ms, ticks_diff, ticks_ms, gmtime, time
from touch import Button


HEADER_HEIGHT = const(20)
FOOTER_HEIGHT = const(20)
FONT_HEIGHT = const(8)

LOOP_DELAY_MS = const(10)
CLOCK_CHECK_MS = const(500)

MARGIN = const(5)
DETAIL_TITLE_SCALE = const(3)

DAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class MenuItem:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        foreground,
        background,
        title,
        hint,
    ):
        self.button = Button(x, y, width, height)
        self.foreground = foreground
        self.background = background
        self.title = title
        self.hint = hint


presto = Presto()
display = presto.display
touch = presto.touch
rtc = RTC()

WIDTH, HEIGHT = display.get_bounds()

CONTENT_Y = HEADER_HEIGHT
CONTENT_HEIGHT = HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT
CELL_WIDTH = WIDTH // 2
CELL_HEIGHT = CONTENT_HEIGHT // 2

BLACK = display.create_pen(0, 0, 0)
GRAY = display.create_pen(30, 30, 30)
BLUE = display.create_pen(0, 0, 127)
RED = display.create_pen(127, 0, 0)
CYAN = display.create_pen(0, 127, 127)
YELLOW = display.create_pen(127, 127, 0)
WHITE = display.create_pen(127, 127, 127)

# Clear the screen before the network call is made
display.set_pen(BLACK)
display.clear()
presto.update()

def show_message(text):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()

show_message("Fetching current time...")

try:
    wifi = presto.connect()
except ValueError as e:
    while True:
        show_message(e)
except ImportError as e:
    while True:
        show_message(e)

# Set the correct time using the NTP service.
try:
    ntptime.settime()
except OSError:
    while True:
        show_message("Unable to get time.\n\nCheck your network\nand try again.")

UTC_OFFSET_HOURS = const(-5)  # Change to -6 in winter

def local_datetime():
    local = gmtime(time() + UTC_OFFSET_HOURS * 60 * 60)
    year, month, day, hour, minute, second, weekday, _ = local
    return year, month, day, weekday, hour, minute, second, 0

MENU = (
    MenuItem(
        0,
        CONTENT_Y,
        CELL_WIDTH,
        CELL_HEIGHT,
        WHITE,
        BLACK,
        "sleep",
        "sleep well",
    ),
    MenuItem(
        CELL_WIDTH,
        CONTENT_Y,
        WIDTH - CELL_WIDTH,
        CELL_HEIGHT,
        BLACK,
        YELLOW,
        "work",
        "work hard\nplay hard",
    ),
    MenuItem(
        0,
        CONTENT_Y + CELL_HEIGHT,
        CELL_WIDTH,
        CONTENT_HEIGHT - CELL_HEIGHT,
        YELLOW,
        RED,
        "gym",
        "exercise!",
    ),
    MenuItem(
        CELL_WIDTH,
        CONTENT_Y + CELL_HEIGHT,
        WIDTH - CELL_WIDTH,
        CONTENT_HEIGHT - CELL_HEIGHT,
        BLUE,
        CYAN,
        "research",
        "do your research",
    ),
)


def draw_centered(text, bounds):
    x, y, width, height = bounds
    text_width = display.measure_text(text)

    text_x = x + (width - text_width) // 2
    text_y = y + (height - FONT_HEIGHT) // 2

    display.text(text, text_x, text_y)


def draw_grid():
    for item in MENU:
        display.set_pen(item.background)
        display.rectangle(*item.button.bounds)

        display.set_pen(item.foreground)
        draw_centered(item.title, item.button.bounds)


def draw_detail(item):
    display.set_pen(item.background)
    display.rectangle(0, CONTENT_Y, WIDTH, CONTENT_HEIGHT)

    display.set_pen(item.foreground)
    display.text(
        item.title,
        MARGIN,
        CONTENT_Y + MARGIN,
        WIDTH - 2 * MARGIN,
        DETAIL_TITLE_SCALE,
    )
    display.text(item.hint, MARGIN, CONTENT_Y + 40)


def draw_status(datetime_tuple):
    year, month, day, weekday, hour, minute, _, _ = datetime_tuple

    display.set_pen(GRAY)
    display.rectangle(0, 0, WIDTH, HEADER_HEIGHT)
    display.rectangle(
        0,
        HEIGHT - FOOTER_HEIGHT,
        WIDTH,
        FOOTER_HEIGHT,
    )

    display.set_pen(WHITE)
    display.text(
        f"{hour:02d}:{minute:02d}   Top Priorities",
        MARGIN,
        3,
    )

    status = (
        f"{year:04d}-{month:02d}-{day:02d}   "
        f"{DAY_NAMES[weekday]}"
    )
    status_x = (WIDTH - display.measure_text(status)) // 2

    display.text(
        status,
        status_x,
        HEIGHT - FOOTER_HEIGHT + 3,
    )
    
draw_grid()

selected_item = None

current_datetime = local_datetime()
displayed_status = current_datetime[:6]
last_clock_check = ticks_ms()

draw_grid()
draw_status(current_datetime)
presto.update()

# presto.update() polls touch internally, so initialize this afterward.
touch_was_down = touch.state

while True:
    touch.poll()

    touch_is_down = touch.state
    touch_started = touch_is_down and not touch_was_down
    redraw = False

    if touch_started:
        if selected_item is None:
            for item in MENU:
                if item.button.is_pressed():
                    selected_item = item
                    draw_detail(item)
                    redraw = True
                    break
        else:
            selected_item = None
            draw_grid()
            redraw = True

    touch_was_down = touch_is_down

    now = ticks_ms()

    if ticks_diff(now, last_clock_check) >= CLOCK_CHECK_MS:
        last_clock_check = now
        current_datetime = local_datetime()
        status = current_datetime[:6]

        if status != displayed_status:
            displayed_status = status
            draw_status(current_datetime)
            redraw = True

    if redraw:
        presto.update()

    sleep_ms(LOOP_DELAY_MS)
