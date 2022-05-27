from datetime import datetime

class ApiResponse:
    def __init__(self):
        self.status = None
        self.description = None
        self.result = None

    def __iter__(self):
        yield "status", self.status
        yield "description", self.description
        yield "result", self.result

    def getResponse(self, type, description=None, result=None):
        if type == 'error':
            self.status = 'error'
            self.description = description

        elif type == 'success':
            self.status = 'success'
            self.result = result
        data = dict(self)
        return {key:data[key] for key in data if data[key] != None}

class HandleDates():
    def __init__(self):
        self.__dateObject = None
        self.__utcOffset = '-2'

    def convertDateRequestToOATCommands(self, requestBody, dateFormat):
        if "utcTimestamp" in requestBody and "utcOffset" in requestBody:
            self.__dateObject = datetime.utcfromtimestamp(int(requestBody["utcTimestamp"]))
            self.__utcOffset = requestBody["utcOffset"][0:1] + str(abs(int(requestBody["utcOffset"]))/60).zfill(2)
        else:
            raise Exception("invalid request Body for Datetime Conversion")
        if dateFormat == "24":
            cmd = self.__dateObject.strftime(":SC%d/%m/%y#:SL%H:%M:%S#:SG" + self.__utcOffset + "#")
        elif dateFormat == "12":
            cmd = self.__dateObject.strftime(":SC%d/%m/%y#:SL%I:%M:%S#:SG" + self.__utcOffset + "#")
        else:
            raise Exception("invalid dateFormat accepts 12 or 24")
        return cmd
