from .base import BaseParams, BaseResult


class DockerTaskParams(BaseParams):

    def __init__(self, **kwargs):
        super(DockerTaskParams, self).__init__(**kwargs)
        self.docker_image = kwargs.get("docker_image")
        self.docker_command = kwargs.get("docker_command")
        self.docker_volume = kwargs.get("docker_volume")
        self.docker_ports = kwargs.get("docker_ports")

    def to_dict(self):
        dict_ = self.to_dict()
        return {
            "docker_image": self.docker_image,
            "docker_command": self.docker_command,
            "docker_volume": self.docker_volume,
            "docker_ports": self.docker_ports,
            **dict_,
        }


class DockerTaskResult(BaseResult):

    def __init__(self, **kwargs):
        super(DockerTaskResult, self).__init__(**kwargs)
