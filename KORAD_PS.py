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
def get_float(ps, prop):
    # time.sleep(0.015)  # was there originally, works without for me
    while True:
        try:
            ps.write(prop)  # Request the prop
            value = ps.read(5)
            ps.flush()
            if value == b'':
                value = b'0'
            value = float(value)
            break
        except ValueError:
            print('<invalid>')
    return value


def get_set_voltage(ps):
    return get_float(ps, REQUEST_SET_VOLTAGE)


def get_set_current(ps):
    return get_float(ps, REQUEST_SET_CURRENT)


def set_and_check(ps, value, prop, format_str, get_fn):
    value_formatted = format_str.format(float(value))
    output_string = prop + bytes(value_formatted, "utf-8")
    while True:
        ps.write(output_string)
        ps.flush()
        time.sleep(0.15)
        value_verify = format_str.format(get_fn(ps))  # Verify ps accepted
        if value_verify == value_formatted:
            break


def set_voltage(ps, voltage):
    set_and_check(ps, voltage, SET_VOLTAGE, "{:2.2f}", get_set_voltage)


def set_current(ps, current):
    set_and_check(ps, current, SET_CURRENT, "{:2.3f}", get_set_current)


def get_actual_voltage(ps):
    return get_float(ps, REQUEST_ACTUAL_VOLTAGE)


def get_actual_current(ps):
    return get_float(ps, REQUEST_ACTUAL_CURRENT)


def set_bool(ps, prop, value):
    output_string = prop + value
    ps.write(output_string)
    time.sleep(0.15)
    ps.flush()


def set_ovp(ps, on_off):
    set_bool(ps, SET_OVP, on_off)


def set_ocp(ps, on_off):
    set_bool(ps, SET_OCP, on_off)


def set_output(ps, on_off):
    set_bool(ps, SET_OUTPUT, on_off)


# ==============================================================================
# Additional Methods (unused for core functionality)
# ==============================================================================
def get_id(ps):
    ps.write(REQUEST_ID)  # Request the ID from the Power Supply
    psid = ps.read(16)
    ps.flush()
    return psid


def get_status(ps):
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
parser.add_argument('--poll-interval', dest='poll_interval', type=int, default="100",
                    help='Poll interval in milliseconds')
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
power_supply = serial.Serial(args.device,
                             baudrate=9600,
                             bytesize=8,
                             parity='N',
                             stopbits=1,
                             timeout=1)

set_voltage(power_supply, args.volt if args.volt <= VMAX else VMAX)

curr = args.current if args.current <= IMAX else IMAX
current_formatted = "{0:.3f}".format(float(curr))
set_current(power_supply, curr)

set_ovp(power_supply, b'1' if args.ovp else b'0')
set_ocp(power_supply, b'1' if args.ocp else b'0')
set_output(power_supply, b'1' if args.out else b'0')


# ==============================================================================
# Poll loop for reading actual values
# ==============================================================================

while True:
    ts_before_read_ms = int(round(time.time() * 1000))
    volt_measured = "{:2.2f}".format(get_actual_voltage(power_supply))
    current_measured = "{0:.3f}".format(get_actual_current(power_supply))
    ts_after_read_ms = int(round(time.time() * 1000))
    print(str(ts_after_read_ms) + ";" + str(volt_measured) + ";" + str(current_measured))
    wait_ms = max(args.poll_interval - (ts_after_read_ms - ts_before_read_ms), 0)
    time.sleep(wait_ms / 1000.0)
