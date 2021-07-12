class JobParams(object):
    def __init__(self, text):
        self.text = text


class JobResult(object):
    def __init__(self, bucket_name=None, obj_key=None, error_message=None):
        self.error_message = error_message
        self.bucket_name = bucket_name
        self.obj_key = obj_key
