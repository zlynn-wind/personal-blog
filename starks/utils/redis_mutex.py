from uuid import uuid4

from starks.extensions import cache


class Mutex(object):

    def __init__(self, key_prefix='mutex:', expire=30):
        self.key = '{}{}'.format(key_prefix, uuid4().hex)
        self.expire = expire

    def lock(self):
        cache.set(self.key, self.key, self.expire)

    def unlock(self):
        cache.delete(self.key)

    def is_lock(self):
        return cache.get(self.key) == self.key
