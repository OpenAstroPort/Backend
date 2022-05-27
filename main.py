#!/bin/python3
from flask import Flask
from flask import request
import logging
import helpers
import re
from meade_processor import MeadeProcessor

dateHelper = helpers.HandleDates()
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
        infoFragments = list(infoString[:-1].split("#"))
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

@app.route("/telescope/position", methods=['GET'])
def telescopePosition():
    response = helpers.ApiResponse()
    # TODO: either restructure or remove optional GET as this is the only method implemented
    try:
        if request.method == 'GET':
            positionString = meadeProcessor.sendCommands(":GR#:GD#")
            positionFragments = list(positionString[:-1].split("#"))
            positionResult = {
                'rightAscension': positionFragments[0],
                'declination': positionFragments[1]
            }
            return response.getResponse(type="success", result=positionResult)
    except Exception as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/datetime", methods=['GET', 'POST'])
def telescopeDatetime():
    response = helpers.ApiResponse()
    
    try:
        if request.method == 'GET':
            datetimeString = meadeProcessor.sendCommands(":GC#:GL#:GG#")
            datetimeFragments = list(datetimeString[:-1].split("#"))
            datetimeResult = {
                'currentDate': datetimeFragments[0],
                'currentTime': datetimeFragments[1],
                'currentUTCOffset': datetimeFragments[2]
            }
            return response.getResponse(type="success", result=datetimeResult)
        elif request.method == 'POST':
            requestBody = request.get_json()
            dateFormat = meadeProcessor.sendCommands(":Gc#")[:-1]
            cmd = dateHelper.convertDateRequestToOATCommands(requestBody, dateFormat)
            commandResultString = meadeProcessor.sendCommands(cmd)
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))

            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)
            else:
                return response.getResponse(type="error", description="setting datetime on Telescope has failed")
    except Exception as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))