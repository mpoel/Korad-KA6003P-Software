# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 23:05:05 2014

@author: jason
"""

import serial
import time
import argparse

# ==============================================================================
# Define protocol commands
# ==============================================================================
REQUEST_STATUS = b"STATUS?"  # Request actual status.
# 0x40 (Output mode: 1:on, 0:off)
# 0x20 (OVP and/or OCP mode: 1:on, 0:off)
# 0x01 (CV/CC mode: 1:CV, 0:CC)
REQUEST_ID = b"*IDN?"

REQUEST_SET_VOLTAGE = b"VSET1?"  # request the set voltage
REQUEST_ACTUAL_VOLTAGE = b"VOUT1?"  # Request output voltage

REQUEST_SET_CURRENT = b"ISET1?"  # Request the set current
REQUEST_ACTUAL_CURRENT = b"IOUT1?"  # Requst the output current

SET_VOLTAGE = b"VSET1:"  # Set the maximum output voltage
SET_CURRENT = b"ISET1:"  # Set the maximum output current

SET_OUTPUT = b"OUT"  # Enable the power output

SET_OVP = b"OVP"  # Enable(1)/Disable(0) OverVoltageProtection

SET_OCP = b"OCP"  # Enable(1)/Disable(0) OverCurrentProtection


# ==============================================================================
# Methods
# ==============================================================================
def get_id():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    ps.write(REQUEST_ID)  # Request the ID from the Power Supply
    psid = ps.read(16)
    ps.flushInput()
    return psid


def get_i_set():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    ps.write(REQUEST_SET_CURRENT)  # Request the target current
    i_set = ps.read(5)
    if i_set == b'':
        i_set = b'0'
    i_set = float(i_set)
    ps.flushInput()
    return i_set


def get_v_set():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    ps.write(REQUEST_SET_VOLTAGE)  # Request the target voltage
    v_set = float(ps.read(5))
    ps.flushInput()
    return v_set


def get_status():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    ps.write(REQUEST_STATUS)  # Request the status of the ps
    stat = str(ps.read(5))
    ps.flushInput()
    return stat


def set_voltage(voltage):
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    if float(voltage) > float(VMAX):
        voltage = VMAX
    voltage = "{:2.2f}".format(float(voltage))
    output_string = SET_VOLTAGE + bytes(voltage, "utf-8")
    ps.write(output_string)
    ps.flushInput()
    time.sleep(0.2)
    veri_volt = "{:2.2f}".format(float(get_v_set()))  # Verify ps accepted
    while veri_volt != voltage:
        ps.write(output_string)  # Try one more time
    return output_string


def set_current(current):
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    if float(current) > float(IMAX):
        current = IMAX
    current = "{:2.3f}".format(float(current))
    output_string = SET_CURRENT + bytes(current, "utf-8")
    ps.write(output_string)
    ps.flushInput()
    time.sleep(0.2)
    veri_amp = "{:2.3f}".format(float(get_i_set()))
    # if veri_amp != current:
    #     veri_amp = 0.00
    return output_string


def v_actual():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    ps.write(REQUEST_ACTUAL_VOLTAGE)  # Request the actual voltage
    time.sleep(0.015)
    v_actual = ps.read(5)
    if v_actual == b'':
        v_actual = b'0'  # deal with the occasional NULL from ps
    v_actual = float(v_actual)
    ps.flushInput()
    return v_actual


def i_actual():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    ps.write(REQUEST_ACTUAL_CURRENT)  # Request the actual current
    time.sleep(0.015)
    i_actual = ps.read(5)
    if i_actual == b'':
        i_actual = b'0'  # deal with the occasional NULL from ps
    i_actual = float(i_actual)
    ps.flushInput()
    return i_actual


def set_op(on_off):
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    output_string = SET_OUTPUT + bytes(on_off, "utf-8")
    ps.write(output_string)
    ps.flushInput()
    return output_string


def set_ovp(on_off):
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    output_string = SET_OVP + on_off
    ps.write(output_string)
    ps.flushInput()
    return output_string


def set_ocp(on_off):
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    ps.flushInput()
    output_string = SET_OCP + on_off
    ps.write(output_string)
    ps.flushInput()
    return output_string


def update_v_and_i():
    volt_measured = "{:2.2f}".format(v_actual())
    current_measured = "{0:.3f}".format(i_actual())
    print(str(int(round(time.time() * 1000))) + ";" + str(volt_measured) + ";" + str(current_measured))


def set_v_a(volt, current):
    set_voltage(volt)
    if current == '':
        current = b'0'
    current = "{0:.3f}".format(float(current))
    set_current(current)


# ==============================================================================
# Variables
# ==============================================================================
V_set = "{0:.2f}".format(get_v_set(), 'V')
I_set = "{0:.3f}".format(get_i_set(), 'I')
PSID = get_id()
Stat = get_status()
VMAX = '05'
IMAX = '3.0'

parser = argparse.ArgumentParser(description='Korad-KA6003P power supply control tool')
parser.add_argument('--volt', dest='volt', default='5',
                    help='Target voltage (default 5V)')
parser.add_argument('--current', dest='current', default='2.0',
                    help='Maximum current (default 2A)')
args = parser.parse_args()

# ==============================================================================
# Set request voltage/current and poll loop for reading actual values
# ==============================================================================
set_v_a(args.volt, args.current)
time.sleep(1)
while 1 == 1:
    update_v_and_i()
