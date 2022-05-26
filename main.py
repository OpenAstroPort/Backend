#!/bin/python3
from flask import Flask
from flask import request
import logging
import serial
from serial.tools import list_ports
import helpers


app = Flask(__name__)

@app.route('/')
def home():
    return {'name': 'OATREST', 'version': 'beta-1.0.0'}

@app.route('/devices', methods=['GET', 'POST'])
def devices():
    # if HTTP Method is GET try to retrieve a list of all available serial ports and return them as json array
    if request.method == 'GET':
        logging.info("requested available com devices")
        response = helpers.ApiResponse()
        try:
            # Try to get available Serial Ports as List
            availablePorts = list_ports.comports()
            availablePortsList = list(map(lambda x: x.device, availablePorts))

            return response.getResponse(type="success", result=availablePortsList)
        except:
            return response.getResponse(type="error", description="failed to retrieve com devices")