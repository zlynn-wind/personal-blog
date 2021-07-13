from datetime import datetime
import uuid

from flask import Blueprint, request, redirect, url_for
from envcfg.raw import aws as aws_cfg

from starks.modules.alimt.service import zh2en
from starks.modules.vqgan.helper import get_random_style
from starks.modules.vqgan.model.vqgan import VQGAN
from starks.modules.vqgan.model.vqgan_job import VQGANJob
from starks.utils.api import success, fail
from starks.utils.s3 import sign_get_url


bp = Blueprint("vqgan", __name__, url_prefix="/api/v1")
AWS_BUCKET_NAME = aws_cfg.BUCKET_NAME
MAX_PAGE_SIZE = 50

VQGAN_IMAGE = "413195515848.dkr.ecr.cn-northwest-1.amazonaws.com.cn/surreal-vqgan-clip:latest",    # noqa: FIXME


@bp.route("/paint.list")
def list_vqgans():
    page = request.args.get("page", type=int, default=1)
    page_size = request.args.get("page_size", type=int, default=10)
    page = max(1, page)
    page_size = min(page_size, MAX_PAGE_SIZE)
    vqgans = VQGAN.paginate(page, page_size)
    return success([e.marshal() for e in vqgans.items])


@bp.route("/paint.get")
def get_vqgan():
    id_ = request.args.get("id")
    if id is None:
        return fail(error="Paint not found", status=404)

    vqgan = VQGAN.query.get(id_)
    if vqgan is None:
        return fail(error="Paint not found", status=404)
    return success(vqgan.marshal())


@bp.route("/paint.preview")
def preview_vqgan():
    id_ = request.args.get("id", type=int)
    vqgan = VQGAN.get(id_)
    if vqgan is None:
        return fail(error="Job not found", status=404)
    return redirect(
        sign_get_url(
            obj_key=vqgan.obj_key,
            bucket_name=vqgan.bucket_name,
        )
    )


@bp.route("/paint.create", methods=["POST"])
def create_paint():
    payload = request.get_json()
    raw_text = payload.get("text", None)
    if raw_text is None:
        return fail(error="text can not be empty", status=400)

    raw_text = raw_text.strip()

    if len(raw_text) == 0 or len(raw_text) > 90:
        return fail(error="text too long", status=400)

    text = zh2en(raw_text)
    today = datetime.now().strftime("%Y%m%d")
    hex_ = uuid.uuid4().hex

    vqgan_job = VQGANJob.create(
        params={
            "nonce": hex_,
            "date": today,
            "raw_text": raw_text,
            "text": text,
            "style": get_random_style(),
            "docker": {
                "image": VQGAN_IMAGE,
            }
        }
    )
    return success(vqgan_job.marshal())


@bp.route("/paint-job.report", methods=["POST"])
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
            text=job.params["raw_text"],
            bucket_name=AWS_BUCKET_NAME,
            obj_key=job.result.get("data", {}).get("obj_key")
        )

        return success({})

    return fail(error='Bad Request')


@bp.route("/paint-job.get")
def get_job():
    job_id = request.args.get("id")
    job = VQGANJob.get_by_id(job_id)
    if job is None:
        return fail(error="Job not found", status=404)
    return success({
        "status": job.status,
        "result": job.result,
        "preview_url": url_for(
            'vqgan.get_job_preview', job_id=job_id, _external=True),
    })


@bp.route("/paint-job.create", methods=["POST"])
def create_job():
    payload = request.get_json()
    raw_text = payload.get("text", None)
    if raw_text is None:
        return fail(error="text can not be empty", status=400)

    raw_text = raw_text.strip()

    if len(raw_text) == 0 or len(raw_text) > 90:
        return fail(error="text too long", status=400)

    text = zh2en(raw_text)
    today = datetime.now().strftime("%Y%m%d")
    hex_ = uuid.uuid4().hex

    vqgan_job = VQGANJob.create(
        params={
            "nonce": hex_,
            "date": today,
            "raw_text": raw_text,
            "text": text,
            "style": get_random_style(),
            "docker": {
                "image": VQGAN_IMAGE,
            }
        }
    )
    return success(vqgan_job.marshal())


@bp.route("/paint-jobs.preview")
def get_job_preview(job_id):
    job_id = request.args.get("job_id", type=int)
    job = VQGANJob.get_by_id(job_id)
    if job is None:
        return fail(error="Job not found", status=404)
    data = job.result.get("data", {})
    return redirect(
        sign_get_url(
            obj_key=data.get("filekey"),
            bucket_name=AWS_BUCKET_NAME,
        )
    )
