from wiener_linien_lib import WienerLinien, DepartureInfos
import argparse
from typing import List
import time
import board  # type: ignore
import busio  # type: ignore
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd  # type: ignore


class LCD:
    def __init__(self):
        lcd_columns = 16
        lcd_rows = 2

        i2c = busio.I2C(board.SCL, board.SDA)

        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
        self.lcd.clear()
        self.lcd.color = [100, 0, 0]

    def show_departures(self, departures: DepartureInfos) -> None:
        lst : List[str] = []
        for name, countdowns in departures.items():
            countdown_str = ' '.join(str(value) for value in countdowns)
            string = f'''{name:.6}: {countdown_str}'''[:16]
            string = f'''{name}: {countdown_str}'''
            lst.append(string)
        lst = lst[:2]

        self.lcd.clear()
        self.lcd.message = '\n'.join(lst)
        
        for _ in range(15):
            time.sleep(1)
            self.lcd.move_left()


def _main(apikey: str, RBL_numbers: List[int]):
    wiener_linien = WienerLinien(apikey)
    lcd = LCD()

    while True:
        data = wiener_linien.get_departures(RBL_numbers)
        lcd.show_departures(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display real time information of Wiener Linien station on a Raspberry Pi')
    parser.add_argument('apikey', help='Key for the Wiener Linien API')
    parser.add_argument('RBL', type=int, nargs='+', help='RBL numbers for the stations')
    args = parser.parse_args()
    _main(args.apikey, args.RBL)
