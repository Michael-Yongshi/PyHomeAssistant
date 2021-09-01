import sys
import serial
# pip3 install pyserial

port = '/dev/ttyUSB0'
baudrate = 115200
ser = serial.Serial(port,baudrate,timeout=0.001)

while True:
    data = ser.readline()

    # data = ser.read(1)
    # data+= ser.read(ser.inWaiting())
    if data != b'':
        print(data)
