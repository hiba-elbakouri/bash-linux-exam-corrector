from pathlib import Path

from backend_correctors.interfaces import BackendCorrector
from helpers import FileHelper, ProcessRunnerHelper


class MongoDbBackendCorrector(metaclass=BackendCorrector):
    _FILES_TO_CORRECT = []


class MongoDBBackendCorrector(metaclass=BackendCorrector):
    _FILES_TO_CORRECT = []


class SimpleMongoDbBackendCorrector(MongoDBBackendCorrector, FileHelper, ProcessRunnerHelper):

    def __init__(self):
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()
