import sys

code_mappings = {
    0x00: "None",
    0x01: "BUTTON1",
    0x02: "BUTTON2",
    0x03: "BUTTON3",
    0x04: "BUTTON4",
    0x05: "BUTTON5",
    0x11: "RESOLUTION_UP",
    0x12: "RESOLUTION_DOWN",
    0x13: "RESOLUTION_CYCLE_UP",
    0x14: "PROFILE_CYCLE_UP",
    0x15: "RESOLUTION_ALTERNATE",
    0x17: "SECOND_MODE",
}

keyboard_hut_table = {
    0x04: "a",
    0x05: "b",
    0x06: "c",
    0x07: "d",
    0x08: "e",
    0x09: "f",
    0x0A: "g",
    0x0B: "h",
    0x0C: "i",
    0x0D: "j",
    0x0E: "k",
    0x0F: "l",
    0x10: "m",
    0x11: "n",
    0x12: "o",
    0x13: "p",
    0x14: "q",
    0x15: "r",
    0x16: "s",
    0x17: "t",
    0x18: "u",
    0x19: "v",
    0x1A: "w",
    0x1B: "x",
    0x1C: "y",
    0x1D: "z",
    0x1E: "1",
    0x1F: "2",
    0x20: "3",
    0x21: "4",
    0x22: "5",
    0x23: "6",
    0x24: "7",
    0x25: "8",
    0x26: "9",
    0x27: "0",
    0x28: "RETURN",
    0x29: "ESCAPE",
    0x2A: "BACKSPACE",
    0x2B: "TAB",
    0x2C: "SPACE",
    # Fill in the rest of the keys fro 0x2D to 0x4F
    0x2D: "MINUS",
    0x2E: "EQUAL",
    0x2F: "LEFTBRACKET",
    0x30: "RIGHTBRACKET",


}

def print_logitech_button(buttonname, code, modifier, key):
    code_str = code_mappings.get(code, "")
    key_str = keyboard_hut_table.get(key, "unknown")
    modifier_str = get_modifiers_string(modifier)
    # print(type(modifier))
    # print("  Key %3s 0x%02X(%20s) %b (%s) %2d (%10s)" % (buttonname,code, code_str, modifier, get_modifiers_string(modifier), key, key_str))
    print(f"  Key {buttonname:3s} 0x{code:02x}({code_str:20s}) 0b{modifier:08b} ({modifier_str:20s}) 0x{key:02X} ({key_str:10s})")
def get_modifiers_string(modifier):
    modifiers = []
    if modifier & 0x01:
        modifiers.append("Left Control")
    if modifier & 0x02:
        modifiers.append("Left Shift")
    if modifier & 0x04:
        modifiers.append("Left Alt")
    if modifier & 0x08:
        modifiers.append("Left GUI")
    if modifier & 0x10:
        modifiers.append("Right Control")
    if modifier & 0x20:
        modifiers.append("Right Shift")
    if modifier & 0x40:
        modifiers.append("Right Alt")
    if modifier & 0x80:
        modifiers.append("Right GUI")
    return ", ".join(modifiers)

def print_feature_report(d):
    d = d.copy()
    print("Feature Report")
    reportid = d.pop(0)
    print("  Report ID: %d" % reportid)
    led_red = d.pop(0)
    led_green = d.pop(0)
    led_blue = d.pop(0)
    print("  LED: %d %d %d" % (led_red, led_green, led_blue))
    led_effect = d.pop(0)
    led_duration = d.pop(0)
    print("  LED Effect: %d and duration %d" % (led_effect, led_duration))
    d = d[5:] # remove  5 unknown bytes
    frequency = 1000 / (1+d.pop(0))
    print("  Frequency: %d" % frequency)
    dpi_shift = d.pop(0) * 50
    dpi_default = d.pop(0)
    dpi_1 = d.pop(0) * 50
    dpi_2 = d.pop(0) * 50
    dpi_3 = d.pop(0) * 50
    dpi_4 = d.pop(0) * 50
    dpis = [dpi_1, dpi_2, dpi_3, dpi_4]
    dpi_default = dpis[dpi_default]
    print("  DPI: shift:%d default:%d %d %d %d %d" % (dpi_shift, dpi_default, dpi_1, dpi_2, dpi_3, dpi_4))
    d = d[13:] # remove 13 unknown bytes
    keys = []
    for i in range(20):
        code, modifier, key = d[0:3]
        keys.append((code, modifier, key))
        d = d[3:]
    # keys = sorted(keys, key=lambda x: x[0])
    for i,(code, modifier, key) in enumerate(keys):
        print_logitech_button("G%d"%(i+1),code, modifier, key)
    gshift_color = (d.pop(0), d.pop(0), d.pop(0))

    keys = []
    for i in range(20):
        code, modifier, key = d[0:3]
        keys.append((code, modifier, key))
        d = d[3:]
    # keys = sorted(keys, key=lambda x: x[0])
    for i, (code, modifier, key) in enumerate(keys):
        print_logitech_button("G%d"%(i+1),code, modifier, key)
    print("  G-Shift Color: %d %d %d" % gshift_color)


profile0 = [243, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 23, 0, 0, 0, 2, 5, 20, 0, 0, 0, 0, 30, 0, 0, 31, 0, 0, 32, 0, 0, 33, 0, 0, 34, 0, 0, 35, 0, 0, 36, 0, 0, 37, 0, 0, 38, 0, 0, 39, 0, 0, 45, 0, 0, 46, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 23, 0, 0, 0, 2, 5, 20, 0, 0, 0, 1, 30, 0, 1, 31, 0, 1, 32, 0, 1, 33, 0, 1, 34, 0, 1, 35, 0, 1, 36, 0, 1, 37, 0, 1, 38, 0, 1, 39, 0, 1, 45, 0, 1, 46]
profile1 = [244, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 23, 0, 0, 0, 2, 5, 20, 0, 0, 0, 0, 89, 0, 0, 90, 0, 0, 91, 0, 0, 92, 0, 0, 93, 0, 0, 94, 0, 0, 95, 0, 0, 96, 0, 0, 97, 0, 0, 98, 0, 0, 86, 0, 0, 87, 255, 255, 255, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 23, 0, 0, 0, 2, 5, 20, 0, 0, 0, 1, 89, 0, 1, 90, 0, 1, 91, 0, 1, 92, 0, 1, 93, 0, 1, 94, 0, 1, 95, 0, 1, 96, 0, 1, 97, 0, 1, 98, 0, 1, 86, 0, 1, 87]
profile2 = [245, 0, 255, 0, 1, 4, 0, 0, 0, 0, 0, 0, 8, 2, 8, 24, 40, 64, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 21, 0, 0, 19, 0, 0, 20, 0, 0, 0, 0, 30, 0, 0, 31, 0, 0, 32, 0, 0, 33, 0, 0, 34, 0, 0, 35, 17, 0, 0, 22, 0, 0, 5, 0, 0, 18, 0, 0, 0, 0, 8, 4, 0, 0, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# print_feature_report(profile0)
# print_feature_report(profile1)
# print_feature_report(profile2)
# sys.exit(0)

import hid 
import binascii

# for device_dict in hid.enumerate():
#     keys = list(device_dict.keys())
#     keys.sort()
#     for key in keys:
#         print("%s : %s" % (key, device_dict[key]))
#     print()

h = hid.device()
h.open(0x046D,0xC24A)

print("Manufacturer: %s" % h.get_manufacturer_string())
print("Product: %s" % h.get_product_string())
print("Serial No: %s" % h.get_serial_number_string())





d = h.get_feature_report(report_num = 0xF3, max_length = 154) # 0xF3 report id: profile 0
print(d)
print_feature_report(d)

# d = h.get_feature_report(report_num = 0xF0, max_length = 154) # 0xF0 report id: get active profile
# print(d)

# d = h.get_feature_report(report_num = 0xF4, max_length = 154) # 0xF4 report id: profile 1
# print(d)
# d = h.get_feature_report(report_num = 0xF5, max_length = 154) # 0xF5 report id: profile 2
# print(d)
# print_feature_report(d)



# while True:
#     d =  h.read(8)
#     print(d)


