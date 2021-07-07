import json


class BaseParams(object):

    DEFAULT_TIMEOUT_SEC = 600

    def __init__(self, **kwargs):
        self.timeout_sec = kwargs.get("timeout_sec", DEFAULT_TIMEOUT_SEC)

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)

    def to_dict(self):
        return {
            "timeout_sec": self.timeout_sec,
        }

    def jsonify(self):
        return json.dumps(self.to_dict())


class BaseResult(object):

    def __init__(self, **kwargs):
        self.status = kwargs.get("status")

    def to_dict(self):
        return {
            "status": self.status,
        }

    def jsonify(self):
        return json.dumps(self.to_dict())
