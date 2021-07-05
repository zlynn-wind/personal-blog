from flask import Blueprint, jsonify

from starks.modules.vqgan.model.vqgan import VQGANJob


bp = Blueprint("vqgan", __name__, url_prefix="/api/v1/vqgan")


@bp.route("/jobs")
def list_jobs():
    jobs = VQGANJob.list_latest_jobs()
    return jsonify(
        success=True,
        data=[{'id': j.id, 'params': j.params, 'result': j.result} for j in jobs]
    )
