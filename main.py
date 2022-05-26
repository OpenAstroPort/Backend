#!/bin/python3
from flask import Flask
from flask import request
import logging
import helpers
from meade_processor import MeadeProcessor

meadeProcessor = MeadeProcessor()

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
            availablePortsList = meadeProcessor.listSerial()
            return response.getResponse(type="success", result=availablePortsList)
        except Exception as e:
            logging.error(e)
            return response.getResponse(type="error", description=str(e))
    if request.method == 'POST':
        logging.info("set com device and baudrate")
        response = helpers.ApiResponse()
        try:
            data = request.get_json(force=True)
            if data['comDevice'] == None:
                raise Exception("no comDevice selected")
            if data['baudRate'] == None:
                raise Exception("no baudRate selected")
            meadeProcessor.setupSerial(comDevie=data['comDevice'], baudRate=data['baudRate'])
            return response.getResponse(type="success", result=meadeProcessor.getCurrentSerialConfig())
        except Exception as e:
            logging.error(e)
            return response.getResponse(type="error", description=str(e))

@app.route("/telescope/info")
def telescopeInfo():
    response = helpers.ApiResponse()
    try:
        infoString = meadeProcessor.sendCommands(":GVP#:GVN#:Gt#:Gg#:GC#:GL#")
        infoFragments = list(filter(lambda x: x != "", infoString.split("#")))
        return response.getResponse(type="success", result=infoFragments)
    except Exception as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))