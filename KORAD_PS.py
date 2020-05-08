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
def open_serial(device):
    ps = serial.Serial(device,
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    # ps.flush()  # was there originally, works without for me
    return ps


def get_float(device, prop):
    ps = open_serial(device)
    ps.write(prop)  # Request the prop
    # time.sleep(0.015)  # was there originally, works without for me
    while True:
        try:
            value = ps.read(5)
            ps.flush()
            if value == b'':
                value = b'0'
            value = float(value)
            break
        except ValueError:
            print('<invalid>')
    return value


def get_set_voltage(device):
    return get_float(device, REQUEST_SET_VOLTAGE)


def get_set_current(device):
    return get_float(device, REQUEST_SET_CURRENT)


def set_and_check(device, value, prop, format_str, get_fn):
    ps = open_serial(device)
    value_formatted = format_str.format(float(value))
    output_string = prop + bytes(value_formatted, "utf-8")
    while True:
        ps.write(output_string)
        ps.flush()
        time.sleep(0.15)
        value_verify = format_str.format(get_fn(device))  # Verify ps accepted
        if value_verify == value_formatted:
            break


def set_voltage(device, voltage):
    set_and_check(device, voltage, SET_VOLTAGE, "{:2.2f}", get_set_voltage)


def set_current(device, current):
    set_and_check(device, current, SET_CURRENT, "{:2.3f}", get_set_current)


def get_actual_voltage(device):
    return get_float(device, REQUEST_ACTUAL_VOLTAGE)


def get_actual_current(device):
    return get_float(device, REQUEST_ACTUAL_CURRENT)


def set_bool(device, prop, value):
    ps = open_serial(device)
    output_string = prop + value
    ps.write(output_string)
    time.sleep(0.15)
    ps.flush()


def set_ovp(device, on_off):
    set_bool(device, SET_OVP, on_off)


def set_ocp(device, on_off):
    set_bool(device, SET_OCP, on_off)


def set_output(device, on_off):
    set_bool(device, SET_OUTPUT, on_off)


# ==============================================================================
# Additional Methods (unused for core functionality)
# ==============================================================================
def get_id(device):
    ps = open_serial(device)
    ps.write(REQUEST_ID)  # Request the ID from the Power Supply
    psid = ps.read(16)
    ps.flush()
    return psid


def get_status(device):
    ps = open_serial(device)
    ps.write(REQUEST_STATUS)  # Request the status of the ps
    stat = str(ps.read(5))
    ps.flush()
    return stat


# ==============================================================================
# Variables
# ==============================================================================
VMAX = 5
IMAX = 3.0


# ==============================================================================
# Argument parsing
# ==============================================================================
def add_bool_arg(parser, name, descriptive_name, default=False):
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=name, action='store_true',
                       help='Activate ' + descriptive_name)
    group.add_argument('--no-' + name, dest=name, action='store_false',
                       help='Deactivate ' + descriptive_name)
    parser.set_defaults(**{name: default})


parser = argparse.ArgumentParser(description='Korad-KA6003P power supply control tool')

parser.add_argument('--device', dest='device', default="/dev/ttyACM0",
                    help='Serial device (default \"/dev/ttyACM0\")')
parser.add_argument('--volt', dest='volt', type=float, default=5.0,
                    help='Target voltage (default 5V)')
parser.add_argument('--current', dest='current', type=float, default=2.0,
                    help='Maximum current (default 2A)')
add_bool_arg(parser, 'ovp', 'Over Voltage Protection')
add_bool_arg(parser, 'ocp', 'Over Current Protection')
add_bool_arg(parser, 'out', 'Output')

args = parser.parse_args()

# ==============================================================================
# Set request voltage/current
# ==============================================================================
set_voltage(args.device, args.volt if args.volt <= VMAX else VMAX)

curr = args.current if args.current <= IMAX else IMAX
current_formatted = "{0:.3f}".format(float(curr))
set_current(args.device, curr)

set_ovp(args.device, b'1' if args.ovp else b'0')
set_ocp(args.device, b'1' if args.ocp else b'0')
set_output(args.device, b'1' if args.out else b'0')


# ==============================================================================
# Poll loop for reading actual values
# ==============================================================================
while True:
    volt_measured = "{:2.2f}".format(get_actual_voltage(args.device))
    current_measured = "{0:.3f}".format(get_actual_current(args.device))
    unix_ms = int(round(time.time() * 1000))
    print(str(unix_ms) + ";" + str(volt_measured) + ";" + str(current_measured))
