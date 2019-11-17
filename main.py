from wiener_linien_lib import WienerLinien, DepartureInfos
import argparse
from typing import List
import asyncio
import board  # type: ignore
import busio  # type: ignore
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd  # type: ignore


def replace_umlaute(s: str):
    s = s.replace("Ä", "Ae")
    s = s.replace("Ö", "Oe")
    s = s.replace("Ü", "Ue")
    s = s.replace("ä", "ae")
    s = s.replace("ß", "ss")
    s = s.replace("ö", "oe")
    s = s.replace("ü", "ue")
    return s


class LCD:
    def __init__(self):
        lcd_columns = 16
        lcd_rows = 2

        i2c = busio.I2C(board.SCL, board.SDA)

        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
        self.lcd.clear()
        self.lcd.color = [100, 0, 0]

        self.departures = []
        self.current_station = 0
        self.request_update = False
        
    def update_departures(self, departures: DepartureInfos) -> None:
        message_before = self.station_string()
        self.departures = sorted(departures.items())
        message_after = self.station_string()
        if message_before != message_after:
            self.request_update = True

    def station_string(self):
        if self.departures:
            name, countdowns = self.departures[self.current_station % len(self.departures)]
            countdown_str = ' '.join(str(value) for value in countdowns)
            return replace_umlaute(f'''{name}\n{countdown_str:>16}''')
        return ""

    async def show_departures(self) -> None:
        while True:
            if self.request_update:
                message = self.station_string()
                print("set message")
                self.lcd.clear()
                self.lcd.message = message
                self.request_update = False
            await asyncio.sleep(0.1)

    async def handle_buttons(self):
        while True:
            if self.lcd.down_button:
                print("Down")
                self.current_station += 1
                self.request_update = True
                await asyncio.sleep(0.5)
            if self.lcd.up_button:
                print("Up")
                self.current_station -= 1
                self.request_update = True
                await asyncio.sleep(0.5)
            if self.lcd.left_button:
                print("Left")
                self.lcd.move_left()
                await asyncio.sleep(0.5)
            if self.lcd.right_button:
                print("Right")
                self.lcd.move_right()
                await asyncio.sleep(0.5)
            if self.lcd.select_button:
                print("Select")
                self.request_update = True
                await asyncio.sleep(0.5)
            await asyncio.sleep(0.1)


async def realtime_data_loop(apikey: str, RBL_numbers: List[int], lcd: LCD):
    wiener_linien = WienerLinien(apikey)
    while True:
        data = wiener_linien.get_departures(RBL_numbers)
        print(data)
        lcd.update_departures(data)
        await asyncio.sleep(30)


async def _main(apikey: str, RBL_numbers: List[int]):
    lcd = LCD()
    await asyncio.gather(
        realtime_data_loop(apikey, RBL_numbers, lcd),
        lcd.show_departures(),
        lcd.handle_buttons()
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display real time information of Wiener Linien station on a Raspberry Pi')
    parser.add_argument('apikey', help='Key for the Wiener Linien API')
    parser.add_argument('RBL', type=int, nargs='+', help='RBL numbers for the stations')
    args = parser.parse_args()
    asyncio.run(_main(args.apikey, args.RBL))
