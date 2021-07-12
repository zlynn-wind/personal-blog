from envcfg.raw import starks as config
from flask import Flask
from werkzeug.utils import import_string

from starks.extensions import db, cache, cors
from starks.error import APIError


blueprints = [
    'starks.modules.auth.api:bp',
    'starks.modules.index.api:bp',
    'starks.modules.video_eval.api:bp',

    'starks.modules.vqgan.api:bp',
    'starks.modules.vqgan.view:bp',
]


def create_app(import_name=None):
    app = Flask(import_name or __name__)

    app.config.from_object('envcfg.raw.starks')
    app.debug = bool(int(config.DEBUG))
    app.config['SQLALCHEMY_POOL_RECYCLE'] = int(config.SQLALCHEMY_POOL_RECYCLE)

    cors.init_app(app)
    db.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': config.CACHE_TYPE})

    setup_errorhandler(app)

    for bp_import_name in blueprints:
        bp = import_string(bp_import_name)
        app.register_blueprint(bp)

    return app


def setup_errorhandler(app):
    @app.errorhandler(APIError)
    def return_help(e):
        return jsonify({'text': str(e)})
