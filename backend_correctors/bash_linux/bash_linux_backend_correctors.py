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
import os
import re
from pathlib import Path

from croniter import croniter

from backend_correctors.interfaces import BackendCorrector
from helpers import FileHelper, ProcessRunnerHelper


class BashLinuxBackendCorrector(metaclass=BackendCorrector):
    _CRON_FILE = 'cron.txt'
    _SALES_FILE = 'sales.txt'
    _SCRIPT_FILE = 'exam.sh'
    _FILES_TO_CORRECT = [_CRON_FILE, _SALES_FILE, _SCRIPT_FILE]


class SimpleBashLinuxBackendCorrector(BashLinuxBackendCorrector, FileHelper, ProcessRunnerHelper):
    _API_PORT = '5000'
    _OUTPUT_REGEX = (r'\b\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} UTC \d{4}\n(?:rtx3060: ?\d+\n|rtx3070: ?\d+\n|rtx3080: ?'
                     r'\d+\n|rtx3090: ?\d+\n|rx6700: ?\d+\n)+')

    def __init__(self):
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()
        self._API_SCRIPT = self._ROOT_DIRECTORY / Path('api')

    def _correct_script_output(self, output: str):
        matches = re.findall(self._OUTPUT_REGEX, output)
        if not matches:
            return False
        # Check if all GPU types appear in every occurrence
        gpu_types = {'rtx3060', 'rtx3070', 'rtx3080', 'rtx3090', 'rx6700'}
        for match in matches:
            gpu_occurrences = re.findall(r'(rtx\d+|rx\d+: ?\d+)', match)
            matched_gpu_types = {
                gpu_occurrence.split(':')[0]
                for gpu_occurrence in gpu_occurrences
            }
            if not gpu_types.issubset(matched_gpu_types):
                return False
        return True

    def _run_script_file(self, script_file: Path):
        return self._run_script(script_file)

    def _run_api_in_background(self):
        self._release_port(self._API_PORT)
        self._run_script(self._API_SCRIPT)

    def _clean_up_bash_file(self, bash_file_path: Path):
        self._remove_empty_lines(bash_file_path)
        self._remove_comments_from_bash_file(bash_file_path)

    @staticmethod
    def _replace_candidate_path_by_local_path(bash_file_path: Path):
        try:
            if not os.access(bash_file_path, os.W_OK):
                # Change the permission of the script file to make it executable
                os.chmod(bash_file_path, 0o744)  # 0o755 sets permission to rwxr-xr-x
            # Read the content of the bash file
            with open(bash_file_path, 'r') as file:
                bash_script = file.read()

            # Use regular expression to replace the text after >>
            modified_script = re.sub(r'>>\s*\S+', '>> sales_1.txt', bash_script)

            with open(bash_file_path, 'w') as file:
                file.write(modified_script)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def correct_exam_file(self, script_file: Path):
        # TODO check the correctness of the script output
        self._replace_candidate_path_by_local_path(script_file)
        self._clean_up_bash_file(script_file)

        self._run_api_in_background()
        script_output = self._run_script_file(script_file)
        self._release_port(self._API_PORT)
        return 'Error' not in script_output

    def correct_sales_file(self, sales_file):
        self._clean_up_ordinary_file(sales_file)
        # Define the regex pattern
        with open(sales_file, 'r') as file:
            file_content = file.read()
            return self._correct_script_output(file_content)

    def correct_cron_file(self, cron_file):
        self._clean_up_cron_file(cron_file)
        try:
            with open(cron_file, 'r') as file:
                for line_number, line in enumerate(file, start=1):

                    # Split the line into fields (schedule and command)
                    fields = line.strip().split(maxsplit=5)
                    if len(fields) != 6:
                        print(f"Error in line {line_number}: Invalid cron format")
                        return False

                    schedule = ' '.join(fields[:5])
                    script_path = fields[5]

                    # Validate the cron schedule
                    try:
                        croniter(schedule)
                    except ValueError:
                        print(f"Error in line {line_number}: Invalid cron schedule")
                        return False

                    # # Validate the script path
                    # if not os.path.isfile(script_path):
                    #     print(f"Error in line {line_number}: Script file not found")
                    #     return False

        except FileNotFoundError:
            print(f"Error: File '{cron_file}' not found")
            return False

        return True
