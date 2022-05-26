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

@app.route("/telescope/status")
def telescopeStatus():
    response = helpers.ApiResponse()
    try:
        statusString = meadeProcessor.sendCommands(":GX#")
        statusFragments = statusString[:-1].split(",")
        status = statusFragments[0]
        #stepperRA = statusFragments[2]
        #stepperDEC = statusFragments[3]
        #stepperTRAC = statusFragments[4]
        currentRA = statusFragments[5]
        currentDEC = statusFragments[6]
        motionStates = statusFragments[1]
        slewingStates = ("SlewToTarget", "FreeSlew", "ManualSlew")
        statusResponse = {
            "status": status,
            "isTracking": motionStates[2] == 'T',
            "isSlewing": status in slewingStates,
            "rightAscension": currentRA,
            "declination": currentDEC
        }
        return response.getResponse(type="success", result=statusResponse)
    except Exception as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/position", methods=['GET', 'POST'])
def telescopePosition():
    response = helpers.ApiResponse()
    try:
        if request.method == 'GET':
            # TODO: implement position GET
            return response.getResponse(type="success", result="Hello World")
        elif request.method == 'POST':
            # TODO: implement position POST
            return response.getResponse(type="success", result="Hello World")
    except Exception as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))
