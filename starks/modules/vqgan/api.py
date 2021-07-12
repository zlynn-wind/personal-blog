from datetime import datetime
import uuid

from flask import Blueprint, request, redirect, url_for
from envcfg.raw import aws as aws_cfg

from starks.modules.vqgan.model.vqgan import VQGAN
from starks.modules.vqgan.model.vqgan_job import VQGANJob
from starks.utils.api import success, fail
from starks.utils.s3 import sign_get_url


bp = Blueprint("vqgan", __name__, url_prefix="/api/v1")
AWS_BUCKET_NAME = aws_cfg.BUCKET_NAME
MAX_PAGE_SIZE = 50


@bp.route("vqgan.list")
def list_vqgans():
    page = request.args.get("page", type=int, default=1)
    page_size = request.args.get("page_size", type=int, default=10)
    page = max(1, page)
    page_size = min(page_size, MAX_PAGE_SIZE)
    vqgans = VQGAN.paginate(page, page_size)
    return success([e.marshal() for e in vqgans.items])


@bp.route("vqgan.get")
def get_vqgan():
    id_ = request.args.get("id")
    if id is None:
        return fail(error="Job not found", status=404)

    vqgan = VQGAN.get(id_)
    if vqgan is None:
        return fail(error="Job not found", status=404)
    return success(vqgan.marshal())


@bp.route("vqgan-job.get")
def get_job():
    job_id = request.args.get("id")
    job = VQGANJob.get_by_id(job_id)
    if job is None:
        return fail(error="Job not found", status=404)
    return success({
        "status": job.status,
        "preview_url": url_for('vqgan.get_job_preview', job_id=job_id),
    })


@bp.route("vqgan/<id_>/preview")
def preview_vqgan(id_):
    vqgan = VQGAN.get(id_)
    if vqgan is None:
        return fail(error="Job not found", status=404)
    return redirect(
        sign_get_url(
            obj_key=vqgan.obj_key,
            bucket_name=vqgan.bucket_name,
        )
    )


@bp.route("vqgan/jobs/report", methods=["POST"])
def report_job():
    payload = request.get_json()
    job_id = payload.get("job_id", None)
    job_type = payload.get("task_type", None)
    status = payload.get("status", None)
    timestamp = payload.get("timestamp", None)
    data = payload.get("data", None)
    if job_type.lower() != "vqgan":
        return fail(error="Invalid job_type")

    job = VQGANJob.get_by_id(job_id)
    if job is None:
        return fail(error="Job not found", status=404)

    if status == "started":
        job.status = VQGANJob.STATUS_IN_PROGRESS
        job.started_at = datetime.fromtimestamp(int(timestamp/1000))
        job.save()
        return success({"job_id": job_id})

    if status == "stopped":
        job.status = VQGANJob.STATUS_ERROR
        job.set_result(is_success=False, error_message=data.get("message"))
        job.ended_at = datetime.utcnow()
        job.save()
        return success({"job_id": job_id})

    if status == "success":
        job.status = VQGANJob.STATUS_SUCCESS
        job.set_result(is_success=True, data=data)
        job.ended_at = datetime.utcnow()
        job.save()

        vqgan = VQGAN.create(
            text=job.params["text"],
            bucket_name=AWS_BUCKET_NAME,
            obj_key=job.result["obj_key"]
        )

        return success({})

    return fail(error='Bad Request')


@bp.route("vqgan-job.create", methods=["POST"])
def create_job():
    payload = request.get_json()
    text = payload.get("text", None)
    if text is None:
        return fail(error="text can not be empty", status=400)

    # TODO: Translate
    if len(text) == 0 or len(text) > 90:
        return fail(error="text too long", status=400)
    today = datetime.now().strftime("%Y%m%d")
    hex_ = uuid.uuid4().hex
    vqgan_job = VQGANJob.create(
        params={
            "nonce": hex_,
            "date": today,
            "text": text.strip(),
            "docker": {
                "image": "413195515848.dkr.ecr.cn-northwest-1.amazonaws.com.cn/surreal-vqgan-clip:latest",    # noqa: FIXME
            }
        }
    )
    return success(vqgan_job.marshal())


@bp.route("/jobs/<job_id>/preview")
def get_job_preview(job_id):
    job = VQGANJob.get_by_id(job_id)
    if job is None:
        return fail(error="Job not found", status=404)
    result = job.result
    return redirect(
        sign_get_url(
            obj_key=result.filekey,
            bucket_name=AWS_BUCKET_NAME,
        )
    )
