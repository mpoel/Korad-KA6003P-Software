# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 23:05:05 2014

@author: jason
"""

import serial
import time
import argparse

#==============================================================================
# Define protocol commands
#==============================================================================
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

#==============================================================================
# Methods
#==============================================================================


def GetID():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_ID)  # Request the ID from the Power Supply
    PSID = PS.read(16)
    # print(b'PSID = '+PSID)
    PS.flushInput()
    return(PSID)


def Get_I_Set():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_SET_CURRENT)  # Request the target current
    I_set = PS.read(5)
    if (I_set == b''):
        I_set = b'0'
    I_set = float(I_set)
    # print(str('Current is set to ')+str(I_set))
    PS.flushInput()
    return(I_set)


def Get_V_Set():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_SET_VOLTAGE)  # Request the target voltage
    V_set = float(PS.read(5))
    # print(str('Voltage is set to ')+str(V_set))
    PS.flushInput()
    return(V_set)


def Get_Status():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_STATUS)  # Request the status of the PS
    Stat = str(PS.read(5))
    # print('Status = '+Stat)
    PS.flushInput()
    return(Stat)


def SetVoltage(Voltage):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    if (float(Voltage) > float(VMAX)):
        Voltage = VMAX
    Voltage = "{:2.2f}".format(float(Voltage))
    Output_string = SET_VOLTAGE + bytes(Voltage, "utf-8")
    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    time.sleep(0.2)
    VeriVolt = "{:2.2f}".format(float(Get_V_Set()))  # Verify PS accepted
        # the setting
    print(VeriVolt)
    print(Voltage)
    while (VeriVolt != Voltage):
        PS.write(Output_string)  # Try one more time
    return(Output_string)


def SetCurrent(Current):
    print('before reopening serial')
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    print('after reopening serial')
    PS.flushInput()
    if (float(Current) > float(IMAX)):
        Current = IMAX
    Current = "{:2.3f}".format(float(Current))
    Output_string = SET_CURRENT + bytes(Current, "utf-8")
    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    time.sleep(0.2)
    VeriAmp = "{:2.3f}".format(float(Get_I_Set()))
    if (VeriAmp != Current):
        VeriAmp = 0.00
    return(Output_string)


def V_Actual():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_ACTUAL_VOLTAGE)  # Request the actual voltage
    time.sleep(0.015)
    V_actual = PS.read(5)
    if (V_actual == b''):
            V_actual = b'0'  # deal with the occasional NULL from PS
#    print('V_actual = ' + str(V_actual))
    V_actual = float(V_actual)
    PS.flushInput()
    return(V_actual)


def I_Actual():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_ACTUAL_CURRENT)  # Request the actual current
    time.sleep(0.015)
    I_actual = PS.read(5)
    if (I_actual == b''):
            I_actual = b'0'  # deal with the occasional NULL from PS
    I_actual = float(I_actual)
    PS.flushInput()
    return(I_actual)


def SetOP(OnOff):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()

    Output_string = SET_OUTPUT + bytes(OnOff, "utf-8")

    PS.write(Output_string)
    # print(Output_string)
    PS.flushInput()
    return(Output_string)


def SetOVP(OnOff):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    Output_string = SET_OVP + OnOff
    PS.write(Output_string)
    # print(Output_string)
    PS.flushInput()
    return(Output_string)


def SetOCP(OnOff):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    Output_string = SET_OCP + OnOff
    PS.write(Output_string)
    # print(Output_string)
    PS.flushInput()
    return(Output_string)


def Update_VandI():
    V_actual = "{:2.2f}".format(V_Actual())
    # vReadoutLabel.configure(text="{} {}".format(V_actual, 'V'))

    I_actual = "{0:.3f}".format(I_Actual())
    # iReadoutLabel.configure(text="{} {}".format(I_actual, 'A'))
    print(str(int(round(time.time() * 1000))) + ";" + str(V_actual) + ";" + str(I_actual) )


def SetVA(volt, current):
    # Volts = vEntry.get()
    SetVoltage(volt)

    # Amps = iEntry.get()
    if (current == ''):
        current = b'0'
    current = "{0:.3f}".format(float(current))
    SetCurrent(current)


#==============================================================================
# Variables
#==============================================================================
V_set = "{0:.2f}".format(Get_V_Set(), 'V')
I_set = "{0:.3f}".format(Get_I_Set(), 'I')
PSID = GetID()
Stat = Get_Status()
VMAX = '05'
IMAX = '3.0'

parser = argparse.ArgumentParser(description='Korad-KA6003P power supply control tool')
parser.add_argument('--volt', dest='volt', default='5',
                    help='Target voltage (default 5V)')
parser.add_argument('--current', dest='current', default='2.0',
                    help='Maximum current (default 2A)')

args = parser.parse_args()
print('args.volt: ' + args.volt)
print('args.current: ' + args.current)


#==============================================================================
# Set request voltage/current and poll loop for reading actual values
#==============================================================================
SetVA(args.volt, args.current)
# var = 1
time.sleep(1)
while 1 == 1:
    Update_VandI()

