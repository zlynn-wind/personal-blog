from flask import request, jsonify

from starks.blueprint import create_api_blueprint


bp = create_api_blueprint('index', __name__)


@bp.route('/')
def index():
    return 'Hello, starks'
