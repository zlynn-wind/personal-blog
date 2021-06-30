from flask import url_for
from envcfg.raw import starks as config

from flask import jsonify


def json_response(data):
    return jsonify(data)


def success(result):
    return jsonify(code=0, result=result)


def marshall_one(instance, fields):
    r = {}
    for each in fields:
        r[each] = getattr(instance, each)
    return r


def marshall(instances, fields):
    single = False
    if not isinstance(instances, (list, tuple)):
        single = True
        instances = [instances]
    result = list(map(lambda x: marshall_one(x, fields), instances))
    if single:
        return result[0]
    return result


def fail(code=9999, error='Unknown Error', status=400):
    return jsonify(code=code, error=error), status


def fail_with(err):
    return fail(code=err.code, error=err.error, status=err.status)


def external_url(*args, **kwargs):
    path = url_for(*args, **kwargs)
    if not path.startswith('/'):
        path = '/{}'.format(path)
    return '{base}{path}'.format(base=config.ROOT_URL, path=path)
