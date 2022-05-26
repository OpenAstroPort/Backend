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