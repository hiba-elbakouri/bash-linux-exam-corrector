import shutil
import subprocess

import pytest

from backend_correctors.interfaces import BackendCorrector
from helpers import FileHelper, ProcessRunnerHelper


class FastApiBackendCorrector(metaclass=BackendCorrector):
    _MAIN_FILE = 'main.py'
    _FILES_TO_CORRECT = [_MAIN_FILE]


class SimpleFastApiBackendCorrector(FastApiBackendCorrector, FileHelper, ProcessRunnerHelper):
    @staticmethod
    def _create_virtualenv():
        # Create a virtual environment
        subprocess.run(['virtualenv', '-p', 'python3.12', 'myenv'])

    @staticmethod
    def _install_requirements():
        # Activate virtual environment
        activate_script = 'myenv/bin/activate'
        activate_cmd = f'source {activate_script}'

        # Install requirements
        subprocess.run([activate_cmd, '&&', 'pip', 'install', '-r', 'requirements.txt'])

    @staticmethod
    def _run_api():
        subprocess.Popen(['uvicorn', 'your_fastapi_script:app', '--reload'])

    @staticmethod
    def _test_api():
        try:
            # Run the tests using the pytest programmatic API
            result_code = pytest.main(
                ["-q", "test_module.py"])  # Replace "test_module.py" with the name of your test module

            # Check the result code
            if result_code == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred while running tests: {e}")
            return False

    @staticmethod
    def _cleanup():
        # Clean up virtual environment
        shutil.rmtree('myenv')

    def correct_main_file(self):
        try:
            self._create_virtualenv()
            self._install_requirements()
            self._run_api()
            self._test_api()
        finally:
            self._cleanup()
