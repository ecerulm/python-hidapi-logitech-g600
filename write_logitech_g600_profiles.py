#!/usr/bin/env python3
import hid
import sys
import time


class LogitechG600Profile:
    LED_EFFECT_SOLID: int = (
        0x00  # https://github.com/libratbag/libratbag/blob/8444ceb638b19c3fbeb073a5cd29f17c6d34dd07/src/driver-logitech-g600.c#L51-L53
    )
    LED_EFFECT_BREATHE: int = 0x01
    LED_EFFECT_LED_CYCLE: int = 0x02

    LEFT_CTRL: int = 0x01
    LEFT_SHIFT: int = 0x02
    LEFT_ALT: int = 0x04
    LEFT_META: int = 0x08
    LEFT_GUI: int = 0x08
    LEFT_CMD: int = 0x08
    RIGHT_CTRL: int = 0x10
    RIGHT_SHIFT: int = 0x20
    RIGHT_ALT: int = 0x40
    RIGHT_META: int = 0x80
    RIGHT_GUI: int = 0x80
    RIGHT_CMD: int = 0x80

    HYPER = LEFT_CTRL | LEFT_SHIFT | LEFT_ALT | LEFT_GUI
    MEH = LEFT_CTRL | LEFT_SHIFT | LEFT_ALT

    NAME_TO_CODE_MODIFIER_KEY = {
        "BUTTON_1": (0x01, 0x00, 0x00),
        "BUTTON_2": (0x02, 0x00, 0x00),
        "BUTTON_3": (0x03, 0x00, 0x00),
        "BUTTON_4": (0x04, 0x00, 0x00),
        "BUTTON_5": (0x05, 0x00, 0x00),
        "RESOLUTION_UP": (0x11, 0x00, 0x00),
        "RESOLUTION_DOWN": (0x12, 0x00, 0x00),
        "RESOLUTION_CYCLE_UP": (0x13, 0x00, 0x00),
        "PROFILE_CYCLE_UP": (0x14, 0x00, 0x00),
        "RESOLUTION_ALTERNATE": (0x15, 0x00, 0x00),
        "SECOND_MODE": (0x17, 0x00, 0x00),
        "KEY_1": (
            0x00,
            0x00,
            0x1E,
        ),  # From HID Usage Table for USB / https://usb.org/document-library/hid-usage-tables-15
        "HYPER+1": (0x00, HYPER, 0x1E),
        "MEH+1": (0x00, MEH, 0x1E),
        "KEY_2": (0x00, 0x00, 0x1F),
        "HYPER+2": (0x00, HYPER, 0x1F),
        "MEH+2": (0x00, MEH, 0x1F),
        "KEY_3": (0x00, 0x00, 0x20),
        "HYPER+3": (0x00, HYPER, 0x20),
        "MEH+3": (0x00, MEH, 0x20),
        "KEY_4": (0x00, 0x00, 0x21),
        "HYPER+4": (0x00, HYPER, 0x21),
        "MEH+4": (0x00, MEH, 0x21),
        "KEY_5": (0x00, 0x00, 0x22),
        "HYPER+5": (0x00, HYPER, 0x22),
        "MEH+5": (0x00, MEH, 0x22),
        "KEY_6": (0x00, 0x00, 0x23),
        "HYPER+6": (0x00, HYPER, 0x23),
        "MEH+6": (0x00, MEH, 0x23),
        "KEY_7": (0x00, 0x00, 0x24),
        "HYPER+7": (0x00, HYPER, 0x24),
        "MEH+7": (0x00, MEH, 0x24),
        "KEY_8": (0x00, 0x00, 0x25),
        "HYPER+8": (0x00, HYPER, 0x25),
        "MEH+8": (0x00, MEH, 0x25),
        "KEY_9": (0x00, 0x00, 0x26),
        "HYPER+9": (0x00, HYPER, 0x26),
        "MEH+9": (0x00, MEH, 0x26),
        "KEY_0": (0x00, 0x00, 0x27),
        "HYPER+0": (0x00, HYPER, 0x27),
        "MEH+0": (0x00, MEH, 0x27),
        "KEY_MINUS": (0x00, 0x00, 0x2D),
        "HYPER+MINUS": (0x00, HYPER, 0x2D),
        "MEH+MINUS": (0x00, MEH, 0x2D),
        "KEY_EQUAL": (0x00, 0x00, 0x2E),
        "HYPER+EQUAL": (0x00, HYPER, 0x2E),
        "MEH+EQUAL": (0x00, MEH, 0x2E),
        "KEY_MUTE": (0x00, 0x00, 0x7F),
        "KEY_VOLUME_UP": (0x00, 0x00, 0x80),
        "KEY_VOLUME_DOWN": (0x00, 0x00, 0x81),
        # There is no Media Play/Pause key in the HID Usage Table for USB  / Keyboard/Keypad Page (0x07)
        "KEY_A": (0x00, 0x00, 0x04),
        "KEY_B": (0x00, 0x00, 0x05),
        "SHIFT+B": (0x00, LEFT_SHIFT, 0x05),
        "CMD+B": (0x00, LEFT_CMD, 0x05),
        "KEY_C": (0x00, 0x00, 0x06),
        "SHIFT+C": (0x00, LEFT_SHIFT, 0x06),
        "CMD+C": (0x00, LEFT_CMD, 0x06),
        "KEY_V": (0x00, 0x00, 0x19),
        "CMD+V": (0x00, LEFT_CMD, 0x19),
        "CMD+SHIFT+V": (0x00, LEFT_CMD | LEFT_SHIFT, 0x19),
    }
    BUTTON_ORDER = {
        "G1": 0,
        "LEFT_CLICK": 0,
        "G2": 1,
        "RIGHT_CLICK": 1,
        "G3": 2,
        "WHEEL_CLICK": 2,
        "G4": 3,
        "WHEEL_LEFT": 3,
        "G5": 4,
        "WHEEL_RIGHT": 4,
        "G6": 5,
        "G7": 6,
        "G8": 7,
        "G9": 8,
        "G10": 9,
        "G11": 10,
        "G12": 11,
        "G13": 12,
        "G14": 13,
        "G15": 14,
        "G16": 15,
        "G17": 16,
        "G18": 17,
        "G19": 18,
        "G20": 19,
    }

    profile_number: int
    report_id: int
    led_red: int
    led_green: int
    led_blue: int

    def __init__(self, profile_number: int):
        self.profile_number = profile_number
        self.report_id = 0xF3 + (profile_number)
        if self.report_id not in [0xF3, 0xF4, 0xF5]:
            raise ValueError("Invalid profile number")
        self.led_red = 0
        self.led_green = 0
        self.led_blue = 0
        self._gshift_color = (0, 0, 0)
        self.led_effect = LogitechG600Profile.LED_EFFECT_SOLID
        self.led_duration = 0
        self._frequency = 125
        self._dpi_shift = 0x04
        self._dpi_default = 2 # 1200 dpi
        self._dpis = [3200 // 50, 2000 // 50, 1200 // 50, 400 // 50]
        self._buttons = []

        for i in range(20):
            self._buttons.append((0, 0, 0x1E))

        # default mappings from https://www.logitech.com/assets/44964/3/g600-mmo-gaming-mouse-quickstart-guide.pdf
        self.set_button("G1", "BUTTON_1")  # button1 - left click
        self.set_button("G2", "BUTTON_2")  # button2 - right click

        self.set_button("G3", "BUTTON_3")  # button3 - wheel click
        self.set_button("G4", "BUTTON_4")  # button4 - wheel left
        self.set_button("G5", "BUTTON_5")  # button5 - wheel right

        self.set_button("G6", "SECOND_MODE")  # SECOND_MODE / G-Shift / 0x17

        # self._buttons[self.BUTTON_ORDER["G7"]] = (0, self.LEFT_SHIFT, 0x05)
        self.set_button("G7", value=(0, self.LEFT_SHIFT, 0x05))  # shift - B
        self.set_button("G8", "PROFILE_CYCLE_UP")  # profile cycle up - 0x14

        for i in range(9, 19):
            self.set_button("G%d" % i, value=(0, 0, 0x1E + i - 9))

        self.set_button("g19", "KEY_MINUS")
        self.set_button("g20", "KEY_EQUAL")

        self._gshift_buttons = self._buttons.copy()
        for i in range(9, 21):
            # Copy the G9 to G20 buttons to the G-Shift buttons adding LEFT_CTRL modifier
            code, _, key = self.get_button("G%d" % i)
            self.set_gshift_button("G%d" % i, value=(code, self.LEFT_CTRL, key))

    def get_led_effect_string(self):
        if self.led_effect == LogitechG600Profile.LED_EFFECT_BREATHE:
            return "Breathing"
        if self.led_effect == LogitechG600Profile.LED_EFFECT_LED_CYCLE:
            return "LED Cycle"
        if self.led_effect == LogitechG600Profile.LED_EFFECT_SOLID:
            return "LED Solid"
        else:
            return "Unknown"

    def feature_report(self):
        to_return = []
        to_return.append(self.report_id)
        to_return.append(self.led_red)
        to_return.append(self.led_green)
        to_return.append(self.led_blue)
        to_return.append(self.led_effect)
        to_return.append(self.led_duration)
        to_return.extend([0 for _ in range(5)])
        to_return.append(self.frequency_to_byte())
        to_return.append(self._dpi_shift)
        to_return.append(self._dpi_default)
        to_return.extend(self._dpis)
        to_return.extend([0 for _ in range(6)])
        to_return.append(2)
        to_return.extend([0 for _ in range(6)])

        for button in self._buttons:
            to_return.extend(button)

        # to_return.extend([self.led_red, self.led_green, self.led_blue])
        to_return.extend(self.gshift_color)

        for button in self._gshift_buttons:
            to_return.extend(button)
        if len(to_return) != 154:
            raise ValueError("Invalid feature report length %d" % len(to_return))

        return to_return

    def frequency_to_byte(self):
        if self.frequency == 1000:
            return 0
        elif self.frequency == 500:
            return 1
        elif self.frequency == 250:
            return 3
        elif self.frequency == 125:
            return 7
        else:
            raise ValueError("Invalid frequency %d hz" % self.frequency)

    @property
    def frequency(self) -> int:
        return self._frequency

    @frequency.setter
    def frequency(self, f: int) -> int:
        if f not in [125, 250, 500, 1000]:
            raise ValueError("Invalid frequency")
        self._frequency = f

    @property
    def dpi_shift(self) -> int:
        return self._dpi_shift * 50

    @dpi_shift.setter
    def dpi_shift(self, d: int) -> None:
        if d not in range(200, 8201, 50):
            raise ValueError("Invalid DPI shift")
        self._dpi_shift = d // 50

    @property
    def dpi_default(self) -> int:
        return self._dpis[self._dpi_default] * 50

    @dpi_default.setter
    def dpi_default(self, d: int) -> None:
        d = d // 50
        if d not in self._dpis:
            raise ValueError(
                "Invalid DPI default %d, not in %s"
                % (d * 50, [x * 50 for x in self._dpis])
            )
        self._dpi_default = self._dpis.index(d)

    @property
    def dpi1(self) -> int:
        return self._dpis[0] * 50

    @dpi1.setter
    def dpi1(self, d: int) -> None:
        if d not in range(200, 8201, 50):
            raise ValueError("Invalid DPI1 value %d" % d)
        self._dpis[0] = d // 50

    @property
    def dpi2(self) -> int:
        return self._dpis[1] * 50

    @dpi2.setter
    def dpi2(self, d: int) -> None:
        if d not in range(200, 8201, 50):
            raise ValueError("Invalid DPI2 value %d" % d)
        self._dpis[1] = d // 50

    @property
    def dpi3(self) -> int:
        return self._dpis[2] * 50

    @dpi3.setter
    def dpi3(self, d: int) -> None:
        if d not in range(200, 8201, 50):
            raise ValueError("Invalid DPI3 value %d" % d)
        self._dpis[2] = d // 50

    @property
    def dpi4(self) -> int:
        return self._dpis[3] * 50

    @dpi4.setter
    def dpi4(self, d: int) -> None:
        if d not in range(200, 8201, 50):
            raise ValueError("Invalid DPI4 value %d" % d)
        self._dpis[3] = d // 50

    @property
    def left_click(self) -> tuple:
        return self._left_click

    @left_click.setter
    def left_click(self, value: str) -> None:
        if value not in LogitechG600Profile.NAME_TO_CODE_MODIFIER_KEY:
            raise ValueError("Invalid left click value %s" % value)
        self._left_click = LogitechG600Profile.NAME_TO_CODE_MODIFIER_KEY[value]

    def get_button(self, button_name: str) -> tuple:
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError("Invalid button name %s" % button_name)
        return self._buttons[index]

    def set_button(self, button_name: str, value: tuple[int, int, int] | str) -> None:
        if isinstance(value, str):
            value = self.NAME_TO_CODE_MODIFIER_KEY[value]
        code, modifier, key = value
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError("Invalid button name %s" % button_name)
        self._buttons[index] = (code, modifier, key)

    def get_gshift_button(self, button_name: str) -> tuple:
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError("Invalid button name %s" % button_name)
        return self._gshift_buttons[index]

    def set_gshift_button(
        self, button_name: str, value: tuple[int, int, int] | str
    ) -> None:
        if isinstance(value, str):
            value = self.NAME_TO_CODE_MODIFIER_KEY[value]
        code, modifier, key = value
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError("Invalid button name %s" % button_name)
        self._gshift_buttons[index] = (code, modifier, key)

    @property
    def gshift_color(self) -> tuple:
        return self._gshift_color

    @gshift_color.setter
    def gshift_color(self, color: tuple) -> None:
        if len(color) != 3:
            raise ValueError("Invalid color %s" % color)
        for c in color:
            if c not in range(256):
                raise ValueError("Invalid value %s in color %s" % (c, color))
        self._gshift_color = color

    @property
    def color(self) -> tuple:
        return (self.led_red, self.led_green, self.led_blue)

    @color.setter
    def color(self, color: tuple) -> None:
        if len(color) != 3:
            raise ValueError("Invalid color %s" % color)
        for c in color:
            if c not in range(256):
                raise ValueError("Invalid value %s in color %s" % (c, color))
        self.led_red, self.led_green, self.led_blue = color

    def _open_device(self) -> hid.device:
        print("Opening device vendor 0x046D (Logitech) product 0xC24A (G600)")
        try:
            h = hid.device()
            h.open(0x046D, 0xC24A)  # Logitech:0x046d G600:0xC24A
            print("Manufacturer: %s" % h.get_manufacturer_string())
            print("Product: %s" % h.get_product_string())
            print("Serial No: %s" % h.get_serial_number_string())
            time.sleep(
                2
            )  # wait until device is ready, other profile writes may be in progress/pending
            return h
        except OSError as e:
            print("error opening device vendor 0x046D (Logitech) product 0xC24A (G600)")
            print("Close Logitech GHUB, Karabiner, Hammerspoon, etc.")
            print(
                "The terminal application must have input monitoring permission in System Preferences > Security & Privacy > Privacy > Input Monitoring"
            )
            print(e)
            sys.exit()

    def write_to_device(self):
        h = self._open_device()

        print("writing profile", self.profile_number)
        rc = h.send_feature_report(self.feature_report())
        if rc == -1:
            print(
                "error writing profile %d. Close Logitech GHUB, Karabiner, Hammerspoon, etc."
                % self.profile_number
            )
            sys.exit()
        print("Successfully wrote profile %d (%d bytes)" % (self.profile_number, rc))
        h.close()

    def set_as_active_profile(self):
        print("Set profile %d as active profile" % self.profile_number)
        h = self._open_device()
        h.send_feature_report([0xF0, 0x80 | (self.profile_number << 4), 0x00, 0x00])
        # 0xF0: the report id to set the active profile
        # - [0xF0, 0x80, 0x00, 0x00] for profile 1 (0x80 | (index << 4)) index: 0
        # - [0xF0, 0x90, 0x00, 0x00] for profile 2 (0x80 | (index << 4)) index: 1
        # - [0xF0, 0xa0, 0x00, 0x00] for profile 3 (0x80 | (index << 4)) index: 2
        h.close()

    def __repr__(self):
        return "LogitechG600Profile(%d)" % self.profile_number

    def __str__(self):
        to_return = []
        to_return.append("Profile %d" % self.profile_number)
        to_return.append(
            "RGB (%d,%d,%d)" % (self.led_red, self.led_green, self.led_blue)
        )
        to_return.append("LED effect (%s)" % (self.get_led_effect_string()))
        to_return.append("LED duration (%d seconds)" % (self.led_duration))
        to_return.append(
            "Frequency %s Hz (0x%02X)" % (self.frequency, self.frequency_to_byte())
        )
        to_return.append(
            "DPI Shift %4d dpi (0x%02X)" % (self.dpi_shift, self._dpi_shift)
        )
        to_return.append(
            "DPI Default %4ddpi (0x%02X)" % (self.dpi_default, self._dpi_default)
        )
        to_return.append("DPI1 %4ddpi (0x%02X)" % (self.dpi1, self._dpis[0]))
        to_return.append("DPI2 %4ddpi (0x%02X)" % (self.dpi2, self._dpis[1]))
        to_return.append("DPI3 %4ddpi (0x%02X)" % (self.dpi3, self._dpis[2]))
        to_return.append("DPI4 %4ddpi (0x%02X)" % (self.dpi4, self._dpis[3]))
        to_return.append(
            "Left Click    G1 0x%02X 0x%02X 0x%02X" % self.get_button("LEFT_CLICK")
        )
        to_return.append(
            "Right Click   G2 0x%02X 0x%02X 0x%02X" % self.get_button("RIGHT_CLICK")
        )
        to_return.append(
            "              G3 0x%02X 0x%02X 0x%02X" % self.get_button("g3")
        )
        to_return.append(
            "              G4 0x%02X 0x%02X 0x%02X" % self.get_button("g4")
        )
        to_return.append(
            "              G5 0x%02X 0x%02X 0x%02X" % self.get_button("g5")
        )
        to_return.append(
            "              G6 0x%02X 0x%02X 0x%02X" % self.get_button("g6")
        )
        to_return.append(
            "              G7 0x%02X 0x%02X 0x%02X" % self.get_button("g7")
        )
        to_return.append(
            "              G8 0x%02X 0x%02X 0x%02X" % self.get_button("g8")
        )
        to_return.append(
            "              G9 0x%02X 0x%02X 0x%02X" % self.get_button("g9")
        )
        to_return.append(
            "             G10 0x%02X 0x%02X 0x%02X" % self.get_button("g10")
        )
        to_return.append(
            "             G11 0x%02X 0x%02X 0x%02X" % self.get_button("g11")
        )
        to_return.append(
            "             G12 0x%02X 0x%02X 0x%02X" % self.get_button("g12")
        )
        to_return.append(
            "             G13 0x%02X 0x%02X 0x%02X" % self.get_button("g13")
        )
        to_return.append(
            "             G14 0x%02X 0x%02X 0x%02X" % self.get_button("g14")
        )
        to_return.append(
            "             G15 0x%02X 0x%02X 0x%02X" % self.get_button("g15")
        )
        to_return.append(
            "             G16 0x%02X 0x%02X 0x%02X" % self.get_button("g16")
        )
        to_return.append(
            "             G17 0x%02X 0x%02X 0x%02X" % self.get_button("g17")
        )
        to_return.append(
            "             G18 0x%02X 0x%02X 0x%02X" % self.get_button("g18")
        )
        to_return.append(
            "             G19 0x%02X 0x%02X 0x%02X" % self.get_button("g19")
        )
        to_return.append(
            "             G20 0x%02X 0x%02X 0x%02X" % self.get_button("g20")
        )
        to_return.append("G-Shift color %s" % (self.gshift_color,))
        to_return.append(
            "Left Click    G1 0x%02X 0x%02X 0x%02X"
            % self.get_gshift_button("LEFT_CLICK")
        )
        to_return.append(
            "Right Click   G2 0x%02X 0x%02X 0x%02X"
            % self.get_gshift_button("RIGHT_CLICK")
        )
        to_return.append(
            "              G3 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g3")
        )
        to_return.append(
            "              G4 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g4")
        )
        to_return.append(
            "              G5 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g5")
        )
        to_return.append(
            "              G6 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g6")
        )
        to_return.append(
            "              G7 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g7")
        )
        to_return.append(
            "              G8 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g8")
        )
        to_return.append(
            "              G9 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g9")
        )
        to_return.append(
            "             G10 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g10")
        )
        to_return.append(
            "             G11 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g11")
        )
        to_return.append(
            "             G12 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g12")
        )
        to_return.append(
            "             G13 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g13")
        )
        to_return.append(
            "             G14 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g14")
        )
        to_return.append(
            "             G15 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g15")
        )
        to_return.append(
            "             G16 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g16")
        )
        to_return.append(
            "             G17 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g17")
        )
        to_return.append(
            "             G18 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g18")
        )
        to_return.append(
            "             G19 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g19")
        )
        to_return.append(
            "             G20 0x%02X 0x%02X 0x%02X" % self.get_gshift_button("g20")
        )
        return "\n".join(to_return)


profile0 = LogitechG600Profile(0)
profile0.color = (255, 0, 0)
profile0.gshift_color = (0, 255, 255)
profile0.frequency = 125

profile0.set_button("g4", value=(0, 0, 0x81))  # keyboard volume down
profile0.set_button("g5", value=(0, 0, 0x80))  # keyboard volume up
profile0.set_button("g7", value="RESOLUTION_CYCLE_UP")  # DPI cycle
profile0.set_button("g8", value="PROFILE_CYCLE_UP")  # profile cycle up
profile0.set_button("g9", value="HYPER+1")  # hyper + 1 / KM screencapture -ic
profile0.set_button("g10", value="CMD+C")  # Cmd + C (copy)
profile0.set_button("g11", value="CMD+SHIFT+V")  # KM Smart Paste
profile0.set_button("g12", value="HYPER+4")  # hyper + 4
profile0.set_button("g13", value="HYPER+5")  # hyper + 5
profile0.set_button("g14", value="HYPER+6")  # hyper + 6
profile0.set_button("g15", value="HYPER+7")  # hyper + 7
profile0.set_button("g16", value="HYPER+8")  # hyper + 8
profile0.set_button("g17", value="HYPER+9")  # hyper + 9
profile0.set_button("g18", value="HYPER+0")  # hyper + 0
profile0.set_button("g19", value="HYPER+MINUS")  # hyper + -
profile0.set_button("g20", value="HYPER+EQUAL")  # hyper + =
profile0.set_gshift_button("g9", value="MEH+1")  # meh + 1
profile0.set_gshift_button("g10", value="CMD+B")  # Cmd + b (bold)
profile0.set_gshift_button("g11", value="MEH+3")  # meh + 3
profile0.set_gshift_button("g12", value="MEH+4")  # meh + 4
profile0.set_gshift_button("g13", value="MEH+5")  # meh + 5
profile0.set_gshift_button("g14", value="MEH+6")  # meh + 6
profile0.set_gshift_button("g15", value="MEH+7")  # meh + 7
profile0.set_gshift_button("g16", value="MEH+8")  # meh + 8
profile0.set_gshift_button("g17", value="MEH+9")  # meh + 9
profile0.set_gshift_button("g18", value="MEH+0")  # meh + 0
profile0.set_gshift_button("g19", value="MEH+MINUS")  # meh + -
profile0.set_gshift_button("g20", value="MEH+EQUAL")  # meh + =
print(profile0)
print(profile0.feature_report())


profile1 = LogitechG600Profile(1)
profile1.color = (0, 255, 0)
profile1.gshift_color = (255, 1, 255)

profile2 = LogitechG600Profile(2)
profile2.color = (0, 0, 255)
profile2.gshift_color = (255, 255, 0)


profile0.write_to_device()
profile0.set_as_active_profile()
profile1.write_to_device()
# profile1.set_as_active_profile()
profile2.write_to_device()
# profile2.set_as_active_profile()


# https://trezor.github.io/cython-hidapi/api.html#hid.device.SEND_FEATURE_REPORT
