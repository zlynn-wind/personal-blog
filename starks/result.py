class Result(object):

    def __init__(self, result=None, error=None):
        self.is_success = error is None
        self.result = result
        self.error = error

    def unwrap(self):
        if self.is_success:
            return self.result
        return None

    @classmethod
    def ok(cls, result):
        return cls(result=result)

    @classmethod
    def error(cls, error):
        return cls(error=error)
