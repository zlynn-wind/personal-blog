from flask import Blueprint


def create_api_blueprint(name, package_name, **kwargs):
    """Create API blueprint for operating events

    :param name: The name of endpoint.
    :param package_name: Always be `__name__`.
    :param url_prefix: The url prefix of relative URL.
    """

    url_prefix = kwargs.pop('url_prefix', '/')
    url_prefix = '{url_prefix}'.format(
        name=name, url_prefix=url_prefix)

    blueprint_name = '{name}'.format(name=name)
    return _create_bp(blueprint_name, package_name,
                      url_prefix=url_prefix, **kwargs)


def _create_bp(name, package_name, **kwargs):
    """Create blueprint"""

    url_prefix = kwargs.pop('url_prefix', '')

    bp = Blueprint(
        name, package_name,
        url_prefix=url_prefix,
        **kwargs)

    return bp
