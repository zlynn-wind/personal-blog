from uuid import uuid4
import time

from envcfg.raw import aws as aws_cfg
from envcfg.raw import starks as cfg
from kubernetes import client, config

from starks.wsgi import application
from starks.utils.api import external_url_for
from starks.modules.vqgan.model.vqgan_job import VQGANJob


AWS_ACCESS_KEY = aws_cfg.ACCESS_KEY
AWS_SECRET_KEY = aws_cfg.SECRET_KEY
AWS_REGION = aws_cfg.REGION
AWS_EKS_CLUSTER_NAME = aws_cfg.EKS_CLUSTER_NAME
AWS_BUCKET_NAME = aws_cfg.BUCKET_NAME
SERVICE_ENDPOINT = cfg.VQGAN_K8S_SERVICE_ENDPOINT
SERVICE_NAMESPACE = cfg.VQGAN_K8S_SERVICE_NAMESPACE
S3_PREFIX = cfg.VQGAN_S3_PREFIX


def get_oldest_pending_job():
    return (
        VQGANJob.query
                .filter_by(status=VQGANJob.STATUS_PENDING)
                .order_by(VQGANJob.id).first())


def get_k8s_job_name(job):
    nonce = job.params.get('nonce')
    if nonce is not None and len(nonce) > 0:
        return f"vqgan-{job.id}-{nonce}"
    else:
        return f"vqgan-{job.id}"


def loop_get_job_status(api_instance, job):
    job_completed = False
    while not job_completed:
        api_response = api_instance.read_namespaced_job_status(
            name=get_k8s_job_name(job),
            namespace=SERVICE_NAMESPACE)
        if api_response.status.succeeded is not None or \
                api_response.status.failed is not None:
            job_completed = True
        time.sleep(1)
        print("Job status='%s'" % str(api_response.status))


def get_job_status(api_instance, job):
    api_response = api_instance.read_namespaced_job_status(
        name=get_k8s_job_name(job),
        namespace=SERVICE_NAMESPACE)
    print(str(api_response.status))


def make_job_object(api_instance, job, prehook, posthook):
    params = job.params
    text = params.get("text")
    docker_args = params.get('docker', None)
    docker_image = docker_args.get("image")

    k8s_job_name = get_k8s_job_name(job)
    container = client.V1Container(
        name=k8s_job_name,
        image=docker_image,
        image_pull_policy="Always",
        command=["/workspace/entrypoint.sh"],
        args=["--timeout", "120",
              "--text", f"{text}",
              "--job_id", str(job.id),
              "--file_key", f"vqgan/{S3_PREFIX}{job.id}.png"],
        env=[
            client.V1EnvVar(name="AWS_ACCESS_KEY", value=AWS_ACCESS_KEY),
            client.V1EnvVar(name="AWS_SECRET_KEY", value=AWS_SECRET_KEY),
            client.V1EnvVar(name="AWS_REGION", value=AWS_REGION),
            client.V1EnvVar(name="AWS_EKS_CLUSTER_NAME",
                            value=AWS_EKS_CLUSTER_NAME),
            client.V1EnvVar(name="AWS_BUCKET_NAME", value=AWS_BUCKET_NAME),
            client.V1EnvVar(name="PREHOOK_URL", value=prehook),
            client.V1EnvVar(name="POSTHOOK_URL", value=posthook),
            client.V1EnvVar(name="JOB_ID", value=str(job.id)),
        ],
        resources=client.V1ResourceRequirements(
            requests=("4", "16Gi"),
        )
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


def create_k8s_job(api_instance, job, prehook, posthook):
    k8s_job = make_job_object(api_instance, job, prehook, posthook)
    api_response = api_instance.create_namespaced_job(
        body=k8s_job, namespace=SERVICE_NAMESPACE)
    print("Kubernetes job {k8s_job.metadata.name} created.")
    return get_job_status(api_instance, job)


def validate_job_params(job):
    params = job.params
    text = params.get("text")
    docker_args = params.get("docker", {})
    if text is None or len(text) == 0:
        print("`text` is empty")
        job.set_result(False, "`text` is empty")
        job.to_error(_commit=False)
        job.save()
        return False

    docker_args = params.get('docker', None)
    if docker_args is None:
        print("`docker` is empty")
        job.set_result(False, "`docker` is empty")
        job.to_error(_commit=False)
        job.save()
        return False
    docker_image = docker_args.get("image")
    if docker_image is None:
        print("`docker.image` is empty")
        job.set_result(False, "`docker.image` is empty")
        job.to_error(_commit=False)
        job.save()
        return False
    return True


def clean_k8s_jobs(api_instance):
    pass


def main():
    print("Started dispatcher")
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    while True:
        with application.test_request_context():
            PREHOOK_URL = external_url_for(
                "vqgan.report_job", base=SERVICE_ENDPOINT)
            POSTHOOK_URL = external_url_for(
                "vqgan.report_job", base=SERVICE_ENDPOINT)
            job = get_oldest_pending_job()
            if job is None:
                print("No jobs found")
                time.sleep(3)
                continue

            print(f"Found job, id is {job.id}")
            if not validate_job_params(job):
                print("Invalid job params.")
                continue
            try:
                job.to_in_progress()
                resp = create_k8s_job(batch_v1, job, PREHOOK_URL, POSTHOOK_URL)
            except Exception as e:
                job.set_result(False, f"{e}")
                job.to_error(_commit=False)
                job.save()
                print(f"[ERROR] Failed to dispatch job {job.id}: {e}")
            finally:
                time.sleep(1)


if __name__ == '__main__':
    main()
