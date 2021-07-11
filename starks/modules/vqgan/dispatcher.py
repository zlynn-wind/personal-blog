import time
import os

from kubernetes import client, config

from starks.wsgi import application
from starks.utils.api import external_url_for
from starks.modules.vqgan.model.vqgan import VQGANJob


AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_EKS_CLUSTER_NAME = os.environ.get("AWS_EKS_CLUSTER_NAME")
SERVICE_NAME = os.environ.get("STARKS_VQGAN_K8S_SERVICE_NAME")


def get_oldest_pending_job():
    return (
        VQGANJob.query
                .filter_by(status=VQGANJob.STATUS_PENDING)
                .order_by(VQGANJob.id).first())


def create_k8s_job(job):
    params = job.params
    input_text = params.get("input_text")
    docker_args = params.get('docker', None)
    docker_image = docker_args.get("image")

    k8s_job_name = f"vqgan-{job.id}"
    container = client.V1Container(
        name=k8s_job_name,
        image=docker_image,
        image_pull_policy="Always",
        command=["/workspace/entrypoint.sh"],
        args=["--timeout", "120",
              "--text", f"{input_text}",
              "--job_id", job.id],
    )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={
            "job_type": "vqgan",
        }),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0,
        selector={
            "surreal/vqgan": "true"
        }
    )
    # Instantiate the job object
    k8s_job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=k8s_job_name),
        spec=spec
    )

    return k8s_job


def validate_job_params(job):
    params = job.params
    input_text = params.get("input_text")
    docker_args = params.get("docker", {})
    if input_text is None or len(input_text) == 0:
        print("`input_text` is empty")
        job.set_result(False, "`input_text` is empty")
        job.save()
        return False

    docker_args = params.get('docker', None)
    if docker_args is None:
        print("`docker` is empty")
        job.set_result(False, "`docker` is empty")
        job.save()
        return False
    docker_image = docker_args.get("image")
    if docker_image is None:
        print("`docker.image` is empty")
        job.set_result(False, "`docker.image` is empty")
        job.save()
        return False
    return True


def main():
    print("Started dispatcher")
    config.load_kube_config()
    while True:
        with application.test_request_context():
            PREHOOK_URL = external_url_for(
                "vqgan.report_job", base=SERVICE_NAME)
            POSTHOOK_URL = external_url_for(
                "vqgan.report_job", base=SERVICE_NAME)
            job = get_oldest_pending_job()

            if job is None:
                print("No jobs found")
                time.sleep(3)
                continue
            if not validate_job_params(job):
                print("Invalid job params.")
                continue
            print(f"Found job, id is {job.id}")
            try:
                create_k8s_job(
                    job,
                    PREHOOK_URL=PREHOOK_URL,
                    POSTHOOK_URL=POSTHOOK_URL,
                )
            except Exception:
                print(f"[ERROR] Failed to dispatch job: {job.id}")


if __name__ == '__main__':
    main()
