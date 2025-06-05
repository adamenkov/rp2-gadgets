# Raspberry Pi Pico Gadgets

A collection of small, self-contained MicroPython gadgets designed for the [Pimoroni Pico LiPo](https://shop.pimoroni.com/products/pico-lipo-16mb) and related RP2040 boards with displays and battery support. Each gadget has a single use case, optimized for quick startup, intuitive button navigation, and minimal dependencies.

## Gadgets

### 🔐 Password Keeper

Securely stores passwords, PINs, and keys in a local JSON file. Designed for offline use — no connectivity or syncing required (or desired).

- View one entry at a time
- Scroll with buttons
- Data is human-editable (JSON format)
- Optional LiPo battery support with charge status display

### 🧠 Vocabulary Builder

A flashcard-style tool for learning English vocabulary.

- Browse and review word-definition pairs
- Mark entries as known
- Easily editable JSON data format
- Instant-on with no loading delays

## Hardware Requirements

- [Pimoroni Pico LiPo](https://shop.pimoroni.com/products/pico-lipo-16mb)
- [Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack)
- [Pico Inky Pack](https://shop.pimoroni.com/products/pico-inky-pack)
- [LiPo battery](https://www.waveshare.com/pico-ups-b.htm) (optional, for portability)

## Getting Started

1. Flash your Pico with [official MicroPython firmware](https://micropython.org/download/).
2. Clone this repo:
   ```bash
   git clone https://github.com/adamenkov/rp2-gadgets.git
   ```
3. Use Thonny.
