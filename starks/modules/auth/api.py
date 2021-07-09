from uuid import uuid4
from envcfg.raw import starks as config
from flask import request, jsonify, url_for, redirect, Blueprint


bp = Blueprint('auth', __name__, url_prefix="/api/v1/auth")


@bp.route("")
def redirect_to_feishu():
    APPID = config.AUTH_FEISHU_APP_ID
    REDIRECT_URI = url_for('auth.feishu_auth', _external=True)
    STATE = uuid4()
    # FIXME
    redirect_url = (f"https://open.feishu.cn/open-apis/authen/v1/index?"
                    f"redirect_uri={REDIRECT_URI}"
                    f"&app_id={APPID}"
                    f"&state={STATE}")
    return redirect(redirect_url)


@bp.route('/feishu')
def auth_feishu():
    code = request.args.get("code")
    _state = request.args.get("state")
