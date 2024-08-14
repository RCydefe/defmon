import os
import time
import machine
import random
import ssd1306
from ssd1306 import SSD1306_I2C
import ujson
from umenu import *
from machine import Pin, SPI, I2C
from time import sleep
import asyncio
from primitives import Pushbutton
import framebuf

#from adventure import main
# Turn on verbose debugging.
import esp
esp.osdebug(0, esp.LOG_VERBOSE)

# enable debug logging
#logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for the asyncio module
#logging.getLogger("asyncio").setLevel(logging.WARNING)

##########################
## hardcoded bitmaps
##########################
shenan = framebuf.FrameBuffer(bytearray(
    b'\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x05\x50\x09\x40\x60\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x07\xff\xf0\x0f\xff\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xf8\x1f\xff\xf0\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x07\xff\xf0\x0f\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xf8\x0f\xff\xe0\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x03\xff\xf8\x0f\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xfc\x1f\xff\xc0\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x01\xff\xf8\x0f\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xf8\x0f\xff\xc0\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x01\xff\xf8\x0f\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xff\xfc\x0f\xff\x80\x40\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x01\x00\xff\xfc\x0f\xff\x80\x40\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80\xff\xfc\x1f\xff\x80\xc0\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x07\xc0\xff\xf8\x1f\xff\x80\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x09\x20\xff\xf8\x1f\xff\x82\xd0\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x19\x30\x7f\xf8\x1f\xff\x01\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x5f\xf4\x7f\xf8\x1f\xff\x3f\x3c\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x38\x38\x7f\xfc\x1f\xff\x0f\x3f\x00\x00\x00\x00\x00\x00\x00\x00\x17\xd0\x7f\xfc\x1f\xff\x01\xe0\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x0f\xe0\x7f\xfc\x1f\xff\x02\xd0\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80\x7f\xf8\x0f\xff\x00\xc0\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x03\x80\x7f\xf8\x0f\xff\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x7f\xf8\x0f\xff\x00\x80\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x01\x00\x78\x00\x00\x1f\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x7c\x0f\xff\xff\x00\x00\x80\x00\x00\x00'
    b'\x00\x00\x00\x01\xc0\x00\x70\x7f\xff\xff\x00\x01\xc0\x00\x00\x00\x00\x07\x00\x03\xe0\x00\x78\x1f\xff\xff\x00\x03\xe0\x00\xe0\x00'
    b'\x00\x08\x80\x01\xc0\x00\x78\x0f\xff\xff\x00\x01\xc0\x01\x10\x00\x00\x10\x00\x00\x82\xf8\x78\x3f\xff\xff\x0f\x20\x80\x00\x08\x00'
    b'\x00\x10\x40\x00\x07\x9e\x70\x3f\xff\xff\x3c\xf0\x00\x02\x08\x00\x00\x10\x40\x00\x07\xe7\xfc\x1f\xff\xff\xf3\xe0\x00\x02\x08\x00'
    b'\x00\x08\xc0\x00\x03\xf9\xf8\x0f\xff\xff\xcf\xe0\x00\x03\x10\x00\x00\x07\x00\x00\x01\xfe\x30\x3f\xff\xfe\x3f\xc0\x00\x00\xe0\x00'
    b'\x00\x02\x30\x00\x00\xff\xc7\x3f\xff\xf1\xff\x80\x00\x0c\x40\x00\x00\x02\x48\x00\x00\x3f\xf8\x1f\xfc\x0f\xfe\x00\x00\x12\x40\x00'
    b'\x00\x01\x84\x00\x00\x07\xff\xe0\x03\xff\xf0\x00\x00\x21\x80\x00\x00\x01\x84\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x21\x80\x00'
    b'\x00\x01\x48\x00\x01\xf0\x03\xff\xff\xe0\x0f\xc0\x00\x12\x80\x00\x00\x02\x30\x00\x07\xf8\x00\x00\x00\x00\x0f\xe0\x00\x0c\x40\x00'
    b'\x00\x02\x00\x00\x07\x0c\x00\xe0\x03\x80\x18\x70\x00\x00\x40\x00\x00\x04\x00\x00\x0e\x0c\x07\xfc\x1f\xf0\x18\x38\x00\x00\x20\x00'
    b'\x00\x08\x00\x00\x0e\x6c\x0f\xde\x3d\xf8\x1b\x38\x00\x00\x10\x00\x00\x00\x00\x00\x0e\x4c\x1e\xff\x7f\xbc\x19\x38\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x0e\x78\x3b\xff\xff\xde\x0f\x18\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x77\xdf\xfd\xef\x00\x78\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x0f\x00\xff\x77\xff\x7b\x80\x78\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xc1\xde\xef\xfb\xbd\xc1\xf8\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x07\xbf\xbd\xdf\xfd\xde\xfe\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x07\xe0\xf7\xbf\x7e\xf7\x83\xf0\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x03\xdf\xef\x7f\x7f\xfb\xfd\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x01\xf0\x3e\xfe\x3f\xbf\x07\xc0\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\xff\xff\xfe\x3f\xff\xff\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xff\xfc\x1f\xff\xff\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x1f\xff\xf9\xcf\xff\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xe2\xa3\xff\xf8\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x01\xff\x84\x90\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x90\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x30\x02\xa0\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x01\xc0\x18\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x03\x02\xa0\x60\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x98\x00\x00\x00\x00\x00\x00\x00'),
    128, 62, framebuf.MONO_HLSB)

DMsplash = framebuf.FrameBuffer(bytearray(
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x7f\xfd\x07\xff\xc3\xff\xe3\xe0\x1f\x01\xff\xa0\xf8\x38\x00\x00\x7f\xfc\x07\xff\xd3\xff\xeb\xe8\x1f\x41\xff\x80\xfa\x3a\x00'
    b'\x00\x7c\x1f\x07\xc0\x13\xe0\x0b\xe8\x1f\x4f\x83\xe0\xfa\x3a\x00\x00\x7c\x1f\x47\xdf\xf3\xef\xfb\xe8\x1f\x4f\x83\xe8\xfa\x3a\x00'
    b'\x00\x7c\x1f\x47\xd0\x03\xe8\x03\xe0\x1f\x4f\x83\xe8\xf8\x3a\x00\x00\x7c\x1f\x47\xd0\x03\xe8\x03\xff\xff\x4f\x83\xe8\xff\x3a\x00'
    b'\x00\x7c\x1f\x47\xc0\x03\xe0\x03\xff\xff\x4f\x83\xe8\xff\x3a\x00\x00\x7c\x1f\x47\xfe\x03\xff\x03\xff\xff\x4f\x83\xe8\xff\x3a\x00'
    b'\x00\x7c\x1f\x47\xfe\x83\xff\x43\xff\xff\x4f\x83\xe8\xff\x3a\x00\x00\x7c\x1f\x47\xfe\x83\xff\x43\xff\xff\x4f\x83\xe8\xff\x3a\x00'
    b'\x00\x7c\x1f\x47\xc0\x83\xe0\x43\x1f\x3f\x4f\x83\xe8\xe7\xfa\x00\x00\x7c\x1f\x47\xdf\x83\xef\xc3\x1f\x3f\x4f\x83\xe8\xe7\xfa\x00'
    b'\x00\x7c\x1f\x47\xd0\x03\xe8\x03\x1f\x3f\x4f\x83\xe8\xe7\xfa\x00\x00\x7c\x1f\x47\xd0\x03\xe8\x03\x1f\x3f\x4f\x83\xe8\xe7\xfa\x00'
    b'\x00\x7c\x1f\x47\xd0\x03\xe8\x03\x1f\x3f\x4f\x83\xe8\xe7\xfa\x00\x00\x7c\x1f\x47\xd0\x03\xe8\x03\x40\x3f\x4f\x83\xe8\xe0\xfa\x00'
    b'\x00\x7c\x1f\x47\xc0\x03\xe8\x03\x7f\xbf\x4f\x83\xe8\xee\xfa\x00\x00\x7f\xfc\x47\xff\xc3\xe8\x03\x40\x3f\x4f\x83\x88\xe8\xfa\x00'
    b'\x00\x7f\xfc\x47\xff\xd3\xe8\x03\x40\x3f\x41\xff\xb8\xe8\xfa\x00\x00\x7f\xfd\xc7\xff\xd3\xe8\x03\x40\x3f\x45\xff\xa0\xe8\xfa\x00'
    b'\x00\x00\x01\x00\x00\x10\x08\x00\x40\x00\x40\x00\x20\x08\x02\x00\x00\x3f\xff\x03\xff\xf1\xf8\x01\xc0\x1f\xc0\xff\xe0\x78\xfe\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x57\x0e\xea\xe0\x99\x5d\x9d\x59\xc0\x00\x00\x00'
    b'\x00\x00\x00\x02\x54\x04\x8a\x41\x55\x51\x49\x55\x00\x00\x00\x00\x00\x00\x00\x02\x77\x04\xe4\x41\xd5\x5d\x49\x59\xc0\x00\x00\x00'
    b'\x00\x00\x00\x02\x54\x04\x8a\x41\x55\xd1\x49\x55\x00\x00\x00\x00\x00\x00\x00\x02\x57\x04\xea\x41\x58\x9d\x49\xd5\xc0\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
    128, 64, framebuf.MONO_HLSB)

#blink the blue light to let us know we're running main
led = Pin(2, Pin.OUT)
i = 0
while i < 6:
  led.value(not led.value())
  sleep(0.1)
  i = i+1

# Button handler code
async def my_butts(menu_object):
    #print("my_butts")
    pb_up.release_func(menu_object.move, (-1,))
    pb_dn.release_func(menu_object.move, ())
    pb_sl.press_func(menu_object.click, ())
    pb_bk.press_func(menu_object.reset, ())
    await asyncio.sleep(60)


    
# Initialize I2C for OLED display
print("Initializing I2C for OLED display")
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)

# Initialize OLED Display
print("Initializing OLED Display")
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

print("Flash Shenanigans")
oled.fill(0)
# Flash Shenanigans
oled.blit(shenan,0,0)
oled.show()
sleep(2)

print("Flash DEFMON")
# Flash DEFMON
oled.fill(0)
oled.blit(DMsplash,0,0)
oled.show()
sleep(2)

# Button setup
print("Setting up buttons...")
'''
pb_up = Pushbutton(Pin(26, Pin.IN, Pin.PULL_UP))
pb_dn = Pushbutton(Pin(25, Pin.IN, Pin.PULL_UP))
pb_sl = Pushbutton(Pin(27, Pin.IN, Pin.PULL_UP))
pb_bk = Pushbutton(Pin(33, Pin.IN, Pin.PULL_UP))
'''
current_party = []
defmon = []

'''
# Instanciate the SDCard on the normal slot 3 pins.
print("Instantiating SDCard")
sd = machine.SDCard(slot=3, width=1, sck=14, miso=12, mosi=13, cs=15, freq=20000)
vfs = None

try: 
    vfs=os.VfsFat(sd)
except OSError:
    print("No SDCard Detected, OSError: ", OSError)
    pass

# Mount the SDCard.
if vfs:
    print("Mounting SDCard")
    os.mount(vfs, '/sd')
    print("files on board")
    print(os.listdir('/sd'))
    # Assuming the SD card is mounted correctly, adjust the path as necessary
    #os.listdir('/sd')

    load_defdex()
    load_party()
else:
    print("skipping SDCard")

# Initialize I2C for OLED display
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
'''
# Button setup
pb_up = Pin(26, Pin.IN, Pin.PULL_UP)
pb_dn = Pin(25, Pin.IN, Pin.PULL_UP)
pb_sl = Pin(33, Pin.IN, Pin.PULL_UP)
pb_bk = Pin(27, Pin.IN, Pin.PULL_UP)

# Game data
defdex = {}
defmons = []
inventory = []
current_menu_selection = 0
high_level_menu = True
in_menu = False
in_adventure = False
in_defdex = False
current_party = []
current_location = "1-1-1"
rooms_cache = {}
defdex_selection = 0

# Load Defdex from SD card
def load_defdex():
    global defdex, defmons
    try:
        with open('/save/defdex.json', 'r') as file:
            defdex = ujson.load(file)
            defmons = [defmon["name"] for defmon in defdex["defmons"]]
    except OSError:
        defdex = {"defmons": []}
        defmons = []

def save_defdex():
    with open('/save/defdex.json', 'w') as file:
        ujson.dump(defdex, file)

def load_current_party():
    global current_party
    try:
        with open('/save/current_party.json', 'r') as file:
            current_party = ujson.load(file)
    except OSError:
        current_party = []

def save_current_party():
    with open('/save/current_party.json', 'w') as file:
        ujson.dump(current_party, file)

def save_inventory():
    with open('/save/inventory.json', 'w') as file:
        ujson.dump(inventory, file)

def load_inventory():
    global inventory
    try:
        with open('/save/inventory.json', 'r') as file:
            inventory = ujson.load(file)
    except OSError:
        inventory = []

load_defdex()
load_current_party()
load_inventory()

# Utility function to wrap text
def wrap_text(text, width):
    words = text.split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        if len(current_line) + 1 + len(word) <= width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

# Utility function to display wrapped text with scrolling
def display_text_with_scroll(text):
    wrapped_lines = wrap_text(text, 17)  # 21 characters per line for SSD1306
    total_lines = len(wrapped_lines)
    start_line = 0
    lines_per_screen = 5

    while True:
        oled.fill(0)
        for i in range(lines_per_screen):
            if start_line + i < total_lines:
                oled.text(wrapped_lines[start_line + i], 0, i * 10)
        oled.show()

        if not pb_dn.value() and start_line + lines_per_screen < total_lines:
            start_line += 1
        elif not pb_up.value() and start_line > 0:
            start_line -= 1
        elif not pb_bk.value():
            break
        time.sleep(0.1)

# Load room information from SD card and cache it
def load_room(room_name):
    if room_name in rooms_cache:
        return rooms_cache[room_name]

    room_data = {
        "description": "",
        "items": {},
        "north": "none",
        "south": "none",
        "east": "none",
        "west": "none",
        "starter1": "none",
        "starter2": "none",
        "inventory_items": [],
        "catch_attempts": 0
    }
    try:
        with open(f'/adventure/{room_name}.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if ": " in line:
                    key, value = line.split(': ', 1)
                    if key == "description":
                        room_data["description"] = value
                    elif key == "items":
                        items = value.split(', ')
                        for item in items:
                            if ": " in item:
                                item_name, item_desc = item.split(': ', 1)
                                room_data["items"][item_name] = item_desc
                    elif key == "inventory_items":
                        room_data["inventory_items"] = value.split(', ')
                    elif key == "catch_attempts":
                        room_data["catch_attempts"] = int(value)
                    else:
                        room_data[key] = value
        rooms_cache[room_name] = room_data
    except OSError:
        oled.fill(0)
        oled.text("Room file error!", 0, 0)
        oled.show()
        time.sleep(2)
    return room_data

# Display functions
menu_items = ["Adventure", "Defdex", "Credits"]

def show_high_level_menu():
    oled.fill(0)
    oled.text("Main Menu", 0, 0)
    for index, item in enumerate(menu_items):
        if index == current_menu_selection:
            oled.text("> " + item, 0, (index + 1) * 10)
        else:
            oled.text("  " + item, 0, (index + 1) * 10)
    oled.show()

def show_menu():
    oled.fill(0)
    oled.text("Game Menu", 0, 0)
    menu_items = ["View", "Search", "Move", "Use"]
    for index, item in enumerate(menu_items):
        if index == current_menu_selection:
            oled.text("> " + item, 0, (index + 1) * 10)
        else:
            oled.text("  " + item, 0, (index + 1) * 10)
    oled.show()

def show_defdex_menu():
    oled.fill(0)
    oled.text("Defdex", 0, 0)
    for index, defmon in enumerate(defdex["defmons"]):
        display_name = defmon["name"] if defmon["caught"] else "?????"
        if index == defdex_selection:
            oled.text("> " + display_name, 0, (index + 1) * 10)
        else:
            oled.text("  " + display_name, 0, (index + 1) * 10)
    oled.show()

def view_defdex_entry(defdex_entry):
    description = defdex_entry["description"]
    display_text_with_scroll(description)

def view_area(room_data):
    display_text_with_scroll(room_data["description"])

def search_area(room_data):
    if room_data["catch_attempts"] == 0:
        oled.fill(0)
        oled.text("Nothing to search for around here.", 0, 0)
        oled.show()
        time.sleep(2)
        return

    room_data["catch_attempts"] -= 1
    rooms_cache[current_location] = room_data
    oled.fill(0)
    oled.text("Searching...", 0, 0)
    oled.show()
    time.sleep(1)
    catch_defmon()

def use_item(room_data):
    items = room_data["items"]
    inventory_items = room_data.get("inventory_items", [])
    if not items:
        oled.fill(0)
        oled.text("No items to use.", 0, 0)
        oled.show()
        time.sleep(1)
        return
    
    item_names = list(items.keys())
    selected_item_index = 0

    while True:
        oled.fill(0)
        oled.text("Items in room:", 0, 0)
        for index, item in enumerate(item_names):
            if index == selected_item_index:
                oled.text("> " + item, 0, (index + 1) * 10)
            else:
                oled.text("  " + item, 0, (index + 1) * 10)
        oled.show()
        
        if not pb_up.value():
            selected_item_index = (selected_item_index - 1) % len(item_names)
            #time.sleep(0.1)
        elif not pb_dn.value():
            selected_item_index = (selected_item_index + 1) % len(item_names)
            #time.sleep(0.1)
        elif not pb_sl.value():
            selected_item = item_names[selected_item_index]
            description = items[selected_item]
            display_text_with_scroll(description)
            if selected_item in inventory_items:
                inventory.append(selected_item)
                save_inventory()
                oled.fill(0)
                oled.text(f"{selected_item} picked up!", 0, 0)
                oled.show()
        elif not pb_bk.value():
            break
        time.sleep(0.1)

def move(room_data):
    directions = {}
    for direction in ["north", "south", "east", "west"]:
        conditional_direction = f"{direction}_with_{direction}"
        if any(item in inventory for item in room_data["inventory_items"]) and conditional_direction in room_data:
            directions[direction] = room_data[conditional_direction]
        elif direction in room_data and room_data[direction] != "none":
            directions[direction] = room_data[direction]

    if not directions:
        oled.fill(0)
        oled.text("No directions to move.", 0, 0)
        oled.show()
        time.sleep(1)
        return

    selected_direction_index = 0
    direction_keys = list(directions.keys())

    while True:
        oled.fill(0)
        oled.text("Directions:", 0, 0)
        for index, direction in enumerate(direction_keys):
            if index == selected_direction_index:
                oled.text("> " + direction, 0, (index + 1) * 10)
            else:
                oled.text("  " + direction, 0, (index + 1) * 10)
        oled.show()
        
        if not pb_up.value():
            selected_direction_index -= 1
            if selected_direction_index < 0:
                selected_direction_index = len(direction_keys) - 1
            #time.sleep(0.1)
        elif not pb_dn.value():
            selected_direction_index += 1
            if selected_direction_index >= len(direction_keys):
                selected_direction_index = 0
            
        elif not pb_sl.value():
            selected_direction = direction_keys[selected_direction_index]
            global current_location
            current_location = directions[selected_direction]
            oled.fill(0)
            oled.text(f"Moved {selected_direction}.", 0, 0)
            oled.show()
            
        elif not pb_bk.value():
            break
        time.sleep(0.1)

def catch_defmon():
    oled.fill(0)
    oled.text("A wild Defmon!", 0, 0)
    defmon = random.choice(defdex["defmons"])
    oled.text(f"It's a {defmon['name']}!", 0, 10)
    oled.text("1. Throw Defball", 0, 20)
    oled.text("2. Run away", 0, 30)
    oled.show()

    while True:
        if not pb_sl.value():
            if random.randint(0, 1) == 1:
                for d in defdex["defmons"]:
                    if d["name"] == defmon["name"]:
                        d["caught"] = True
                save_defdex()
                load_defdex()
                oled.fill(0)
                oled.text(f"Caught {defmon['name']}!", 0, 0)
                oled.show()
            else:
                oled.fill(0)
                oled.text(f"{defmon['name']} escaped!", 0, 0)
                oled.show()
            
        elif not pb_bk.value():
            oled.fill(0)
            oled.text("Ran away safely.", 0, 0)
            oled.show()
            time.sleep(1)
            break
        time.sleep(0.1)

def choose_starter_defmon(room_data):
    starters = [room_data["starter1"], room_data["starter2"]]
    selected_starter_index = 0

    while True:
        oled.fill(0)
        oled.text("Choose your starter:", 0, 0)
        for index, starter in enumerate(starters):
            if index == selected_starter_index:
                oled.text("> " + starter, 0, (index + 1) * 10)
            else:
                oled.text("  " + starter, 0, (index + 1) * 10)
        oled.show()

        if not pb_up.value():
            selected_starter_index -= 1
            if selected_starter_index < 0:
                selected_starter_index = len(starters) - 1
            #time.sleep(0.1)
        elif not pb_dn.value():
            selected_starter_index += 1
            if selected_starter_index >= len(starters):
                selected_starter_index = 0
            #time.sleep(0.1)
        elif not pb_sl.value():
            selected_starter = starters[selected_starter_index]
            current_party.append(selected_starter)
            save_current_party()
            oled.fill(0)
            oled.text(f"You chose {selected_starter}!", 0, 0)
            oled.show()
        elif not pb_bk.value():
            break
        time.sleep(0.1)

def show_credits():
    credits_text = """
    Co-Creators:
    - B0rk
    - Marba$
    - yci
    - 13L4Z!N
    - FraggleRock
    - Tkdemon
    - 13L4Z!N & PirateMaal
    """
    display_text_with_scroll(credits_text.strip())

def main():
    global current_menu_selection, high_level_menu, in_menu, in_adventure, in_defdex, defdex_selection, current_location

    while True:
        if high_level_menu:
            show_high_level_menu()

        elif in_menu:
            room_data = load_room(current_location)
            show_menu()

        elif in_defdex:
            show_defdex_menu()

        if not pb_up.value():
            print('pb_up: ', pb_up.value())
            if high_level_menu or in_menu or in_defdex:
                current_menu_selection -= 1
                if current_menu_selection < 0:
                    current_menu_selection = len(menu_items) - 1 if high_level_menu else (3 if in_menu else len(defdex["defmons"]) - 1)
                if in_defdex:
                    defdex_selection = current_menu_selection

        elif not pb_dn.value():
            if high_level_menu or in_menu or in_defdex:
                current_menu_selection += 1
                if high_level_menu and current_menu_selection >= len(menu_items):
                    current_menu_selection = 0
                elif in_menu and current_menu_selection > 3:
                    current_menu_selection = 0
                elif in_defdex and current_menu_selection >= len(defdex["defmons"]):
                    current_menu_selection = 0
                if in_defdex:
                    defdex_selection = current_menu_selection

        elif not pb_sl.value():
            if high_level_menu:
                if current_menu_selection == 0:  # Adventure
                    high_level_menu = False
                    in_menu = True
                    if current_location == "3-5":
                        room_data = load_room(current_location)
                        choose_starter_defmon(room_data)
                elif current_menu_selection == 1:  # Defdex
                    high_level_menu = False
                    in_defdex = True
                elif current_menu_selection == 2:  # Credits
                    high_level_menu = False
                    show_credits()
                    high_level_menu = True  # Return to main menu after displaying credits
            elif in_menu:
                room_data = load_room(current_location)
                if current_menu_selection == 0:
                    view_area(room_data)
                elif current_menu_selection == 1:
                    search_area(room_data)
                elif current_menu_selection == 2:
                    move(room_data)
                elif current_menu_selection == 3:
                    use_item(room_data)
            elif in_defdex:
                for d in defdex["defmons"]:
                    if d["name"] == defmons[defdex_selection] or d["caught"]:
                        view_defdex_entry(d)
                        break

        elif not pb_bk.value():
            if in_menu or in_defdex:
                in_menu = False
                in_defdex = False
                high_level_menu = True
                current_menu_selection = 0
            oled.fill(0)
            oled.text("Back to main menu...", 0, 0)
            oled.show()
            show_high_level_menu()

        time.sleep(.1)

if __name__ == "__main__":
    main()
