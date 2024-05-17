from pathlib import Path

from backend_correctors.interfaces import BackendCorrector
from helpers import FileHelper, ProcessRunnerHelper


class DockerBackendCorrector(metaclass=BackendCorrector):
    _DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    _FILES_TO_CORRECT = [_DOCKER_COMPOSE_FILE]


class SimpleDockerBackendCorrector(DockerBackendCorrector, FileHelper, ProcessRunnerHelper):

    def __init__(self):
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()

    def correct_docker_compose_file(self, main_file):
        pass
