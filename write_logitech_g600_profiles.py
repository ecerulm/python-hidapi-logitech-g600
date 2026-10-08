#!/usr/bin/env python3
import sys
import time

import hid
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogitechG600Profile:
    LED_EFFECT_SOLID: int = 0x00  # https://github.com/libratbag/libratbag/blob/8444ceb638b19c3fbeb073a5cd29f17c6d34dd07/src/driver-logitech-g600.c#L51-L53
    LED_EFFECT_BREATHE: int = 0x01
    LED_EFFECT_LED_CYCLE: int = 0x02

    # Modifiers. From HID 1.5 / Chapter 10. Keyboard/keypad page 0x07
    # E0 Keyboard LeftControl
    # E1 Keyboard LeftShift
    # E2 Keyboard LeftAlt
    # E3 Keyboard Left GUI
    # E4 Keyboard RightControl
    # E5 Keyboard LeftShift
    # E6 Keyboard LeftAlt
    # E7 Keyboard Left GUI

    LEFT_CTRL: int = 0x01  # This values are not from HID 1.5, it's a G600 thing
    LEFT_SHIFT: int = 0x02
    LEFT_ALT: int = 0x04
    LEFT_META: int = 0x08  #
    LEFT_GUI: int = 0x08  # LEFT_META, LEFT_GUI and LEFT_CMD are the same key
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
        "HYPER+1": (
            0x00,
            HYPER,
            0x1E,
        ),  # From HID usage table for USB, Chapter 10 Keyboard/Keypad page 0x07
        "MEH+1": (
            0x00,
            MEH,
            0x1E,
        ),  # From HID 1.5 / Chapter 10 Keyboard/Keypat page 0x07 / Keyboard 1 and !
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
        "CTRL+ALT+CMD+7": (0x00, LEFT_CTRL | LEFT_ALT | LEFT_CMD, 0x24),
        "KEY_8": (0x00, 0x00, 0x25),
        "HYPER+8": (0x00, HYPER, 0x25),
        "MEH+8": (0x00, MEH, 0x25),
        "KEY_9": (0x00, 0x00, 0x26),
        "HYPER+9": (0x00, HYPER, 0x26),
        "MEH+9": (0x00, MEH, 0x26),
        "KEY_0": (
            0x00,
            0x00,
            0x27,
        ),  # From HID 1.5 / Chapter 10 Keyboard/Keypad page 0x07 / Keyboard 0 and )
        "HYPER+0": (0x00, HYPER, 0x27),
        "MEH+0": (0x00, MEH, 0x27),  # 0x27
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
        # The Play/Pause (0xCD) and Play/Skip (0xCE) are part of Consumer Page 0x0C
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
        "CTRL+RIGHT": (
            0x00,
            LEFT_CTRL,
            0x4F,
        ),  # in HID UsageTable for USB / 4f -> Keyboard RightArrow
        "CTRL+LEFT": (
            0x00,
            LEFT_CTRL,
            0x50,
        ),  # in HID UsageTable for USB / 50 -> Keyboard LeftArrow
        "CTRL+CMD+SHIFT+4": (
            0x00,
            LEFT_CTRL | LEFT_CMD | LEFT_SHIFT,
            0x21,
        ),  # in HIG UsageTable for USB / 0x21 -> "4"
        "CMD+`": (
            0x00,
            LEFT_CMD,
            0x35,
        ),  # in HID Usage Table for USB / 35 -> Keyboard Grave Accent and Tilde
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
        self._dpi_default = 2  # 1200 dpi
        self._dpis = [3200 // 50, 2000 // 50, 1200 // 50, 400 // 50]
        self._buttons = []  # tuples (code, modifier, value)
        # code can be
        # 0x00 regular keyboard key from HID Usage Table 0x07 Keyboard usage
        # 0x01 button 1
        # 0x02 button 2
        # 0x03 button 3
        # 0x04 button 4
        # 0x05 button 5
        # 0x11 DPI resolution up
        # 0x12 DPI resolution down
        # 0x13 resolution cycle
        # 0x14 profile cycle
        # 0x15 resolution alternate
        # 0x17 second mode

        for _ in range(20):
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
        to_return.extend([0 for _ in range(6)])  # Fill with 6 zeroes
        to_return.append(2)
        to_return.extend([0 for _ in range(6)])  # Fill with 6 zeroes

        # Section with all the regular buttons (no G-shift)
        for button in self._buttons:
            to_return.extend(button)

        # to_return.extend([self.led_red, self.led_green, self.led_blue])
        to_return.extend(self.gshift_color)

        # Section with the G-shift buttons
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
    def frequency(self, f: int) -> None:
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

    def get_dpi(self, slot: int) -> int:
        """Return DPI for slot 1-4 in real dpi (already multiplied by 50)."""
        return self._dpis[slot - 1] * 50

    def set_dpi(self, slot: int, d: int) -> None:
        """Set DPI for slot 1-4. ``d`` is real dpi (200-8200, multiple of 50)."""
        if d not in range(200, 8201, 50):
            raise ValueError("Invalid DPI%d value %d" % (slot, d))
        self._dpis[slot - 1] = d // 50

    def get_button(self, button_name: str) -> tuple:
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError(f"Invalid button name {button_name}")
        return self._buttons[index]

    def set_button(self, button_name: str, value: tuple[int, int, int] | str) -> None:
        # (code, modifier, key)
        # code
        if isinstance(value, str):
            value = self.NAME_TO_CODE_MODIFIER_KEY[value]
        code, modifier, key = value
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError(f"Invalid button name {button_name}")
        self._buttons[index] = (code, modifier, key)

    def get_gshift_button(self, button_name: str) -> tuple:
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError(f"Invalid button name {button_name}")
        return self._gshift_buttons[index]

    def set_gshift_button(
        self, button_name: str, value: tuple[int, int, int] | str
    ) -> None:
        if isinstance(value, str):
            value = self.NAME_TO_CODE_MODIFIER_KEY[value]
        code, modifier, key = value
        index = self.BUTTON_ORDER.get(button_name.upper(), None)
        if index is None:
            raise ValueError(f"Invalid button name {button_name}")
        self._gshift_buttons[index] = (code, modifier, key)

    @property
    def gshift_color(self) -> tuple:
        return self._gshift_color

    @gshift_color.setter
    def gshift_color(self, color: tuple) -> None:
        if len(color) != 3:
            raise ValueError(f"Invalid color {color}")
        for c in color:
            if c not in range(256):
                raise ValueError(f"Invalid value {c} in color {color}")
        self._gshift_color = color

    @property
    def color(self) -> tuple:
        return (self.led_red, self.led_green, self.led_blue)

    @color.setter
    def color(self, color: tuple) -> None:
        if len(color) != 3:
            raise ValueError(f"Invalid color {color}")
        for c in color:
            if c not in range(256):
                raise ValueError(f"Invalid value {c} in color {color}")
        self.led_red, self.led_green, self.led_blue = color

    # Default seconds to wait after opening before sending a report: the device
    # may still be busy applying a previous profile write.
    DEFAULT_SETTLE_SECONDS = 2

    @staticmethod
    def open_device(settle_seconds: float = DEFAULT_SETTLE_SECONDS) -> "hid.device":
        print("Opening device vendor 0x046D (Logitech) product 0xC24A (G600)")
        try:
            h = hid.device()
            h.open(0x046D, 0xC24A)  # Logitech:0x046d G600:0xC24A
            print(f"Manufacturer: {h.get_manufacturer_string()}")
            print(f"Product: {h.get_product_string()}")
            print(f"Serial No: {h.get_serial_number_string()}")
            time.sleep(settle_seconds)
            return h
        except OSError:
            print("error opening device vendor 0x046D (Logitech) product 0xC24A (G600)")
            print("Close Logitech GHUB, Karabiner, Hammerspoon, etc.")
            print(
                "The terminal application must have input monitoring permission in System Settings > Privacy & Security > Input Monitoring"
            )
            raise

    def _with_handle(self, handle, settle_seconds: float, fn):
        """Run ``fn(handle)`` against an open device.

        If ``handle`` is given it is reused and left open (the caller owns its
        lifecycle). Otherwise a fresh handle is opened and closed around ``fn``.
        """
        if handle is not None:
            return fn(handle)
        h = self.open_device(settle_seconds)
        try:
            return fn(h)
        finally:
            h.close()

    def write_to_device(
        self, handle=None, settle_seconds: float = DEFAULT_SETTLE_SECONDS
    ) -> None:
        def _write(h):
            print("writing profile", self.profile_number)
            rc = h.send_feature_report(self.feature_report())
            if rc == -1:
                raise OSError(
                    "error writing profile %d.\n"
                    "Close Logitech GHUB, Karabiner, Hammerspoon, etc.\n"
                    "run this as sudo root" % self.profile_number
                )
            print(
                "Successfully wrote profile %d (%d bytes)" % (self.profile_number, rc)
            )

        self._with_handle(handle, settle_seconds, _write)

    def set_as_active_profile(
        self, handle=None, settle_seconds: float = DEFAULT_SETTLE_SECONDS
    ) -> None:
        print("Set profile %d as active profile" % self.profile_number)

        def _activate(h):
            rc = h.send_feature_report(
                [0xF0, 0x80 | (self.profile_number << 4), 0x00, 0x00]
            )
            # 0xF0: the report id to set the active profile
            # - [0xF0, 0x80, 0x00, 0x00] for profile 1 (0x80 | (index << 4)) index: 0, 0x80 = b10000000
            # - [0xF0, 0x90, 0x00, 0x00] for profile 2 (0x80 | (index << 4)) index: 1, 0x90 = b10010000
            # - [0xF0, 0xa0, 0x00, 0x00] for profile 3 (0x80 | (index << 4)) index: 2, 0xa0 = b10100000
            if rc == -1:
                raise OSError(
                    "error setting profile %d as active" % self.profile_number
                )

        self._with_handle(handle, settle_seconds, _activate)

    def __repr__(self):
        return "LogitechG600Profile(%d)" % self.profile_number

    def __str__(self):
        to_return = []
        to_return.append("Profile %d" % self.profile_number)
        to_return.append(
            "RGB (%d,%d,%d)" % (self.led_red, self.led_green, self.led_blue)
        )
        to_return.append(f"LED effect ({self.get_led_effect_string()})")
        to_return.append("LED duration (%d seconds)" % (self.led_duration))
        to_return.append(
            f"Frequency {self.frequency} Hz (0x{self.frequency_to_byte():02X})"
        )
        to_return.append(
            "DPI Shift %4d dpi (0x%02X)" % (self.dpi_shift, self._dpi_shift)
        )
        to_return.append(
            "DPI Default %4ddpi (0x%02X)" % (self.dpi_default, self._dpi_default)
        )
        for slot in range(1, 5):
            to_return.append(
                "DPI%d %4ddpi (0x%02X)"
                % (slot, self.get_dpi(slot), self._dpis[slot - 1])
            )
        labels = {1: "Left Click   ", 2: "Right Click  "}
        for i in range(1, 21):
            label = labels.get(i, "             ")
            to_return.append(
                "%sG%-2d 0x%02X 0x%02X 0x%02X"
                % ((label, i) + self.get_button("G%d" % i))
            )
        to_return.append(f"G-Shift color {self.gshift_color}")
        for i in range(1, 21):
            label = labels.get(i, "             ")
            to_return.append(
                "%sG%-2d 0x%02X 0x%02X 0x%02X"
                % ((label, i) + self.get_gshift_button("G%d" % i))
            )
        return "\n".join(to_return)


def build_profiles() -> list[LogitechG600Profile]:
    print("MEH", f"{LogitechG600Profile.MEH:02x}")
    print("HYPER", f"{LogitechG600Profile.HYPER:02x}")
    profile0 = LogitechG600Profile(0)
    profile0.color = (255, 0, 0)
    profile0.gshift_color = (0, 255, 255)
    profile0.frequency = 125

    # HYPER = Control + Shift + Alt + Command (all)  = LEFT_CTRL | LEFT_SHIFT | LEFT_ALT | LEFT_GUI
    # MEH   = Control + Shift + Alt  (no Command)    = LEFT_CTRL | LEFT_SHIFT | LEFT_ALT

    profile0.set_button("g4", value=(0, 0, 0x81))  # keyboard volume down
    profile0.set_button("g5", value=(0, 0, 0x80))  # keyboard volume up
    profile0.set_button("g7", value="RESOLUTION_CYCLE_UP")  # DPI cycle
    profile0.set_button("g8", value="PROFILE_CYCLE_UP")  # profile cycle up
    profile0.set_button(
        "g9", value="CTRL+CMD+SHIFT+4"
    )  # macOS screenshot of selected area to clipboard
    profile0.set_button("g10", value="CMD+C")  # Cmd + C (copy)
    profile0.set_button("g11", value="CMD+SHIFT+V")  # KM Smart Paste
    profile0.set_button("g12", value="HYPER+4")  # hyper + 4
    profile0.set_button("g13", value="HYPER+5")  # hyper + 5
    profile0.set_button("g14", value="HYPER+6")  # hyper + 6
    # No Shift: macOS records Shift+7 as "&", which breaks Shortcuts hotkeys
    profile0.set_button("g15", value="CTRL+ALT+CMD+7")  # Play/Pause via Shortcuts
    profile0.set_button(
        "g16", value="CTRL+LEFT"
    )  # Mission Control > Previous desktop space
    profile0.set_button(
        "g17", value="CTRL+RIGHT"
    )  # Mission Control > Next desktop space
    profile0.set_button("g18", value="HYPER+0")  # hyper + 0
    profile0.set_button("g19", value="HYPER+MINUS")  # hyper + -
    profile0.set_button("g20", value="HYPER+EQUAL")  # hyper + =
    profile0.set_gshift_button("g9", value="MEH+1")  # meh + 1
    profile0.set_gshift_button("g10", value="CMD+B")  # Cmd + b (bold)
    profile0.set_gshift_button("g11", value="CMD+V")  # Cmd + V (paste)
    profile0.set_gshift_button("g12", value="MEH+4")  # meh + 4
    profile0.set_gshift_button("g13", value="MEH+5")  # meh + 5
    profile0.set_gshift_button("g14", value="MEH+6")  # meh + 6
    profile0.set_gshift_button("g15", value="MEH+7")  # meh + 7
    profile0.set_gshift_button("g16", value="MEH+8")  # meh + 8
    profile0.set_gshift_button("g17", value="MEH+9")  # meh + 9
    profile0.set_gshift_button("g18", value="MEH+0")  # meh + 0
    profile0.set_gshift_button("g19", value="MEH+MINUS")  # meh + -
    profile0.set_gshift_button("g20", value="MEH+EQUAL")  # meh + =

    profile1 = LogitechG600Profile(1)
    profile1.color = (0, 255, 0)
    profile1.gshift_color = (255, 1, 255)

    profile2 = LogitechG600Profile(2)
    profile2.color = (0, 0, 255)
    profile2.gshift_color = (255, 255, 0)

    return [profile0, profile1, profile2]


class Settings(BaseSettings):
    """Command-line settings for writing G600 profiles.

    Values can be passed as CLI flags (e.g. ``--profiles 0 1`` or
    ``--reuse_connection true``) or via ``G600_``-prefixed environment variables.
    """

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_prog_name="write_logitech_g600_profiles",
        env_prefix="G600_",
    )

    profiles: list[int] = Field(
        default=[0, 1, 2],
        description="Which profile numbers (0-2) to write to the device.",
    )
    active_profile: int | None = Field(
        default=0,
        description="Profile to leave active after writing, or null to leave unchanged.",
    )
    reuse_connection: bool = Field(
        default=False,
        description=(
            "Open the device once and reuse the handle for all operations. "
            "Some setups/firmware reject reused handles; off by default opens a "
            "fresh handle per operation."
        ),
    )
    settle_seconds: float = Field(
        default=LogitechG600Profile.DEFAULT_SETTLE_SECONDS,
        description="Seconds to wait after opening the device before sending a report.",
    )


def run(settings: Settings) -> int:
    all_profiles = {p.profile_number: p for p in build_profiles()}

    selected: list[LogitechG600Profile] = []
    for number in settings.profiles:
        if number not in all_profiles:
            print("Invalid profile number %d (expected 0, 1 or 2)" % number)
            return 1
        selected.append(all_profiles[number])

    if (
        settings.active_profile is not None
        and settings.active_profile not in all_profiles
    ):
        print(
            "Invalid active profile %d (expected 0, 1 or 2)" % settings.active_profile
        )
        return 1

    handle = None
    try:
        if settings.reuse_connection:
            handle = LogitechG600Profile.open_device(settings.settle_seconds)

        for profile in selected:
            profile.write_to_device(
                handle=handle, settle_seconds=settings.settle_seconds
            )
            print("Wrote profile", profile.profile_number)
            print("Color (R,G,B): ", profile.color)

        if settings.active_profile is not None:
            all_profiles[settings.active_profile].set_as_active_profile(
                handle=handle, settle_seconds=settings.settle_seconds
            )
    except OSError as e:
        print(e)
        return 1
    finally:
        if handle is not None:
            handle.close()
    return 0


def main() -> int:
    return run(Settings())


if __name__ == "__main__":
    sys.exit(main())


# https://trezor.github.io/cython-hidapi/api.html#hid.device.SEND_FEATURE_REPORT
