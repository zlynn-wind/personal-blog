import uuid
from datetime import datetime

from flask import Blueprint, render_template, request

from starks.modules.vqgan.model.vqgan import VQGANJob


bp = Blueprint("vqgan_view", __name__, url_prefix="/vqgan")


@bp.route("")
def index():
    jobs = VQGANJob.list_latest_jobs()
    return render_template("vqgan/list.html", jobs=jobs)


@bp.route("/<jid>")
def show_result(jid):
    job = VQGANJob.query.get(jid)
    return render_template("vqgan/show.html", job=job)


@bp.route("", methods=["POST"])
def create_vqgan():
    input_text = request.form.get("input_text")
    input_text = input_text.replace("'", "\\'")
    timeout = request.form.get("timeout", type=int)
    today = datetime.now().strftime("%Y%m%d")
    hex_ = uuid.uuid4().hex
    volume = f"/opt/mediakit/public/vqgan/{today}/{hex_}/"
    vqgan = VQGANJob.create(
        username="surreal",
        params={
            "nonce": hex_,
            "date": today,
            "input_text": input_text,
            "timeout": timeout,
            "docker": {
                "image": "surreal/vqgan-clip:2021070501",
                "command": f"'{input_text}'",
                "volume": volume,
            },
        }
    )
    jobs = VQGANJob.list_latest_jobs()
    return render_template("vqgan/list.html", jobs=jobs)
