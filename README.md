This is a script to update the onboard profile on a Logitech G600 mouse. 

It uses python and `hidapi` to communicate with the mouse.

You can't communicate directly with the mouse in macOS because the OS hid driver already
"owns" the device. You can't just open the device and send it commands. You have to
to use hidapi will in turn will use `IOHidManager` to that the kernel driver send the 
HID Set Report command to the device.


# Report structure


The format of the report and the report id are not specified in the Logitech documentation.

The libratbag project has reverse engineered the report format and report id for the G600
and I have used their code as a reference.

The 3 profiles are stores in the mouse in report 0xF3, 0xF4, and 0xF5.

`hidapi`'s `send_feature_report` take a list of int where the first element is the report id
and the rest is the actual report. I'll consider the report id to be part of the report 
althought techincally they are different.


* byte 0: report id (0xF3 for profile 0, 0xF4 for profile 1, 0xF5 for profile 2)
* byte 1: led_red (0-255)
* byte 2: led_green (0-255)
* byte 3: led_blue (0-255)
* byte 4: led_effect (0x00 for solid color, 0x01 for breathing effect, 0x02 for color cycle)
* byte 5: led_duration (0x00 - 0x0F), in seconds so from 0 to 15 seconds
* byte 6-10: unknown1 [0x00, 0x00, 0x00, 0x00, 0x00]
* byte 11: USB report rate (0x00 for 1000Hz (1000/ 0+1), 0x01 for 500Hz (1000/2+1), 0x03 for 250Hz (1000/4+1), 0x07 for 125Hz (1000/7+1))
* byte 12: DPI shift value (0x04-0xA4), value * 50 = dpi, 0x04 = 4 * 50 = 200dpi, 0xA4 = 164 * 50 = 8200dpi
* byte 13: DPI default value (0x00-0x03) index on DPI values list that follows in the next 4 bytes
* byte 14: DPI value 1 (0x04-0xA4), value * 50 = dpi, 0x04 = 4 * 50 = 200dpi, 0xA4 = 164 * 50 = 8200dpi (default 3200dpi 0x40)
* byte 15: DPI value 2 (0x04-0xA4), value * 50 = dpi, 0x04 = 4 * 50 = 200dpi, 0xA4 = 164 * 50 = 8200dpi (default 2000dpi 0x28)
* byte 16: DPI value 3 (0x04-0xA4), value * 50 = dpi, 0x04 = 4 * 50 = 200dpi, 0xA4 = 164 * 50 = 8200dpi (default 1200dpi 0x18)
* byte 17: DPI value 4 (0x04-0xA4), value * 50 = dpi, 0x04 = 4 * 50 = 200dpi, 0xA4 = 164 * 50 = 8200dpi (default  400dpi 0x08)
* byte 18-30: unknown2 [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
* byte 31-33: G1 left mouse button  (code, modifier, key) (code can be 0x00, 0x01, 0x02,0x03, 0x04, 0x05, 0x11, 0x12, 0x13, 0x14, 0x15, 0x17). See below for explanation
* byte 34-36: G2 right mouse button (code, modifier, key)
* byte 37-39: G3 wheel button (code, modifier, key)
* byte 40-42: G4 wheel left (code, modifier, key)
* byte 43-45: G5 wheel right (code, modifier, key)
* byte 46-48: G6 G-shift mouse button (code, modifier, key)
* byte 49-51: G7 (code, modifier, key)
* byte 52-54: G8 (code, modifier, key)
* byte 55-57: G9 (code, modifier, key)
* byte 58-60: G10 (code, modifier, key)
* byte 61-63: G11 (code, modifier, key)
* byte 64-66: G12 (code, modifier, key)
* byte 67-69: G13 (code, modifier, key)
* byte 70-72: G14 (code, modifier, key)
* byte 73-75: G15 (code, modifier, key)
* byte 76-78: G16 (code, modifier, key)
* byte 79-81: G17 (code, modifier, key)
* byte 82-84: G18 (code, modifier, key)
* byte 85-87: G19 (code, modifier, key)
* byte 88-90: G20 (code, modifier, key)
* byte 91-93: GShift color (red, green, blue) 
* byte 94-96: GShift G1 left mouse button (code, modifier, key)
* byte 97-99: GShift G2 right mouse button (code, modifier, key)
* byte 100-102: GShift G3 wheel button (code, modifier, key)
* byte 103-105: GShift G4 wheel left (code, modifier, key)
* byte 106-108: GShift G5 wheel right (code, modifier, key)
* byte 109-111: GShift G6 Gshiftbutton (code, modifier, key)
* byte 112-114: GShift G7 (code, modifier, key)
* byte 115-117: GShift G8 (code, modifier, key)
* byte 118-120: GShift G9 (code, modifier, key)
* byte 121-123: GShift G10 (code, modifier, key)
* byte 124-126: GShift G11 (code, modifier, key)
* byte 127-129: GShift G12 (code, modifier, key)
* byte 130-132: GShift G13 (code, modifier, key)
* byte 133-135: GShift G14 (code, modifier, key)
* byte 136-138: GShift G15 (code, modifier, key)
* byte 139-141: GShift G16 (code, modifier, key)
* byte 142-144: GShift G17 (code, modifier, key)
* byte 145-147: GShift G18 (code, modifier, key)
* byte 148-150: GShift G19 (code, modifier, key)
* byte 151-153: GShift G20 (code, modifier, key)


the key mappings are (code, modifier, key):
* code 0x00 means that it's a key (not a mouse button), it will use (modifier,key) for the mapping 
  * When code 0x00
  * modifier is an & (bitwise and) of the possible values:
    * 0x01 left_ctrl
    * 0x02 left_shift
    * 0x04 left_alt
    * 0x08 left_gui
    * 0x10 right_ctrl
    * 0x20 right_shift
    * 0x40 right_alt
    * 0x80 right_gui
  * key is the key code according to the USB HID Usage Tables for USB / Keyboard/Keypad Page 0x07
    * 0x04 a
    * ...
    * 0x1D z
    * 0x1E 1
    * ...
    * 0x27 0
    * 0x2d - minus dash
    * 0x2e = equal
    * 0x7f mute (keyboard mute key)
    * 0x80 volume_up (keyboard volume up key)
    * 0x81 volume_down (keyboard volume down key)
* code 0x01 means that it's mouse button1 (left mouse click)
* code 0x02 means that it's mouse button2 (right mouse click)
* code 0x03 means that it's mouse button3 # HID Usage Tables for USB / Button Page 0x09 
* code 0x04 means that it's mouse button4 # HID Usage Tables for USB / Button Page 0x0j
* code 0x05 means that it's mouse button4 # HID Usage Tables for USB / Button Page 0x0j
* code 0x05 means that it's mouse button4 # HID Usage Tables for USB / Button Page 0x0j
* code 0x11 means DPI up, resolution_up 
* code 0x12 means DPI down, resolution_up 
* code 0x13 means DPI cycle up, resolution_cycle_up 
* code 0x14 means Profile cycle up, profile_cycle_up
* code 0x15 means DPI shift , resolutions_alternate
* code 0x17 means G-Shift, second_mode




# How to run

```
pyenv virtualenv 3.12 g600
source $(pyenv prefix g600)/bin/activate
pip install -U pip
pip install hidapi
sudo python write_logitech_g600_profiles.py
```

You need to run as sudo, you can't send HID feature reports without root access in macOS at least.
