# Vocabulary Builder

A flashcard-style vocabulary gadget for learning and reviewing English words.

![](IMG_0978.JPEG)  
![](IMG_0979.JPEG)  
![](IMG_0980.JPEG)

## Features

- Browse word-definition pairs one at a time
- Mark entries as known
- Human-editable JSON data format (`vocab.json`)
- Instant-on, zero-dependency design
- Optional LiPo battery support with charge status display

## Hardware

- [Pimoroni Pico LiPo](https://shop.pimoroni.com/products/pico-lipo-16mb)  
  or compatible RP2040 board with:
  - Display (e.g. Pico Display or Inky)
  - Three buttons

## File Format

Vocabulary is stored in a `vocab.json` file. Each entry is a dictionary with a `word`, a `definition`, and an optional `known` flag.

```json
[
  { "word": "eloquent", "definition": "fluent or persuasive in speaking or writing" },
  { "word": "succinct", "definition": "briefly and clearly expressed" }
]
