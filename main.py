from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from machine import ADC, Pin
from time import sleep
import time
import qrcode

from pimoroni import Button
from pimoroni_i2c import PimoroniI2C
from breakout_sgp30 import BreakoutSGP30

# Configure Light Sensor
lux_pwr = Pin(27, Pin.OUT)
lux_pwr.value(1)
lux = ADC(26)

# Configure CO2 Sensor
PINS_BREAKOUT_GARDEN = {
    "sda": 4,
    "scl": 5,
    } # i2c pins 4, 5  for breakout garden
PINS_PICO_EXPLORER = {
    "sda": 20,
    "scl": 21,
    } # i2c pins for pico explorer

i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
sgp30 = BreakoutSGP30(i2c)
        
sgp30.start_measurement(False)

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
state = 0 # 0 - ID Card, 1 - Light Sensor, 2 - Coming Soon
mode = 0  # Individual modes for each state, dictated by up and down arrows    
selection = -1
boot_press_count = 0
modes = [[0, 1], [0]]

counter_data = []
counter_keys = [
    'Ubuntu',
    'Kubuntu',
    'Lubuntu',
    'Budgie',
    'Unity',
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

voting_config = {
    'bg_color': UBUNTU_PURPLE,
    'text_color': WHITE,
    'font': 'serif',
    'line_color': WHITE,
    }

# Main Logic
while True:
    if button_a.is_pressed:
        state = 0
        mode = 0
    if button_b.is_pressed:
        state = 1
        mode = 0
    if button_c.is_pressed:
        state = 2
        mode = 0
        
    if button_down.is_pressed:
        if mode > 0:
            mode -= 1
        elif mode == 0:
            mode = modes[state][-1]
    if button_up.is_pressed:
        if mode < modes[state][len(modes[state]) - 1]:
            mode += 1
        elif mode == modes[state][len(modes[state]) - 1]:
            mode = 0
    
    if state == 0:
        if mode == 0:
            vref_en.value(1)
            # Calculate the logic supply voltage, as will be lower that the usual 3.3V when running off low batteries
            vdd = 1.24 * (65535 / vref_adc.read_u16())
            vbat = (
                (vbat_adc.read_u16() / 65535) * 3 * vdd
            )  # 3 in this is a gain, not rounding of 3.3V

            # Disable the onboard voltage reference
            vref_en.value(0)
            
            # Get air quality reading
            air_quality = sgp30.get_air_quality()
            
            if button_boot.is_pressed:
                if id_badge_config['bg_color'] == 1:
                    id_badge_config['bg_color'] = 2
                else:
                    id_badge_config['bg_color'] = 1
            display.set_font(id_badge_config['font'])
            display.set_pen(UBUNTU_PURPLE if id_badge_config['bg_color'] == 1 else CHELSEA_CUCUMBER_GREEN)
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
            
            print(air_quality[BreakoutSGP30.ECO2])
            text = f"{str(air_quality[BreakoutSGP30.ECO2])}ppm"
            text_width = display.measure_text(text, .6, 0)
            display.text(text, ((WIDTH // 3) * 2 - 20) + (text_width // 2), HEIGHT - 15, scale=.6)
            
            display.update()
        
        if mode == 1:
            display.set_pen(UBUNTU_PURPLE if id_badge_config['bg_color'] == 1 else CHELSEA_CUCUMBER_GREEN)
            display.clear()
            display.set_pen(BLACK)
            
            code = qrcode.QRCode()
            code.set_text(id_badge_config['qrtext'])
            
            size, module_size = measure_qr_code(HEIGHT, code)
            left = int((WIDTH // 2) - (size // 2))
            top = int((HEIGHT // 2) - (size // 2))
            draw_qr_code(left, top, HEIGHT, code)
            display.update()

        sleep(1)
            
        
    if state == 1:
        options = [0, 1, 2, 3, 4, 5, 6, 7]
        if button_down.is_pressed:
            if selection == options[-1]:
                selection = 0
            elif selection > -1:
                selection += 1
            elif selection == -1:
                selection = 0
                
        if button_up.is_pressed:
            if selection == 0:
                selection = options[-1]
            elif selection > 0:
                selection -= 1
            elif selection == -1:
                selection = options[-1]
        print(selection)
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
        display.set_pen(voting_config['bg_color'])
        display.clear()
        
        display.set_pen(voting_config['line_color'])
        
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
        
        # Draw Text
        display.set_pen(voting_config['text_color'])
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
        state = 0
