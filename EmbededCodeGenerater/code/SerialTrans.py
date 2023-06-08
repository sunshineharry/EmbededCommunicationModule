#!/usr/bin/python
# -*-coding: utf-8 -*-

import serial

import threading
import time

class SerialMsg():
    isSended = True
    msg = ''

SerialMsgA = SerialMsg()    # A发B收
SerialMsgB = SerialMsg()    # B发A收

class SerialPort(threading.Thread):
    def __init__(self,port,buand,num,type):
        super().__init__()
        if type == 'COM':
            self.port = serial.Serial(port,buand)
            self.port.close()
            if not self.port.isOpen():
                self.port.open()
        if type == 'web':
            self.port = serial.serial_for_url(port, baudrate=115200)
        self.num = num
        

    def port_open(self):
        if not self.port.isOpen():
            self.port.open()

    def port_close(self):
        self.port.close()

    def send_data(self):
        global SerialMsgA, SerialMsgB
        if self.num == 'B':
            if SerialMsgB.isSended == False and SerialMsgB.msg != b'':
                self.port.write(SerialMsgB.msg)
                SerialMsgB.isSended = True
                print('B Send: ', SerialMsgB.msg, '\n')
        if self.num == 'A':
            if SerialMsgA.isSended == False and SerialMsgA.msg != b'':
                self.port.write(SerialMsgA.msg)
                SerialMsgA.isSended = True
                print('A Send: ', SerialMsgA.msg, '\n')


    def read_data(self):
        global SerialMsgA, SerialMsgB
        if self.num == 'A':
            msg = self.port.read_all()
            if msg == b'':
                pass
            else:
                SerialMsgB.msg = msg
                SerialMsgB.isSended = False
                print('A Read: ', msg, '\n')
        if self.num == 'B':
            msg = self.port.read_all()
            if msg == b'':
                pass
            else:
                SerialMsgA.msg = msg
                SerialMsgA.isSended = False
                print('B Read: ', msg, '\n')

    def run(self):
        while True:
            self.send_data()
            time.sleep(0.1)
            self.read_data()
            time.sleep(0.1)


if __name__ == "__main__":
    serial_port_A = SerialPort('rfc2217://localhost:4000',115200,'A','web')
    serial_port_B = SerialPort('COM11',115200,'B','COM')
    serial_port_A.start()
    serial_port_B.start()

