# The MIT License (MIT)
#
# Copyright (c) 2019 Tavish Naruka <tavish@electronut.in> for Electronut Labs (electronut.in)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`electronutlabs_ltr329als01`
================================================================================

Circuitpython library for reading data from light sensor LTR329ALS01.


* Author(s): Tavish Naruka <tavish@electronut.in>

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports
import time

from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/electronut/Electronutlabs_CircuitPython_LTR329ALS01.git"

# pylint: disable=bad-whitespace
LTR_ADDRESS                 = const(0x29)

REG_ALS_CONTR               = const(0x80)
REG_ALS_MEAS_RATE           = const(0x85)
REG_ALS_DATA_CH1_0          = const(0x88)
REG_ALS_DATA_CH1_1          = const(0x89)
REG_ALS_DATA_CH0_0          = const(0x8A)
REG_ALS_DATA_CH0_1          = const(0x8B)
REG_ALS_STATUS              = const(0x8C)

CONST_GAIN_1X               = const(0x00)
CONST_GAIN_2X               = const(0x01)
CONST_GAIN_4X               = const(0x02)
CONST_GAIN_8X               = const(0x03)
CONST_GAIN_48X              = const(0x06)
CONST_GAIN_96X              = const(0x07)

CONST_INT_50                = const(0x01)
CONST_INT_100               = const(0x00)
CONST_INT_150               = const(0x04)
CONST_INT_200               = const(0x02)
CONST_INT_250               = const(0x05)
CONST_INT_300               = const(0x06)
CONST_INT_350               = const(0x07)
CONST_INT_400               = const(0x03)

CONST_RATE_50               = const(0x00)
CONST_RATE_100              = const(0x01)
CONST_RATE_200              = const(0x02)
CONST_RATE_500              = const(0x03)
CONST_RATE_1000             = const(0x04)
CONST_RATE_2000             = const(0x05)

class LTR329ALS01:
    """Driver for the LTR329ALS01 ambient light sensor."""

    def __init__(self, i2c, gain = CONST_GAIN_1X, integration = CONST_INT_100, rate = CONST_RATE_500):
        import adafruit_bus_device.i2c_device as i2c_device
        self._i2c = i2c_device.I2CDevice(i2c, LTR_ADDRESS)
        self._buffer = bytearray(2)
        self._gain = gain
        self._integration = integration
        self._rate = rate

        # just in case it we are just starting, choip needs 10ms after boot
        time.sleep(0.1)

        self._write_register_byte(REG_ALS_CONTR, self._get_contr(gain))
        self._write_register_byte(REG_ALS_MEAS_RATE, self._get_meas_rate(integration, rate))

        time.sleep(0.01)

    def _get_gain(self, gain):
        if gain == CONST_GAIN_1X:  return 1
        if gain == CONST_GAIN_2X:  return 2
        if gain == CONST_GAIN_4X:  return 4
        if gain == CONST_GAIN_8X:  return 8
        if gain == CONST_GAIN_48X: return 48
        if gain == CONST_GAIN_96X: return 96

    def _get_integration(self, integration):
        if integration == CONST_INT_50:  return 50
        if integration == CONST_INT_100: return 100
        if integration == CONST_INT_150: return 150
        if integration == CONST_INT_200: return 200
        if integration == CONST_INT_250: return 250
        if integration == CONST_INT_300: return 300
        if integration == CONST_INT_350: return 350
        if integration == CONST_INT_400: return 400

    def _get_rate(self, rate):
        if rate == CONST_RATE_50:   return 50
        if rate == CONST_RATE_100:  return 100
        if rate == CONST_RATE_200:  return 200
        if rate == CONST_RATE_500:  return 500
        if rate == CONST_RATE_1000: return 1000
        if rate == CONST_RATE_2000: return 2000

    def _get_contr(self, gain):
        return ((gain & 0x07) << 2) + 0x01

    def _get_meas_rate(self, integration, rate):
        return ((integration & 0x07) << 3) + (rate & 0x07)

    def _read_register(self, register):
        self._buffer[0] = register & 0xFF
        with self._i2c as i2c:
            i2c.write(self._buffer, start=0, end=1)
            i2c.readinto(self._buffer, start=0, end=1)
            return self._buffer[1]

    def _write_register_byte(self, register, value):
        self._buffer[0] = register & 0xFF
        self._buffer[1] = value & 0xFF
        with self._i2c as i2c:
            i2c.write(self._buffer, start=0, end=2)
    
    def _combine_word(self, high, low):
        return ((high & 0xFF) << 8) + (low & 0xFF)

    def get_lux(self):
        ch1low = self._read_register(REG_ALS_DATA_CH1_0)
        ch1high = self._read_register(REG_ALS_DATA_CH1_1)
        data1 = int(self._combine_word(ch1high, ch1low))

        ch0low = self._read_register(REG_ALS_DATA_CH0_0)
        ch0high = self._read_register(REG_ALS_DATA_CH0_1)
        data0 = int(self._combine_word(ch0high, ch0low))

        als_int = float(self._get_integration(self._integration)) / 100.0
        als_gain = self._get_gain(self._gain)

        f_data0 = float(data0)
        f_data1 = float(data1)
        ratio = f_data1 / (f_data1 + f_data0)

        if ratio < 0.45:
            als_lux = (1.7743 * f_data0 + (1.1059 * f_data1)) / (als_gain * als_int)
        elif ratio < 0.64 and ratio >= 0.45:
            als_lux = (4.2785 * f_data0 - (1.9548 * f_data1)) / (als_gain * als_int)
        elif ratio < 0.85 and ratio >= 0.64:
            als_lux = (0.5926 * f_data0 + (0.1185 * f_data1)) / (als_gain * als_int)
        else:
            als_lux = 0.0
        
        return als_lux
