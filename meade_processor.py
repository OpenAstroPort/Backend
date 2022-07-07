import serial
import logging
from serial.tools import list_ports

class MeadeProcessor:
    def __init__(self):
        self.comDevice = None
        self.baudRate = None
        self.serialConnection = None
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

    def connectSerial(self):
        try:
            if not self.baudRate:
                raise BaseException("no baudrate specified please setup serial device first")
            if not self.comDevice:
                raise BaseException("no comDevice specified please setup serial device first")
            self.serialConnection = serial.Serial(port=self.comDevice, baudrate=self.baudRate, timeout=1)
            self.serialConnection.flush()
            self.serialConnection.read()
            return True
        except:
            raise BaseException("issue opening serial connection")

    def disconnectSerial(self):
        try:
            if not self.serialConnection:
                raise BaseException("no serial connection opened cant close it")
            self.serialConnection.close()
            return True
        except:
            raise BaseException("issue disconnecting serial device")

    def listSerial(self):
        try:
            availablePorts = list_ports.comports()
            availablePortsList = list(map(lambda x: x.device, availablePorts))
        except:
            raise BaseException("failed to retrieve serial devices")
        return availablePortsList

    def setupSerial(self, comDevie, baudRate):
        if baudRate not in self.__validBaudRates:
            raise BaseException("invalid baud rate")
        if comDevie not in self.listSerial():
            raise BaseException("selected comDevice is unavailable")
        self.comDevice = comDevie
        self.baudRate = baudRate

    def getCurrentSerialConfig(self):
        return {
            "comDevice": self.comDevice,
            "baudRate": self.baudRate
        }

    def sendCommands(self, commandString):
        if self.comDevice == None:
            raise BaseException("no comDevice selected")
        if self.baudRate == None:
            raise BaseException("no baudRate selected")
        if self.serialConnection == None:
            raise BaseException("not connected to a serial port")
        logging.info("## Sending Command to OAT:")
        logging.info(commandString.encode('utf-8'))
        self.serialConnection.flush()
        self.serialConnection.write(commandString.encode('utf-8'))
        result = self.serialConnection.readline()
        logging.info("## Received Result from OAT:")
        logging.info(result.decode('utf-8'))
        return result.decode('utf-8')