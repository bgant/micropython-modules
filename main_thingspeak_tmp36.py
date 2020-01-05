#
# Brandon Gant
# 2019-12-17
#
# Espressif ESP8266-DevKitc_V1 board with ESP-WROOM-02D chip
# Espressif ESP32-PICO-KIT_V4.1 board with ESP32-PICO-D4 chip 
# TMP36 temperature sensor with Vout connected to ADC pin
#

import key_store
import AnalogDevices_TMP36 as tmp36
from time import sleep
from sys import exit
from machine import reset

# Get Unique Machine ID
from ubinascii import hexlify
from machine import unique_id
client_id = hexlify(unique_id()).decode('utf-8')  # String with Unique Client ID
print('Client ID:', client_id)

# Check hardware
from uos import uname
hardware = uname().sysname
if 'esp32' in hardware:
    import urequests
elif 'esp8266' in hardware:
    # No urequests in ESP8266 Micropython
    import http_client
else:
    print('Not test with', hardware)
    exit(1)

#server = 'api.thingspeak.com'
server = '192.168.7.100'
#port = '44301' # HTTPS
port = '8001'   # HTTP

# ThingSpeak free tier limited to 15 seconds between data updates
sleep_interval = 60   # Seconds
periodic_reset = 360  # with 60 second sleep, reset every 6 hours (just in case)


def main():
    print('=============================================')
    print()

    # Read the Temperature
    from uos import uname
    hardware = uname().sysname
    if 'esp32' in hardware:
        tempf = round(tmp36.read_temp(37,'F'), 1)
    elif 'esp8266' in hardware:
        tempf = round(tmp36.read_temp(0,'F'), 1)
    print('Temperature Reading: %sF' % tempf)

    # Send the Data to Server
    print('Sending Data To: %s:%s' % (server, port))
    if 'esp32' in hardware:
        if '443' in port:
            transport = 'https://'
        else:
            transport = 'http://'
        URL = transport + server + ':' + port + '/update?api_key=' + client_id + '&field1=' + str(tempf)
        r = urequests.get(URL)
        response_text = r.text
        status = str(r.status_code)
    elif 'esp8266' in hardware:
        # Create the GET Request string
        get_request = 'GET /update?api_key=' + client_id + '&field1=' + str(tempf) + ' HTTP/1.0\r\n\r\n'
        get_request = str.encode(get_request)  # Convert Type str to bytes
        response_text = http_client.send_data(server, get_request)
        #print(response_text)
        status = [ line for line in response_text.split('\r\n') if "Status" in line ]
        status = status[0]

    if '200' in status:
        print('Status: Success')
        print()
    else:
        print('Status: Failed')
        sleep(sleep_interval)
        reset()


counter = 0
while True:
    try:
        main()
        counter += 1
        sleep(0.5)  # Give a half-second to display output before device sleeps
        sleep(sleep_interval)

        if counter > periodic_reset:  # Reset on a schedule just in case
            reset() 
    except:
        sleep(sleep_interval)
        reset()

