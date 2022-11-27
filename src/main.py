import time
from neopixel import Neopixel
from machine import Pin
import network
import urequests as requests
import json
from secrets import SSID, PASS, API_KEY

led = Pin("LED", Pin.OUT)

# Neopixel control
NUM_PIXELS = 8
PIXEL_DATA = 28

# Neopixel colors
GREEN = (255, 0, 0, 0)

# Connect to internet network
# https://www.tomshardware.com/how-to/connect-raspberry-pi-pico-w-to-the-internet
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASS)

# https://www.freva.com/how-to-control-a-neopixel-led-strip-with-a-raspberry-pi-pico/
pixels = Neopixel(NUM_PIXELS, 0, PIXEL_DATA, 'RGBW')
pixels.brightness(25)

octo_url = 'http://octopi.local'


def octoprint_request(token, url_base, url_ext, method='GET'):
    '''Sends request to octoprint server. This is how we
    get printer information to display later.
    '''
    api_url = '{}/{}'.format(url_base, url_ext)

    headers = {
             'Content-Type': 'application/json',
             'X-Api-Key': token
              }
    data = {}
    
    # returns a request object not json dictionary, need to convert
    # later using `get_to_json`
    return requests.request(method, api_url, headers=headers, data=data)

def get_to_json(request):
    return json.loads(request.text)


def all_pixels_off(pixels, num_pixels):
    for i in range(num_pixels):
        pixels.set_pixel(num_pixels - (i+1), (0, 0, 0, 0))
        pixels.show()
        time.sleep(0.2)
    
    

def display_job_status(pixels, num_pixels, job_status, color, delay=0.5):
    '''Use neopixel to display the job status. If a job is running
    represent its percent completion by lighting up run of
    pixels corresponding to that percentage. If there is no job running
    then show all pixels as red.
    '''
    job_dict = get_to_json(job_status)

    print(job_dict['progress']['completion'])
    
    # Job is running
    if job_dict['progress']['completion']:
        # calculation percent done
        print_time = job_dict['progress']['printTime']
        print_time_left = job_dict['progress']['printTimeLeft']
        num_lit_leds = int((print_time / (print_time_left + print_time)) * num_pixels)
        # Light up at least 1 LED
        if num_lit_leds < 1:
            num_lit_leds = 1
        # sequentially light up rest of leds representing percent complete
        for i in range(0, num_lit_leds):
            pixels.set_pixel(i, color)
            pixels.show()
            time.sleep(delay)
            if i == num_lit_leds - 1:
                # Flash the last led three times 
                for k in range(3):
                    pixels.set_pixel(i, (0, 0, 0, 0))
                    pixels.show()
                    time.sleep(delay)
                    pixels.set_pixel(i, color)
                    pixels.show()
                    time.sleep(delay)
            
        all_pixels_off(pixels, num_pixels)
        time.sleep(10)
        return True
    else:
        pixels.fill((0, 255, 0, 0))
        pixels.show()
        time.sleep(5)
        all_pixels_off(pixels, num_pixels)
        time.sleep(30)
        return False

# main loop

all_pixels_off(pixels, NUM_PIXELS)

# flash onboard LED
for _ in range(3):
    led.on()
    time.sleep(0.3)
    led.off()
    time.sleep(0.2)

led.off()

while True:
    try:
        job_status = octoprint_request(
            API_KEY,
            octo_url,
            'api/job'
            )
        displayed_job_status = display_job_status(
            pixels,
            NUM_PIXELS,
            job_status,
            GREEN)
    except Exception as e:
        led.on()
        time.sleep(10)
        led.off()
        
   



