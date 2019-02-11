# SparkFun TMP102:      https://www.sparkfun.com/products/13314
# SparkFun ESP32 Thing: https://www.sparkfun.com/products/13907
# MicroPython:          https://docs.micropython.org/en/latest/
# Source Tutorial:
#    https://learn.sparkfun.com/tutorials/micropython-programming-tutorial-getting-started-with-the-esp32-thing
#
# Brandon Gant
# 2019-02-11
#
# Usage:
#    import tmp102
#    tmp102.read_temp()
#    tmp102.read_temp('F')
#    tmp102.init()

import machine

# Pin Definitions
sda_pin = machine.Pin(21)
scl_pin = machine.Pin(22)

# Create and I2C object out of our SDA and SCL pin objects
i2c = machine.I2C(sda=sda_pin, scl=scl_pin)
i2c_addresses = i2c.scan()

# TMP102 address on the I2C bus (set by manufacturer)
tmp102_address = 0x48

if tmp102_address not in i2c_addresses:
    raise Exception('No TMP102 device found on I2C bus')

# TMP102 register addresses
reg_temp = 0x00
reg_config = 0x01


# Calculate the 2's complement of a number
def twos_comp(val, bits):
    if (val & (1 << (bits -1))) !=0:
        val = val - (1 << bits)
    return val


# Read temperature registers and calculate Celsius
def read_temp(scale='C'):  # Defaults to [C]elsius

    # Read temperature registers
    val = i2c.readfrom_mem(tmp102_address, reg_temp, 2)
    celsius = (val[0] << 4) | (val[1] >> 5)

    # Covert to 2's complement (temperatures can be negative)
    celsius = twos_comp(celsius, 12)

    # Convert registers value to temperature (C)
    celsius = celsius * 0.0625

    # Outputs Celius by default, but you can specify other scales
    if scale.lower() == 'c':
        return celsius
    elif scale.lower() == 'f':
        fahrenheit = (celsius * 9/5) + 32 
        return fahrenheit
    elif scale.lower() == 'k':
        kelvin = celsius + 273.15
        return kelvin
    else:
        print("valid values are [C]elsius, [F]ahrenheit, or [K]elvin")


# Reset TMP102 configuration settings
def init():

    # Read CONFIG register (2 bytes) and convert to integer list
    val = i2c.readfrom_mem(tmp102_address, reg_config, 2)
    print("Old CONFIG:", val)
    val = list(val)

    # Set to 4Hz sampling (CR1, CR0 = 0b10)
    val[1] = val[1] & 0b00111111
    val[1] = val[1] | (0b10 << 6)

    # Write 4Hz sampling back to CONFIG
    i2c.writeto_mem(tmp102_address, reg_config, bytearray(val))

    # Check that new config is in place
    val = i2c.readfrom_mem(tmp102_address, reg_config, 2)
    print("New CONFIG:", val)

