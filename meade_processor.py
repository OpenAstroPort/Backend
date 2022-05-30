import serial
from serial.tools import list_ports
import logging


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
        logging.error("Trying to send commands: %s to ESP" % commandString)
        with serial.Serial(port=self.comDevice, baudrate=self.baudRate, timeout=1) as ser:
            # Broken ESP Seems to restart every time after serial connection is established. Restart fucks up the first read which is why we add a empty read here:
            ser.read()
            ser.flush()
            ser.write(commandString.encode('utf-8'))
            ser.flush()
            result = ser.readline()
            logging.error("received '%s' from command" % result)
            return result.decode('utf-8')