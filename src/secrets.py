SSID = ''  # your wifi network name
PASS = ''  # your wifi password
API_KEY = ''  # your octoprint api key

if not SSID or not PASS or not API_KEY:
    raise Exception('Make sure you set all these values!')