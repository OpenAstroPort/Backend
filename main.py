#!/bin/python3
from flask import Flask
from flask import request
import json
import serial
from serial.tools import list_ports


app = Flask(__name__)

@app.route('/')
def home():
    return json.dumps({'name': 'OATREST', 'version': 'beta-1.0.0'})

@app.route('/devices', methods=['GET', 'POST'])
def devices():
    # if HTTP Method is GET try to retrieve a list of all available serial ports and return them as json array
    if request.method == 'GET':
        try:
            # Try to get available Serial Ports as List
            availablePorts = list_ports.comports()
            availablePortsList = list(map(lambda x: x.device,availablePorts))

            return {
                "status": "success",
                "result": availablePortsList
            }
        except:
            return {
                "status": "failed",
                "description": "could not retrieve available ports"
            }