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

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5050)

@app.route('/')
def home():
    return {'name': 'OATREST', 'version': 'beta-1.0.0'}

@app.route('/devices', methods=['GET', 'POST'])
def devices():
    response = helpers.ApiResponse()
    # if HTTP Method is GET try to retrieve a list of all available serial ports and return them as json array
    if request.method == 'GET':
        logging.info("requested available com devices")
        try:
            # Try to get available Serial Ports as List
            availablePortsList = meadeProcessor.listSerial()
            return response.getResponse(type="success", result=availablePortsList)
        except BaseException as e:
            logging.error(e)
            return response.getResponse(type="error", description=str(e))
    if request.method == 'POST':
        logging.info("set com device and baudrate")
        try:
            data = request.get_json(force=True)
            if data['comDevice'] == None:
                raise BaseException("no comDevice selected")
            if data['baudRate'] == None:
                raise BaseException("no baudRate selected")
            meadeProcessor.setupSerial(comDevie=data['comDevice'], baudRate=data['baudRate'])
            return response.getResponse(type="success", result=meadeProcessor.getCurrentSerialConfig())
        except BaseException as e:
            logging.error(e)
            return response.getResponse(type="error", description=str(e))

@app.route("/telescope/info")
def telescopeInfo():
    response = helpers.ApiResponse()
    try:
        infoString = meadeProcessor.sendCommands(":GVP#:GVN#:Gt#:Gg#:GC#:GL#")
        infoFragments = list(infoString[:-1].split("#"))
        return response.getResponse(type="success", result=infoFragments)
    except BaseException as e:
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
    except BaseException as e:
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
    except BaseException as e:
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
    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/geolocation", methods=['GET', 'POST'])
def telescopeGeolocation():
    response = helpers.ApiResponse()
    try:
        if request.method == 'GET':
            locationString = meadeProcessor.sendCommands(":Gt#:Gg#")
            locationList = locationString[:-1].split("#")
            locationDict =  {
                "lat": locationList[0],
                "lng": locationList[1],
            }
            return response.getResponse(type="success", result=locationDict)
        if request.method == 'POST':
            locationDict = request.get_json()
            commandResultString = meadeProcessor.sendCommands("St%s#:Sg%s#" % (locationDict["lat"], locationDict["lng"]))
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))

            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)

    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/move", methods=["POST"])
def telescopeMovement():
    response = helpers.ApiResponse()
    try:
        if request.method == 'POST':
            moveData = request.get_json()
            if 'direction' not in moveData:
                raise BaseException("no direction provided")
            if moveData['direction'] not in ['n', 'w', 's', 'e']:
                raise BaseException("invalid direction given")
            commandResultString = meadeProcessor.sendCommands(":M%s#" % moveData["direction"])
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))
            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)
    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))


@app.route("/telescope/move/quit", methods=["POST"])
def telescopeStopMovement():
    response = helpers.ApiResponse()
    try:
        if request.method == 'POST':
            moveData = request.get_json()
            if 'direction' not in moveData:
                raise BaseException("no direction provided")
            if moveData['direction'] not in ['n', 'w', 's', 'e', 'a']:
                raise BaseException("invalid direction given")
            commandResultString = meadeProcessor.sendCommands(":Q%s#" % moveData["direction"])
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))
            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)
    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/action", methods=["POST"])
def telescopeActions():
    response = helpers.ApiResponse()
    statusString = meadeProcessor.sendCommands(":GX#")
    statusFragments = statusString[:-1].split(",")
    status = statusFragments[0]
    currentRA = statusFragments[5]
    currentDEC = statusFragments[6]
    motionStates = statusFragments[1]
    slewingStates = ("SlewToTarget", "FreeSlew", "ManualSlew")
    telescopeStates = {
        "status": status,
        "isTracking": motionStates[2] == 'T',
        "isSlewing": status in slewingStates,
        "rightAscension": currentRA,
        "declination": currentDEC
    }
    try:
        if request.method == 'POST':
            actionData = request.get_json()
            if 'action' not in actionData:
                raise BaseException("no action provided")
            if actionData['action'] not in ['setHome', 'toggleParking', 'togglePrecision', 'toggleTracking', 'reset']:
                raise BaseException("invalid action provided")
            if actionData["action"] == 'setHome':
                commandResultString = meadeProcessor.sendCommands(":hS#")
            elif actionData["action"] == 'toggleParking':
                if telescopeStates["status"] != 'Parked':
                    commandResultString = meadeProcessor.sendCommands(":hP#")
                else:
                    commandResultString = meadeProcessor.sendCommands(":hU#")
            elif actionData['action'] == 'toggleTracking':
                if telescopeStates["isTracking"]:
                    commandResultString = meadeProcessor.sendCommands(":MT0#")
                else:
                    commandResultString = meadeProcessor.sendCommands(":MT1#")
            elif actionData['action'] == 'togglePrecision':
                commandResultString = meadeProcessor.sendCommands(":P#")
            elif actionData['action'] == 'reset':
                commandResultString = meadeProcessor.sendCommands(":I#")
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))
            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)
    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/slew", methods=["POST"])
def telescopeSlews():
    response = helpers.ApiResponse()
    try:
        if request.method == 'POST':
            slewData = request.get_json()
            if 'to' not in slewData:
                raise BaseException("no to provided")
            if slewData['to'] not in ['home', 'target']:
                raise BaseException("invalid to provided")
            if slewData['to'] == 'home':
                commandResultString = meadeProcessor.sendCommands(":hF#")
            elif slewData['to'] == 'target':
                commandResultString = meadeProcessor.sendCommands(":MT#")
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))
            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)
    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))

@app.route("/telescope/slew/speed", methods=['POST'])
def telescopeSlewSpeed():
    response = helpers.ApiResponse()
    try:
        if request.method == 'POST':
            speedData = request.get_json()
            if 'speed' not in speedData:
                raise BaseException("no speed was given")
            speed = int(speedData['speed'])
            if speed > 4 and speed < 0:
                raise BaseException("invalid speed was given expected values from 1-4")
            if speedData['speed'] == 1:
                commandResultString = meadeProcessor.sendCommands(":RG#") # Slowest
            elif speedData['speed'] == 2:
                commandResultString = meadeProcessor.sendCommands(":RC#")
            elif speedData['speed'] == 3:
                commandResultString = meadeProcessor.sendCommands(":RM#")
            elif speedData['speed'] == 4:
                commandResultString = meadeProcessor.sendCommands(":RS#")
            commandSuccessStates = map(lambda x: bool(x), re.findall(r'\d', commandResultString))
            if False not in commandSuccessStates:
                commandResult = {
                    "commandSuccess": False not in commandSuccessStates
                }
                return response.getResponse(type="success", result=commandResult)
    except BaseException as e:
        logging.error(e)
        return response.getResponse(type="error", description=str(e))