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
import concurrent
import os
import re
import shutil
import sys
from pathlib import Path

import tqdm
from croniter import croniter
from tabulate import tabulate

from helpers import TarFileHelper, ProcessRunnerHelper, FileHelper
from interfaces import ExamCorrector, ExamCorrectorBackend


class BashLinuxExamCorrector(ExamCorrector, TarFileHelper, ProcessRunnerHelper, FileHelper):
    """
     A class to correct Linux exam files for candidates.

     This class provides methods to fetch, extract, correct, and clean up exam files for candidates.
     It includes functionality to handle cron, sales, and script files, and processes candidate files in a structured
     manner.

     Args:
         candidates_exams_path (str): The path to the candidates' exam files.
         corrector (ExamCorrectorBackend, optional): An instance of ExamCorrectorBackend for correction. Defaults to
         None.
         correct_exam_path (str, optional): The path to the correct exam file. Defaults to None.

     Raises:
         FileNotFoundError: If the cron, sales, or script file is not found during processing.

     Returns:
         None
     """
    _EXAM_FILES_EXTRACTION_TARGET_FOLDER = Path('extracted_exam_files')

    _CRON_FILE = 'cron.txt'
    _SALES_FILE = 'sales.txt'
    _SCRIPT_FILE = 'exam.sh'
    _OUTPUT_REGEX = (r'\b\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} UTC \d{4}\n(?:rtx3060: \d+\n|rtx3070: \d+\n|rtx3080: '
                     r'\d+\n|rtx3090: \d+\n|rx6700: \d+\n)+')
    _API_PORT = '5000'

    class CronFileNotFound(FileNotFoundError):
        pass

    class SalesFileNotFound(FileNotFoundError):
        pass

    class ScriptFileNotFound(FileNotFoundError):
        pass

    def __init__(self, candidates_exams_path: str, corrector: ExamCorrectorBackend = None,
                 correct_exam_path: str = None) -> None:
        self.correct_exam_path = Path(correct_exam_path) if correct_exam_path else None
        self.candidates_exams_path = Path(candidates_exams_path)
        self.corrector = corrector
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()
        self._API_SCRIPT = self._ROOT_DIRECTORY / Path('api')

    def _fetch_exam_files_from_exams_folder(self):
        return self._fetch_tar_files_from_folder(self.candidates_exams_path)

    def _extract_exam_file_to_destination(self, exam_file):
        destination = self._ROOT_DIRECTORY / self._EXAM_FILES_EXTRACTION_TARGET_FOLDER / exam_file.name
        destination.mkdir(parents=True, exist_ok=True)
        self._extract_tar_file(exam_file, destination)

    def _fetch_candidates_folders(self):
        return [item for item in (self._ROOT_DIRECTORY / self._EXAM_FILES_EXTRACTION_TARGET_FOLDER).iterdir() if
                item.is_dir()]

    @staticmethod
    def _fetch_candidate_name_from_folder_path(folder_path):
        return folder_path.name.split('.')[0].split('_')[1]

    def _fetch_candidate_files(self, candidate_folder_path):
        # TODO treat the case if other files exist, in this case we should decide if there is no problem with that
        #  or the candidate should fail giving the fact that he delivered unnecessary files
        cron_file = None
        script_file = None
        sales_file = None
        for root, directories, files in os.walk(candidate_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file == self._CRON_FILE:
                    cron_file = file_path
                elif file == self._SCRIPT_FILE:
                    script_file = file_path
                elif file == self._SALES_FILE:
                    sales_file = file_path
        exceptions = []
        if not cron_file:
            exceptions.append(self.CronFileNotFound())
        if not sales_file:
            exceptions.append(self.SalesFileNotFound())
        if not script_file:
            exceptions.append(self.ScriptFileNotFound())
        if exceptions:
            raise ExceptionGroup('this is was bad', exceptions)
        return cron_file, script_file, sales_file

    def _correct_cron_file(self, cron_file):
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

    def _correct_script_output(self, output: str):
        matches = re.findall(self._OUTPUT_REGEX, output)
        if not matches:
            return False
        # Check if all GPU types appear in every occurrence
        gpu_types = {'rtx3060', 'rtx3070', 'rtx3080', 'rtx3090', 'rx6700'}
        for match in matches:
            gpu_occurrences = re.findall(r'(rtx\d+|rx\d+): \d+', match)
            matched_gpu_types = {
                gpu_occurrence.split(':')[0]
                for gpu_occurrence in gpu_occurrences
            }
            if not gpu_types.issubset(matched_gpu_types):
                return False
        return True

    def _correct_sales_file(self, sales_file):
        self._clean_up_ordinary_file(sales_file)
        # Define the regex pattern
        with open(sales_file, 'r') as file:
            file_content = file.read()
            return self._correct_script_output(file_content)

    def _run_api_in_background(self):
        self._release_port(self._API_PORT)
        self._run_script(self._API_SCRIPT)

    def _run_script_file(self, script_file: Path):
        return self._run_script(script_file)

    @staticmethod
    def _replace_candidate_path_by_local_path(script_file: Path):
        with open(script_file, 'r') as infile, open(script_file, 'w') as outfile:
            for line in infile:
                # Replace any occurrence of the specified directory path with "sales.txt"
                modified_line = re.sub(r'\/(?:[^/]+\/)*sales\.txt', 'sales_1.txt', line)
                # Write the modified line to the output file
                outfile.write(modified_line)

    def _correct_script_file(self, script_file: Path):
        self._replace_candidate_path_by_local_path(script_file)
        self._clean_up_bash_file(script_file)

        self._run_api_in_background()
        script_output = self._run_script_file(script_file)
        return not 'Error' in script_output

    def _clean_extracted_files(self):
        folder = self._ROOT_DIRECTORY / self._EXAM_FILES_EXTRACTION_TARGET_FOLDER
        try:
            shutil.rmtree(folder)
        except OSError as e:
            print(f"Error: {folder} could not be removed. Reason: {e}")

    @staticmethod
    def _print_as_table(data):
        headers = data[0].keys()

        table_data = [[d[key] for key in headers] for d in data]

        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def _process_candidate(self, candidate_folder_path):
        candidate_name = self._fetch_candidate_name_from_folder_path(candidate_folder_path)
        description = ''
        error_description_map = {
            self.CronFileNotFound: '- cron file not found',
            self.ScriptFileNotFound: '- script file not found',
            self.SalesFileNotFound: '- sales file not found',
            'cron_incorrect': '- cron file is not correct',
            'script_incorrect': '- script file is not correct',
            'sales_incorrect': '- sales file is not correct'
        }
        try:
            cron_file, script_file, sales_file = self._fetch_candidate_files(candidate_folder_path)
        except ExceptionGroup as e:
            result = 'Failed'
            for exception in e.exceptions:
                description += error_description_map[type(exception)]
        else:
            file_checks = {
                'cron_incorrect': not self._correct_cron_file(cron_file),
                'script_incorrect': not self._correct_script_file(script_file),
                'sales_incorrect': not self._correct_sales_file(sales_file)
            }
            for check, failed in file_checks.items():
                if failed:
                    description += error_description_map[check]

            result = 'Failed' if any(file_checks.values()) else 'Passed'

        return {
            'candidate_name': candidate_name,
            'result': result,
            'remarques supplémentaires': description,
        }

    def _clean_environment(self):
        self._release_port(self._API_PORT)
        # self._clean_extracted_files()

    def correct_candidate_files(self):
        exam_files = self._fetch_exam_files_from_exams_folder()
        for exam_file in exam_files:
            self._extract_exam_file_to_destination(exam_file)
        candidates_folders = self._fetch_candidates_folders()

        # TODO think about making all candidates files processing asynchronous
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(
                tqdm.tqdm(executor.map(self._process_candidate, candidates_folders), total=len(candidates_folders)))

        candidates_result = list(results)
        self._print_as_table(candidates_result)
        self._clean_environment()


if __name__ == '__main__':
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python bash_linux_exam_corrector.py <path_to_exams_folder>")
        sys.exit(1)

    exams_folder = sys.argv[1]  # Get the argument from command line

    corrector = BashLinuxExamCorrector(exams_folder)
    corrector.correct_candidate_files()
