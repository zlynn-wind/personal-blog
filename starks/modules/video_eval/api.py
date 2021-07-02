import os

from flask import request, jsonify

from starks.blueprint import Blueprint


bp = Blueprint("video_eval", __name__, url_prefix="/api/v1/video_eval")
FACEHACK_HOME = os.environ.get("STARKS_FACEHACK_HOME", "./")

EVAL_EXEC = os.path.join(FACEHACK_HOME, 'FaceShifter',
                         'scripts', 'video_evaluation.py')


@bp.route("")
def index():
    return "Hello Video Eval"


@bp.route("/trigger", methods=["GET"])
def get_trigger():
    return ""


@bp.route("/trigger", methods=["POST"])
def trigger_job():
    params = request.get_json()
    job_name = params.get("job_name")
    suffix = params.get("suffix")
    cmd_args = [EVAL_EXEC, ]
    if job_name is not None:
        cmd_args.extend(["--job_name", job_name])
    if suffix is not None:
        cmd_args.extend(["--suffix", suffix])
