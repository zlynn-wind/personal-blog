import time
import os
import threading

import docker
import requests

from starks.wsgi import application
from starks.extensions import db
from starks.modules.vqgan.model.vqgan import VQGANJob


client = docker.from_env()
TIMEOUT = (60)


def get_oldest_pending_job():
    return VQGANJob.query.filter_by(status=VQGANJob.STATUS_PENDING).order_by(VQGANJob.id).first()


def execute_job(job):
    params = job.params
    input_text = params.get('input_text', None)
    if input_text is None or len(input_text) == 0:
        print("`input_text` is empty")
        job.set_result(False, "`input_text` is empty")
        return
    docker_args = params.get('docker', None)
    if docker_args is None:
        print("`docker` is empty")
        job.set_result(False, "`docker` is empty")
        return

    today = datetime.now().strftime("%Y%m%d")
    date = params.get('date', today)
    nonce = params.get('nonce',)
    default_volume = f"/opt/mediakit/public/vqgan/{date}/{nonce}/"

    docker_image = docker_args.get("image")
    docker_command = docker_args.get("command")
    docker_volume = docker_args.get("volume", default_volume)

    print(f"Executing VQGAN job {job.id}: {params}")

    if not os.path.isdir(docker_volume):
        os.makedirs(docker_volume)

    try:
        container = client.containers.run(
            docker_image,
            docker_command,
            auto_remove=True,
            detach=True,
            tty=True,
            volumes={
                docker_volume: {
                    'bind': '/workspace/incubator/VQGAN_CLIP/progress/',
                    'mode': 'rw',
                },
            },
        )

        def wait_exit():
            last_ts = int(time.time())
            while True:
                try:
                    container.reload()
                    if container.status in ('created', 'running'):
                        print(container.logs(since=last_ts).decode('utf-8'), end='')
                        last_ts = int(time.time())
                        time.sleep(2)
                    else:
                        break
                except requests.exceptions.HTTPError:
                    break

        def wait_exit_wait():
            while True:
                try:
                    container.wait(timeout=2)
                    time.sleep(2)
                except requests.exceptions.ReadTimeout:
                    print(f"Container {container.id} still running")
                    continue

        thread = threading.Thread(target=wait_exit)
        thread.start()
        thread.join(TIMEOUT)
        if thread.is_alive():
            print("Timedout, killed")
            container.stop()
            container.remove(force=True)

    except Exception as e:
        print("[ERROR]", e.get_message())
        raise e
    finally:
        container.stop()
        container.remove(force=True)


def flush_result(job):
    today = datetime.now().strftime("%Y%m%d")
    date = params.get('date', today)
    nonce = params.get('nonce',)
    filekey = f"vqgan/{date}/{nonce}/"

    if volume is not None:
        max_ = 0
        files = os.listdir(volume)
        for each in files:
            name = each.lstrip('step_').rstrip('.png')
            step = 0
            try:
                step = int(name)
            except Exception:
                continue
            max_ = max(max_, int(name))

    job.result = {
        'step': max_,
        'filekey': filekey,
    }
    job.save()


def main():
    print("Started worker")
    while True:
        try:
            with application.test_request_context():
                job = get_oldest_pending_job()
                if job is None:
                    print("No jobs found")
                    time.sleep(3)
                    continue
                print(f"Found job, id is {job.id}")
                job.status = VQGANJob.STATUS_IN_PROGRESS
                job.save()

                execute_job(job)
                flush_result(job)

                job.status = VQGANJob.STATUS_SUCCESS
                job.save()
        except Exception:
            job.status = VQGANJob.STATUS_ERROR
            job.save()


if __name__ == '__main__':
    main()
