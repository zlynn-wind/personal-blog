class APIError(Exception):

    def __init__(self, code, error, status):
        self.code = code
        self.error = error
        self.status = status
