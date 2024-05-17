# Copyright (c) 2024. THIS SOURCE CODE BELONGS TO DATASCIENTEST. ANY OUTSIDER REPLICATION OF IT IS LEGALLY
# PERSECUTED
#  _______      ___    ___ ________  _____ ______
# |\  ___ \    |\  \  /  /|\   __  \|\   _ \  _   \
# \ \   __/|   \ \  \/  / | \  \|\  \ \  \\\__\ \  \
#  \ \  \_|/__  \ \    / / \ \   __  \ \  \\|__| \  \
#   \ \  \_|\ \  /     \/   \ \  \ \  \ \  \    \ \  \
#    \ \_______\/  /\   \    \ \__\ \__\ \__\    \ \__\
#     \|_______/__/ /\ __\    \|__|\|__|\|__|     \|__|
#              |__|/ \|__|
#  ________  ________  ________  ________  _______   ________ _________  ________  ________
# |\   ____\|\   __  \|\   __  \|\   __  \|\  ___ \ |\   ____\\___   ___\\   __  \|\   __  \
# \ \  \___|\ \  \|\  \ \  \|\  \ \  \|\  \ \   __/|\ \  \___\|___ \  \_\ \  \|\  \ \  \|\  \
#  \ \  \    \ \  \\\  \ \   _  _\ \   _  _\ \  \_|/_\ \  \       \ \  \ \ \  \\\  \ \   _  _\
#   \ \  \____\ \  \\\  \ \  \\  \\ \  \\  \\ \  \_|\ \ \  \____   \ \  \ \ \  \\\  \ \  \\  \|
#    \ \_______\ \_______\ \__\\ _\\ \__\\ _\\ \_______\ \_______\  \ \__\ \ \_______\ \__\\ _\
#     \|_______|\|_______|\|__|\|__|\|__|\|__|\|_______|\|_______|   \|__|  \|_______|\|__|\|__|
#
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
