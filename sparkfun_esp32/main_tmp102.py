# SparkFun ESP32 Thing: https://www.sparkfun.com/products/13907
# MicroPython:          https://docs.micropython.org/en/latest/
#
# Brandon Gant
# 2019-03-28
#
# Usage:
#    ampy -p /dev/ttyUSB0 put main_tmp102.py /main.py
#
# Temperature Logger:
# This script uses a TMP102 sensor to check the temperature every five minutes
# and log the results to an MQTT server as well as locally.
#

import utime
print('main.py: Press CTRL+C to drop to REPL...')
utime.sleep(3)

try:
    import btree
    import client
    import machine
    import mqtt
    import tmp102

    unique_id = str(client.id())

    f = open('key_store.db', 'r+b')
    db = btree.open(f)

    broker = db[b'mqtt_broker'].decode('utf-8')
    topic = 'devices/' + unique_id

    timestamp = utime.time()   # Epoch UTC
    mqtt.publish(broker, topic + '/temp/timestamp', str(timestamp)) 

    temp = round(tmp102.read_temp('F'), 1)
    mqtt.publish(broker, topic + '/temp/value', str(temp))

    db[str(timestamp)] = str(temp) 
    db.flush()
    db.close()

    print(timestamp, temp)
    utime.sleep(1)  # Give UART time to print text before going to sleep
    machine.deepsleep(300000)    # Reset on Wake

except:
    print('Error... sleeping again')
    machine.deepsleep(300000) 
