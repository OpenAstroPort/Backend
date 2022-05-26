import logging
import serial

class MeadeProcessor:
    def __init__(self):
        self.comDevice = None
        self.baudRate = None

    def setupSerial(self, device, baudRate):
        self.comDevice = device
        self.baudRate = baudRate

    def sendCommand(self, command):
        if self.comDevice != None and self.baudRate != None:
            try:
                with serial.Serial(port=self.comDevice, baudrate=self.baudRate, timeout=1) as ser:
                    ser.flush()
                    ser.write(command)
                    ser.flush()
                    result = ser.readLine()
                    return result
            except:
                return False