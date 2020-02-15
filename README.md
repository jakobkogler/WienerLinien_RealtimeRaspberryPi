# WienerLinien_RealtimeRaspberryPi

As the name suggest, this project contains a script that displays realtime departure times from the Wiener Linien on a Raspberry Pi with an [Adafruit 16x2 Character LCD + Keypad Kit](https://www.adafruit.com/product/1109).

This project was inspired by the project [WL-Monitor-Pi](https://github.com/mabe-at/WL-Monitor-Pi), but was designed with more features in mind.

Especially it supports:

  - Interactive menu (via asyncio)
  - Multiple stations (switch the displayed station using Up/Down buttons)
  - Showing the next few arrivals times
  - Slow-Mode and Fast-Mode (switch request interval from 30 seconds to 5 seconds via the Select button)
  - Showing arrival in seconds, if possible.

## Installation

The project uses [Poetry](https://python-poetry.org/) for dependency management.

```
poetry env use 3.7
poetry install
```

Afterwards you can run the script for some given RBL numbers (find them [here](https://till.mabe.at/rbl/) or at [data.gv.at](https://www.data.gv.at/katalog/dataset/stadt-wien_wienerlinienechtzeitdaten)) with:

```
poetry run realtime RLB [RBL ...]
```

## Testing

Run the unit-tests with:

```
poetry run pytest --mypy --black
```
