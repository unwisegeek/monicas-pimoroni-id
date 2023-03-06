from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from machine import ADC, Pin
from time import sleep
import qrcode
import json

from pimoroni import Button

# Configure Light Sensor
lux_pwr = Pin(27, Pin.OUT)
lux_pwr.value(1)
lux = ADC(26)

# Configure Display
display = PicoGraphics(display=DISPLAY_TUFTY_2040)
WIDTH, HEIGHT = display.get_bounds()
display.set_font("sans")

# Configure Buttons
button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)
button_boot = Button(23, invert=True)

# Configure Colors
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
TEAL = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 0, 255)

CHELSEA_CUCUMBER_GREEN = display.create_pen(136, 169, 91)
UBUNTU_PURPLE = display.create_pen(119, 33, 111);

pen_color_list = [WHITE, TEAL, MAGENTA, YELLOW, RED, GREEN, BLUE]
pcl_idx = 0

# Configure Battery Sensors
vbat_adc = ADC(29)
vref_adc = ADC(28)
vref_en = Pin(27)
vref_en.init(Pin.OUT)
vref_en.value(0)

usb_power = Pin(24, Pin.IN)

FULL_BAT = 3.7
EMPTY_BAT = 2.5

def getLightRead():
    reading = lux.read_u16()
    return reading

def getVoltRead():
    pass

def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size

def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(WHITE)
    display.rectangle(ox, oy, size, size)
    display.set_pen(BLACK)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)

# State Handler - Lol
state = 1
mode = 0     # 0 - ID Card, 1 - Light Sensor, 2 - Coming Soon
selection = -1
boot_press_count = 0

counter_data = []
counter_keys = [
    'Ubuntu',
    'Kubuntu',
    'Lubuntu',
    'Budgie',
    'Kylin',
    'MATE',
    'Studio',
    'Xubuntu',
]

# Configuration
id_badge_config = {
    'line_color': WHITE,
    'bg_color': 1,
    'text_color': WHITE,
    'font': "serif",
    'qrtext':'https://www.linkedin.com/in/monica-ayhens-madon-42a63626',
}

# Main Logic
while True:
    if button_a.is_pressed:
        state = 0
    if button_b.is_pressed:
        state = 1
    if button_c.is_pressed:
        state = 2
        
    if state == 0:
        vref_en.value(1)
        # Calculate the logic supply voltage, as will be lower that the usual 3.3V when running off low batteries
        vdd = 1.24 * (65535 / vref_adc.read_u16())
        vbat = (
            (vbat_adc.read_u16() / 65535) * 3 * vdd
        )  # 3 in this is a gain, not rounding of 3.3V

        # Disable the onboard voltage reference
        vref_en.value(0)
        if button_boot.is_pressed:
            if id_badge_config['bg_color'] == 1:
                id_badge_config['bg_color'] = 2
            else:
                id_badge_config['bg_color'] = 1
        display.set_font(id_badge_config['font'])
        if id_badge_config['bg_color'] == 1:
            display.set_pen(UBUNTU_PURPLE)
        else:
            display.set_pen(CHELSEA_CUCUMBER_GREEN)
        display.clear()
        
        # Border
        display.set_pen(id_badge_config['line_color'])
        display.line(0, 0, WIDTH, 0) # Top
        display.line(0, 0, 0, HEIGHT) # Left
        display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1) # Right
        display.line(0, HEIGHT - 1, WIDTH - 1, HEIGHT - 1) # Bottom
        
        # Name Square
        display.line(0, HEIGHT // 10 * 3 + 1, WIDTH, HEIGHT // 10 * 3 + 1)
        
        # Connect/QR Border
        display.line(WIDTH // 2, HEIGHT // 10 * 3 + 1, WIDTH // 2, HEIGHT - 30)
        
        # Stats Border
        display.line(0, HEIGHT - 30, WIDTH - 1, HEIGHT - 30)
        display.line(WIDTH // 3, HEIGHT - 30, WIDTH // 3, HEIGHT - 1)
        display.line(WIDTH // 3 * 2, HEIGHT - 30, WIDTH // 3 * 2, HEIGHT - 1)

        display.set_pen(id_badge_config['text_color'])
        
        text = "Monica Ayhens-Madon"
        text_width = display.measure_text(text, .8, 0)
        display.text(text, (WIDTH - text_width) // 2, HEIGHT // 10 * 1, scale=.8)

        
        text = "Ubuntu Community Council"
        text_width = display.measure_text(text, .6, 0)
        display.text(text, (WIDTH - text_width) // 2, HEIGHT // 10 * 2, scale=.6)

        display.set_pen(BLACK)
        code = qrcode.QRCode()
        code.set_text(id_badge_config['qrtext'])
        
        qr_width, qr_height = code.get_size()
        draw_qr_code(WIDTH // 2 + 14, HEIGHT // 10 * 3 + 2, HEIGHT // 10 * 6, code)
        
        
        display.set_pen(id_badge_config['text_color'])
        
        text = "Connect"
        text_width = display.measure_text(text, .6, 0)
        display.text(text, (text_width // 2), HEIGHT // 10 * 5, scale=.6)
        
        text = "  with  "
        text_width = display.measure_text(text, .6, 0)
        display.text(text, text_width // 2, HEIGHT // 10 * 6, scale=.6)
        
        text = "LinkedIn"
        text_width = display.measure_text(text, .6, 0)
        display.text(text, text_width // 2, HEIGHT // 10 * 7, scale=.6)
        
        
        text = f"L: {getLightRead()}"
        text_width = display.measure_text(text, .6, 0)
        display.text(text, text_width // 2, HEIGHT - 15, scale=.6)
        
        if usb_power.value() == 1:
            text = " USB "
        else:
            text = f"{round(vbat, 2)}v"
        text_width = display.measure_text(text, .6, 0)
        display.text(text, (WIDTH // 3) + (text_width // 2), HEIGHT - 15, scale=.6)
        display.update()
        sleep(1)
        
    if state == 1:
        if button_down.is_pressed:
            if selection < 7:
                selection += 1
            else:
                selection = 7
        if button_up.is_pressed:
            if selection > 1:
                selection -= 1
            else:
                selection = 0
        if button_boot.is_pressed:
            boot_press_count += 1
            if boot_press_count == 10:
                with open('counter.json', 'w') as outfile:
                    counter_data = [ 0, 0, 0, 0, 0, 0, 0, 0 ]
                    counter_string = ""
                    for i in range(0, len(counter_data)):
                        counter_string += f"{counter_data[i]}" if i == len(counter_data) - 1 else f"{counter_data[i]},"
                    outfile.write(counter_string)
                print("Reinitialized counter file")
                boot_count_press = 0
        if button_b.is_pressed and selection > -1:
            counter_data[selection] += 1
            with open('counter.json', 'w') as outfile:
                counter_string = ""
                for i in range(0, len(counter_data)):
                    counter_string += f"{counter_data[i]}" if i == len(counter_data) - 1 else f"{counter_data[i]},"
                outfile.write(counter_string)
            print("Wrote selection.")
            selection = -1
        try:
            a = counter_data[0]
        except IndexError:
            try:
                with open('counter.json', 'r') as infile:
                    counter_string = infile.read().split(',')
                    counter_data = []
                    for i in range(0, len(counter_string)):
                        counter_data.append(int(counter_string[i]))
                    print(f"Read file: {counter_data}")
            except OSError:
                with open('counter.json', 'w') as outfile:
                    counter_data = [ 0, 0, 0, 0, 0, 0, 0, 0 ]
                    counter_string = ""
                    for i in range(0, len(counter_data)):
                        counter_string += f"{counter_data[i]}" if i == len(counter_data) - 1 else f"{counter_data[i]},"
                    outfile.write(counter_string)
                    print("Created file")
        display.set_pen(BLUE)
        display.clear()
        
        display.set_pen(WHITE)
        
        # Draw Boxes
        display.line(0, 0, WIDTH, 0) # Top
        display.line(0, 0, 0, HEIGHT) # Left
        display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT) # Right
        display.line(0, HEIGHT - 1, WIDTH - 1, HEIGHT - 1) # Bottom
        
        # Draw Entry Lines
        for i in range(1, 8):
            height = i * (HEIGHT // 8)
            display.line(0, height, WIDTH - 1, height)
            
        display.line(WIDTH // 10, 0, WIDTH // 10, HEIGHT) # Left divider line
        
        display.line(WIDTH - (WIDTH // 10 * 2), 0, WIDTH - ((WIDTH // 10) * 2), HEIGHT) # Right divider line
        
        for i in range(0, len(counter_data)):
            text = str(counter_data[i])
            text_width = display.measure_text(text, .6, 0)
            working_width = (WIDTH // 10) * 2
            display.text(text, WIDTH - working_width + 5, HEIGHT // 8 * (i + 1) - 10, scale=.6)
            
        
        for i in range(0, len(counter_keys)):
            text = counter_keys[i]
            text_width = display.measure_text(text, .6, 0)
            working_width = WIDTH - ((WIDTH // 10) * 3)
            left = (WIDTH // 10) + ((working_width - text_width) // 2)
            display.text(counter_keys[i], left, HEIGHT // 8 * (i + 1) - 10, scale=.6)

        if 0 <= selection:
            text = "X"
            text_width = display.measure_text(text, .6, 0)
            left = ((WIDTH // 10) - text_width) // 2
            display.text(text, left, HEIGHT // 8 * (selection + 1) - 10, scale=.6)

        display.update()
        sleep(.5)
    if state == 2:
        infile = open('counter.json', 'r')
        data = infile.read()
        infile.close()
        print(type(data))
        print(data)
        sleep(1)
