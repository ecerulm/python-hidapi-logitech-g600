This is a script to update the onboard profile on a Logitech G600 mouse. 

It uses python and `hidapi` to communicate with the mouse.

You can't communicate directly with the mouse in macOS because the OS hid driver already
"owns" the device. You can't just open the device and send it commands. You have to
to use hidapi will in turn will use `IOHidManager` to that the kernel driver send the 
HID Set Report command to the device.

# Why do this?

* I don't like the Logitech G Hub software
* You can't edit the onboard profile directly in GHub you need to switch to
  regular profile and then write that profile to the onboard memory.
* I want to have a textual representation of the profiles so I can version control them
* I want to set the Gshift color (the color when Gshift button is pressed) that is not
  available in the GHub software.


# Report structure


The format of the report and the report id are not specified in the Logitech documentation.

The libratbag project has reverse engineered the report format and report id for the G600
and I have used their code as a reference.

The 3 profiles are stored in the mouse in report `0xF3`, `0xF4`, and `0xF5`.

`hidapi`'s `send_feature_report` take a list of int where the first element is the report id
and the rest is the actual report. I'll consider the report id to be part of the report 
althought techincally they are different.

I got the default values from [Setup Guide Logitech® G600 MMO Gaming Mouse 
](https://www.logitech.com/assets/44964/3/g600-mmo-gaming-mouse-quickstart-guide.pdf)

| byte | description | notes |default|
|------|-------------|-------|-------|
| 0 | report id | (`0xF3` for profile 0, `0xF4` for profile 1, `0xF5` for profile 2)|
|  1| led_red | (0-255)| 0|
|  2| led_green| (0-255)|0|
|  3| led_blue |(0-255)|0|
|  4| led_effect |(`0x00` for solid color, `0x01` for breathing effect, `0x02` for color cycle)| `0x00`|
|  5| led_duration | (`0x00` - `0x0F`), in seconds so from 0 to 15 seconds| 0 seconds|
|  6-10| unknown1 | [`0x00`, `0x00`, `0x00`, `0x00`, `0x00`]| |
|  11| USB report rate |`0x00` for 1000Hz (1000/ 0+1),</br> `0x01` for 500Hz (1000/2+1),</br> `0x03` for 250Hz (1000/4+1),</br> `0x07` for 125Hz (1000/7+1))| `0x07` 125Hz|
|  12| DPI shift value |(`0x04`-`0xA4`), </br>value * 50 = dpi, </br>0x04 = 4 * 50 = 200dpi, </br>0xA4 = 164 * 50 = 8200dpi| 200dpi |
|  13| DPI default value | (`0x00`-`0x03`)</br> index on DPI values list that follows in the next 4 bytes, `0x00` use DPI value1, `0x01` use DPI value 2, `0x02` use DPI value 3, `0x03` use DPI value 4| 2 (1200 dpi)|
|  14| DPI value 1 |(`0x04`-`0xA4`),</br> value * 50 = dpi,</br> `0x04` = 4 * 50 = 200dpi,</br> `0xA4` = 164 * 50 = 8200dpi | (default 3200dpi `0x40`)|
|  15| DPI value 2 |(`0x04`-`0xA4`),</br> value * 50 = dpi,</br> `0x04` = 4 * 50 = 200dpi,</br> `0xA4` = 164 * 50 = 8200dpi |(default 2000dpi `0x28`)|
|  16| DPI value 3 |(`0x04`-`0xA4`),</br> value * 50 = dpi,</br> `0x04` = 4 * 50 = 200dpi,</br> `0xA4` = 164 * 50 = 8200dpi |(default 1200dpi `0x18`)|
|  17| DPI value 4 |(`0x04`-`0xA4`),</br> value * 50 = dpi,</br> `0x04` = 4 * 50 = 200dpi,</br> `0xA4` = 164 * 50 = 8200dpi |(default  400dpi `0x08`)|
|  18-30| unknown2 | `[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]`|
|  31-33| G1 left mouse button  |(code, modifier, key) (code can be `0x00`, `0x01`, `0x02`,`0x03`, `0x04`, `0x05`, `0x11`, `0x12`, `0x13`, `0x14`, `0x15`, `0x17`). See below for explanation| button1|
|  34-36| G2 right mouse button |(code, modifier, key)| `(0x02,0x00,0x00)` button2|
|  37-39| G3 wheel button |(code, modifier, key)| `(0x03,0x00,0x00)` button3|
|  40-42| G4 wheel left |(code, modifier, key)|  `(0x04,0x00,0x00)` button4|
|  43-45| G5 wheel right |(code, modifier, key)|  `(0x05,0x00,0x00)` button5|
|  46-48| G6 G-shift mouse button |(code, modifier, key)| `(0x17,0x00,0x00)` second_mode|
|  49-51| G7 |(code, modifier, key)| `(0x00,0x02,0x05)` shift-B|
|  52-54| G8 |(code, modifier, key)| `(0x14,0x00,0x00)` profile_cycle_up|
|  55-57| G9 |(code, modifier, key)| `(0x00,0x00,0x1E)` key_1 `"1"`|
|  58-60| G10 |(code, modifier, key)| `(0x00,0x00,0x1F)` key_2 `"2"` |
|  61-63| G11 |(code, modifier, key)| `(0x00,0x00,0x20)` key_3 `"3"`|
|  64-66| G12 |(code, modifier, key)| `(0x00,0x00,0x21)` key_4 `"4"`|
|  67-69| G13 |(code, modifier, key)| `(0x00,0x00,0x22)` key_5 `"5"`|
|  70-72| G14 |(code, modifier, key)| `(0x00,0x00,0x23)` key_6 `"6"`|
|  73-75| G15 |(code, modifier, key)| `(0x00,0x00,0x24)` key_7 `"7"`|
|  76-78| G16 |(code, modifier, key)| `(0x00,0x00,0x25)` key_8 `"8"`|
|  79-81| G17 |(code, modifier, key)| `(0x00,0x00,0x26)` key_9 `"9"`|
|  82-84| G18 |(code, modifier, key)| `(0x00,0x00,0x27)` key_0 `"0"`|
|  85-87| G19 |(code, modifier, key)| `(0x00,0x00,0x2D)` key_minus `"-"`|
|  88-90| G20 |(code, modifier, key)| `(0x00,0x00,0x2E)` key_equal `"="`|
|  91-93| GShift color |(red, green, blue) | `0x00, 0x00,0x00` black |
|  94-96| GShift G1 left mouse button |(code, modifier, key)| `(0x01,0x00,0x00)` button1|
|  97-99| GShift G2 right mouse button |(code, modifier, key)| `(0x02,0x00,0x00)` button2| 
|  100-102| GShift G3 wheel button |(code, modifier, key)|`(0x03,0x00,0x00)` button3| 
|  103-105| GShift G4 wheel left |(code, modifier, key)|`(0x04,0x00,0x00)` button4| 
|  106-108| GShift G5 wheel right |(code, modifier, key)|`(0x05,0x00,0x00)` button5| 
|  109-111| GShift G6 Gshiftbutton |(code, modifier, key)|`(0x17,0x00,0x00)` second_mode| 
|  112-114| GShift G7 |(code, modifier, key)|`(0x00,0x02,0x05)` shift-b| 
|  112-114| GShift G8 |(code, modifier, key)|`(0x14,0x00,0x00)` profile_cycle_up| 
|  118-120| GShift G9 |(code, modifier, key)|`(0x00,0x00,0x1E)` key_1 `"1"`| 
|  121-123| GShift G10 |(code, modifier, key)|`(0x00,0x00,0x1F)` key_2 `"2"`| 
|  124-126| GShift G11 |(code, modifier, key)|`(0x00,0x00,0x20)` key_3 `"3"`| 
|  127-129| GShift G12 |(code, modifier, key)|`(0x00,0x00,0x21)` key_4 `"4"`| 
|  130-132| GShift G13 |(code, modifier, key)|`(0x00,0x00,0x22)` key_5 `"5"`| 
|  133-135| GShift G14 |(code, modifier, key)|`(0x00,0x00,0x23)` key_6 `"6"`| 
|  136-138| GShift G15 |(code, modifier, key)|`(0x00,0x00,0x24)` key_7 `"7"`| 
|  139-141| GShift G16 |(code, modifier, key)|`(0x00,0x00,0x25)` key_8 `"8"`| 
|  142-144| GShift G17 |(code, modifier, key)|`(0x00,0x00,0x26)` key_9 `"9"`| 
|  145-147| GShift G18 |(code, modifier, key)|`(0x00,0x00,0x27)` key_0 `"0"`| 
|  148-150| GShift G19 |(code, modifier, key)|`(0x00,0x00,0x2D)` key_minus `"-"`| 
|  151-153| GShift G20 |(code, modifier, key)|`(0x00,0x00,0x2E)` key_equal `"="`| 


the key mappings are (code, modifier, key):

* code `0x00` means that it's a key (not a mouse button), it will use (modifier,key) for the mapping 
    * When code `0x00` modifier is an & (bitwise and) of the possible values:
        * `0x01` left_ctrl
        * `0x02` left_shift
        * `0x04` left_alt
        * `0x08` left_gui / windows key / command key/ meta key
        * `0x10` right_ctrl
        * `0x20` right_shift
        * `0x40` right_alt
        * `0x80` right_gui / windows key / command key / meta key
    * When code `0x00` key is the key code according to the USB HID Usage Tables for USB / Keyboard/Keypad Page 0x07
        * `0x04` a
        * ...
        * `0x13` p
        * ...
        * `0x19` v
        * `0x1D` z
        * `0x1E` 1
        * ...
        * `0x27` 0
        * `0x2D` - minus dash
        * `0x2E` = equal
        * ...
        * `0x3A` F1
        * ...
        * `0x45` F12
        * ...
        * `0x68` F13
        * ...
        * `0x73` F24
        * ...
        * `0x7F` mute (keyboard mute key)
        * `0x80` volume_up (keyboard volume up key)
        * `0x81` volume_down (keyboard volume down key)
* code `0x01` means that it's mouse button1 (left mouse click) # [HID Usage Tables] for USB / Button Page 0x09
* code `0x02` means that it's mouse button2 (right mouse click) # [HID Usage Tables] for USB / Button Page 0x09
* code `0x03` means that it's mouse button3 # [HID Usage Tables] for USB / Button Page 0x09 
* code `0x04` means that it's mouse button4 # [HID Usage Tables] for USB / Button Page 0x09
* code `0x05` means that it's mouse button4 # [HID Usage Tables] for USB / Button Page 0x09
* code `0x05` means that it's mouse button4 # [HID Usage Tables] for USB / Button Page 0x09
* code `0x11` means DPI up, resolution_up 
* code `0x12` means DPI down, resolution_up 
* code `0x13` means DPI cycle up, resolution_cycle_up 
* code `0x14` means Profile cycle up, profile_cycle_up
* code `0x15` means DPI shift , resolutions_alternate
* code `0x17` means G-Shift button, second_mode




# How to run

You need to give your terminal application the "Input Monitoring" permission via
System Preferences -> Security & Privacy -> Privacy -> Input Monitoring

You also need to run as root (sudo)

```
brew install hidapi
pyenv virtualenv 3.12 g600
source $(pyenv prefix g600)/bin/activate
pip install -U pip
pip install hidapi
sudo python write_logitech_g600_profiles.py
```

You need to run as sudo, you can't send HID feature reports without root access in macOS at least.

Close all software that maybe using USB devices directly like 

* Logitech GHub
* Karabiner-Elements
* HammerSpoon
* Keyboard Maestro

You may need to run the script multiple times (5-10 time) to get the mouse to accept the new profile.
I don't know why but sometimes it takes a few tries. and sometimes it works on the first try.


# References

* [libratbag profile report](https://github.com/libratbag/libratbag/blob/8444ceb638b19c3fbeb073a5cd29f17c6d34dd07/src/driver-logitech-g600.c#L61-L77)
* [libratbag write profile](https://github.com/libratbag/libratbag/blob/8444ceb638b19c3fbeb073a5cd29f17c6d34dd07/src/driver-logitech-g600.c#L477-L590)
* [libratbag set active profile](https://github.com/libratbag/libratbag/blob/8444ceb638b19c3fbeb073a5cd29f17c6d34dd07/src/driver-logitech-g600.c#L247)

[HID Usage Tables]: https://www.usb.org/document-library/hid-usage-tables-15
