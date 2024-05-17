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
import contextlib
import json
import shutil
import subprocess
import time
from pathlib import Path
import requests
from backend_correctors.interfaces import BackendCorrector
from helpers import FileHelper, ProcessRunnerHelper


class FastApiBackendCorrector(metaclass=BackendCorrector):
    _MAIN_FILE = 'main.py'
    _FILES_TO_CORRECT = [_MAIN_FILE]


class SimpleFastApiBackendCorrector(FastApiBackendCorrector, FileHelper, ProcessRunnerHelper):
    BASE_URL = "http://localhost:8000"
    ENDPOINTS = {
        "questions": f"{BASE_URL}/questions",
        "add_questions": f"{BASE_URL}/add-questions",
        "alive": f"{BASE_URL}/alive"
    }
    AUTH = ("admin", "4dm1N")
    TEMPLATE_KEYS = {
        "question", "subject", "use", "correct", "responseA",
        "responseB", "responseC", "responseD", "remark"
    }

    def __init__(self):
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()
        self._env_path = self._ROOT_DIRECTORY / "../../myenv"
        self._extracted_path = self._ROOT_DIRECTORY / "../../extracted_exam_files"

    @staticmethod
    def _create_virtualenv():
        subprocess.run(['python3', '-m', 'venv', 'myenv'], check=True)

    def _install_requirements(self, file_path):
        subprocess.run([self._env_path / 'bin' / 'pip3', 'install', '-r', file_path], check=True)

    def _add_init_file(self):
        init_file_path = self._extracted_path / "__init__.py"
        init_file_path.touch()

    def _copy_api_file(self, file_path):
        shutil.copy(file_path, self._extracted_path)

    def _run_api(self):
        uvicorn_command = [
            str(self._env_path / 'bin' / 'uvicorn'), "extracted_exam_files.main:app"
        ]
        return subprocess.Popen(uvicorn_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def _fetch_response(endpoint):
        response = requests.get(endpoint, auth=SimpleFastApiBackendCorrector.AUTH)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def _responses_are_different(response_1, response_2):
        return json.dumps(response_1, sort_keys=True) != json.dumps(response_2, sort_keys=True)

    @staticmethod
    def _test_if_get_questions_endpoint_response_is_random():
        response_1 = SimpleFastApiBackendCorrector._fetch_response(SimpleFastApiBackendCorrector.ENDPOINTS["questions"])
        time.sleep(1)
        response_2 = SimpleFastApiBackendCorrector._fetch_response(SimpleFastApiBackendCorrector.ENDPOINTS["questions"])
        return SimpleFastApiBackendCorrector._responses_are_different(response_1, response_2)

    @staticmethod
    def _test_get_questions_endpoint_response_structure():
        response = SimpleFastApiBackendCorrector._fetch_response(SimpleFastApiBackendCorrector.ENDPOINTS["questions"])
        if response and isinstance(response, list):
            return all(
                isinstance(item, dict) and set(item.keys()) == SimpleFastApiBackendCorrector.TEMPLATE_KEYS
                for item in response
            )
        return False

    def _test_get_questions_endpoint_response(self):
        structure_valid = self._test_get_questions_endpoint_response_structure()
        response_is_random = self._test_if_get_questions_endpoint_response_is_random()
        return structure_valid and response_is_random

    @staticmethod
    def _test_add_questions_endpoint():
        response = requests.post(SimpleFastApiBackendCorrector.ENDPOINTS["add_questions"],
                                 auth=SimpleFastApiBackendCorrector.AUTH)
        return response.status_code == 200 and response.json() == {"Message": "La question a bien été ajoutée"}

    @staticmethod
    def _test_health_check_endpoint(timeout=50):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with contextlib.suppress(Exception):
                response = requests.get(SimpleFastApiBackendCorrector.ENDPOINTS["alive"])
                if response.status_code == 200 and response.json() == {'message': "L'API fonctionne"}:
                    return True
            time.sleep(1)
        print(f"Timeout: Server did not start within {timeout} seconds")
        return False

    @staticmethod
    def _terminate_uvicorn_process(uvicorn_process):
        uvicorn_process.terminate()
        try:
            uvicorn_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            uvicorn_process.kill()

    @staticmethod
    def _cleanup():
        shutil.rmtree('myenv')

    def correct_main_file(self, main_file):
        uvicorn_process = None
        try:
            self._add_init_file()
            self._copy_api_file(main_file)
            uvicorn_process = self._run_api()
            health_check_passed = self._test_health_check_endpoint()
            questions_endpoint_valid = self._test_get_questions_endpoint_response()
            add_questions_endpoint_valid = self._test_add_questions_endpoint()
            return health_check_passed and questions_endpoint_valid and add_questions_endpoint_valid
        finally:
            if uvicorn_process:
                self._terminate_uvicorn_process(uvicorn_process)
            self._cleanup()

    def correct_requirements_file(self, requirement_file):
        try:
            self._create_virtualenv()
            self._install_requirements(requirement_file)
            return True
        except Exception as e:
            print(e)
            return False
