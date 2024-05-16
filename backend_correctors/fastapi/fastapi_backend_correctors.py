import contextlib
import os
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

    def __init__(self):
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()

    @staticmethod
    def _create_virtualenv():
        subprocess.run(['python3', '-m', 'venv', 'myenv'])

    def _install_requirements(self, file_path):

        subprocess.run([f'{self._ROOT_DIRECTORY}/../../myenv/bin/pip3', 'install', '-r',
                        file_path])

    def _add_init_file(self):
        # Create __init__.py file in the destination directory
        init_file_path = os.path.join(f'{self._ROOT_DIRECTORY}/../../extracted_exam_files/',
                                      "__init__.py")
        with open(init_file_path, "w"):
            pass  # This creates an empty __init__.py file

    def _copy_api_file(self, file_path):
        shutil.copy(file_path, f'{self._ROOT_DIRECTORY}/../../extracted_exam_files')

    def _run_api(self):

        # Define the Uvicorn command
        uvicorn_command = [
            f"{self._ROOT_DIRECTORY}/../../myenv/bin/uvicorn", "extracted_exam_files.main:app"
        ]
        # time.sleep(1000)

        # Run Uvicorn in the background
        uvicorn_process = subprocess.Popen(uvicorn_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Optionally, you can capture the output
        # stdout, stderr = uvicorn_process.communicate()
        # print(stdout, stderr)
        return uvicorn_process

    @staticmethod
    def _test_get_questions_endpoint():
        response = requests.get("http://localhost:8000/alive")
        if response.status_code == 200:
            print("Server started successfully!")
            # import pdb; pdb.set_trace()
            return response.json() == {'message': "L'API fonctionne"}

    @staticmethod
    def _test_add_questions_endpoint():
        response = requests.post("http://localhost:8000/alive")
        if response.status_code == 200:
            print("Server started successfully!")
            return response.json() == {'message': "L'API fonctionne"}

    @staticmethod
    def _test_health_check_endpoint() -> bool:
        timeout = 50  # in seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            with contextlib.suppress(Exception):
                # Try sending a request to the server
                response = requests.get("http://localhost:8000/alive")

                if response.status_code == 200:
                    print("Server started successfully!")
                    # import pdb; pdb.set_trace()
                    print('--------------------------------------')
                    print(response.json())
                    return response.json() == {'message': "L'API fonctionne"}
            time.sleep(1)
        else:
            print(f"Timeout: Server did not start within {timeout} seconds")

    @staticmethod
    def _terminate_uvicorn_process(uvicorn_process):

        # Terminate the process
        uvicorn_process.terminate()
        # Wait for the process to terminate
        uvicorn_process.wait(timeout=5)
        if uvicorn_process.returncode is None:
            # If the process is still running after timeout, kill it forcefully
            uvicorn_process.kill()

        # Run correction scripts (replace this with your actual correction logic)
        # subprocess.run(['pytest', 'tests'])  # Example: Run tests using pytest
        # subprocess.run(['flake8', 'src'])

    @staticmethod
    def _cleanup():
        # Clean up virtual environment
        shutil.rmtree('myenv')

    def correct_main_file(self, main_file):
        uvicorn_process = None
        flag = None
        try:
            self._add_init_file()
            self._copy_api_file(main_file)
            uvicorn_process = self._run_api()
            flag = self._test_health_check_endpoint()
            flag_1 = self._test_get_questions_endpoint()
            flag_2 = self._test_add_questions_endpoint()

        finally:
            if uvicorn_process:
                self._terminate_uvicorn_process(uvicorn_process)
            self._cleanup()
            return True if flag else False

    def correct_requirements_file(self, requirement_file):
        try:
            self._create_virtualenv()
            self._install_requirements(requirement_file)
            return True
        except Exception as e:
            print(e)
            return False
