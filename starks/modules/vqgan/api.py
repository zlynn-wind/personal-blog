from flask import Blueprint, request

from starks.modules.vqgan.model.vqgan import VQGANJob
from starks.utils.api import success, fail


bp = Blueprint("vqgan", __name__, url_prefix="/api/v1/vqgan")


@bp.route("/jobs")
def list_jobs():
    jobs = VQGANJob.list_latest_jobs()
    return success([{'id': j.id, 'params': j.params, 'result': j.result}
                   for j in jobs])


@bp.route("/jobs/report", methods=["POST"])
def report_job():
    payload = request.get_json()
    job_id = payload.get("job_id", None)
    job_type = payload.get("task_type", None)
    event = payload.get("event", None)
    timestamp = payload.get("timestamp", None)
    data = payload.get("data", None)
    if job_type.lower() != "vqgan":
        return fail(error="Invalid job_type")

    job = VQGANJob.get_by_id(job_id)
    if job is None:
        return fail(error="Job not found", status=404)

    if event == "started":
        job.status = VQGANJob.STATUS_IN_PROGRESS
        job.params = {
            "started_at": timestamp,
        }
        job.save()
        return success({"job_id": job_id})

    if event == "stopped":
        job.status = VQGANJob.STATUS_ERROR
        job.set_result(False, data.get("message"))
        job.save()
        return success({"job_id": job_id})

    if event == "success":
        job.status = VQGANJob.STATUS_SUCCESS
        job.result = {"success": True, **data}
        job.save()
        return success({"job_id": job_id})

    return fail(error='Bad Request')
