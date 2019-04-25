import key_store
from mqtt_as import MQTTClient, config
import uasyncio as asyncio
import utime
import ntptime

# Set RTC using NTP
def ntp():
    ntptime.host = key_store.get('ntp_host')
    print("NTP Server:", ntptime.host)
    while utime.time() < 10000:  # Retry until clock is set
        ntptime.settime()
        utime.sleep(1)
    print('UTC Time:   {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))

async def main(client):
    # Called once on startup
    await client.connect()
    ntp()

    # Initialize counter to publish as demo example
    n = 0

    # Main loop that publishes to broker
    while True:
        await asyncio.sleep(5)
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        await client.publish('devices/' + config['client_id'].decode('utf-8') + '/demo/timestamp', str(utime.time()), qos = 1)
        await client.publish('devices/' + config['client_id'].decode('utf-8') + '/demo/value', '{}'.format(n), qos = 1)
        n += 1

# Override default mqtt_as.py config variable settings
config['ssid']    = key_store.get('ssid_name')
config['wifi_pw'] = key_store.get('ssid_pass')
config['server']  = key_store.get('mqtt_broker')

MQTTClient.DEBUG = False  # Optional: print diagnostic messages
client = MQTTClient(config)
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
