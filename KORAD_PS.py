# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 23:05:05 2014

@author: jason, mpoell
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
def open_serial():
    ps = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    # ps.flush()  # was there originally, works without for me
    return ps


def get_float(prop):
    ps = open_serial()
    ps.write(prop)  # Request the prop
    # time.sleep(0.015)  # was there originally, works without for me
    value = ps.read(5)
    if value == b'':
        value = b'0'
    value = float(value)
    ps.flush()
    return value


def get_set_voltage():
    return get_float(REQUEST_SET_VOLTAGE)


def get_set_current():
    return get_float(REQUEST_SET_CURRENT)


def set_and_check(value, prop, format_str, get_fn):
    ps = open_serial()
    value_formatted = format_str.format(float(value))
    output_string = prop + bytes(value_formatted, "utf-8")
    while True:
        ps.write(output_string)
        ps.flush()
        time.sleep(0.15)
        value_verify = format_str.format(float(get_fn()))  # Verify ps accepted
        if value_verify == value_formatted:
            break
    return output_string


def set_voltage(voltage):
    return set_and_check(voltage, SET_VOLTAGE, "{:2.2f}", get_set_voltage)


def set_current(current):
    return set_and_check(current, SET_CURRENT, "{:2.3f}", get_set_current)


def get_actual_voltage():
    return get_float(REQUEST_ACTUAL_VOLTAGE)


def get_actual_current():
    return get_float(REQUEST_ACTUAL_CURRENT)


# ==============================================================================
# Additional Methods (unused for core functionality)
# ==============================================================================
def get_id():
    ps = open_serial()
    ps.write(REQUEST_ID)  # Request the ID from the Power Supply
    psid = ps.read(16)
    ps.flush()
    return psid


def get_status():
    ps = open_serial()
    ps.write(REQUEST_STATUS)  # Request the status of the ps
    stat = str(ps.read(5))
    ps.flush()
    return stat


def set_op(on_off):
    ps = open_serial()
    output_string = SET_OUTPUT + bytes(on_off, "utf-8")
    ps.write(output_string)
    ps.flush()
    return output_string


def set_ovp(on_off):
    ps = open_serial()
    output_string = SET_OVP + on_off
    ps.write(output_string)
    ps.flush()
    return output_string


def set_ocp(on_off):
    ps = open_serial()
    output_string = SET_OCP + on_off
    ps.write(output_string)
    ps.flush()
    return output_string


# ==============================================================================
# Variables
# ==============================================================================
VMAX = 5
IMAX = 3.0


# ==============================================================================
# Argument parsing
# ==============================================================================
parser = argparse.ArgumentParser(description='Korad-KA6003P power supply control tool')
parser.add_argument('--volt', dest='volt', type=float, default=5.0,
                    help='Target voltage (default 5V)')
parser.add_argument('--current', dest='current', type=float, default=2.0,
                    help='Maximum current (default 2A)')
args = parser.parse_args()


# ==============================================================================
# Set request voltage/current
# ==============================================================================
set_voltage(args.volt if args.volt <= VMAX else VMAX)

curr = args.current if args.current <= IMAX else IMAX
current_formatted = "{0:.3f}".format(float(curr))
set_current(curr)


# ==============================================================================
# Poll loop for reading actual values
# ==============================================================================
while True:
    volt_measured = "{:2.2f}".format(get_actual_voltage())
    current_measured = "{0:.3f}".format(get_actual_current())
    unix_ms = int(round(time.time() * 1000))
    print(str(unix_ms) + ";" + str(volt_measured) + ";" + str(current_measured))
