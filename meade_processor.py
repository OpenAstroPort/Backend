import serial
from serial.tools import list_ports


class MeadeProcessor:
    def __init__(self):
        self.comDevice = None
        self.baudRate = None
        self.__validBaudRates = [
            300,
            1200,
            2400,
            4800,
            9600,
            19200,
            38400,
            57600,
            74880,
            115200,
            230400,
            250000,
            500000,
            1000000
        ]

    def listSerial(self):
        try:
            availablePorts = list_ports.comports()
            availablePortsList = list(map(lambda x: x.device, availablePorts))
        except:
            raise Exception("failed to retrieve serial devices")
        return availablePortsList

    def setupSerial(self, comDevie, baudRate):
        if baudRate not in self.__validBaudRates:
            raise Exception("invalid baud rate")
        if comDevie not in self.listSerial():
            raise Exception("selected comDevice is unavailable")
        self.comDevice = comDevie
        self.baudRate = baudRate

    def getCurrentSerialConfig(self):
        return {
            "comDevice": self.comDevice,
            "baudRate": self.baudRate
        }

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