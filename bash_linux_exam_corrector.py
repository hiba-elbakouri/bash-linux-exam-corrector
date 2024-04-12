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
import shutil
import sys
from pathlib import Path

import tqdm
from tabulate import tabulate

from correction_backends.interfaces import BashLinuxBackendCorrector
from correction_backends.simple_backend_corrector import SimpleBashLinuxBackendCorrector
from helpers import TarFileHelper
from interfaces import ExamCorrector


class BashLinuxExamCorrector(ExamCorrector, TarFileHelper):
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

    class CronFileNotFound(FileNotFoundError):
        pass

    class SalesFileNotFound(FileNotFoundError):
        pass

    class ScriptFileNotFound(FileNotFoundError):
        pass

    def __init__(self, candidates_exams_path: str, corrector: BashLinuxBackendCorrector,
                 correct_exam_path: str = None) -> None:
        self.correct_exam_path = Path(correct_exam_path) if correct_exam_path else None
        self.candidates_exams_path = Path(candidates_exams_path)
        self.corrector = corrector
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()

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
                'cron_incorrect': not self.corrector.correct_cron_file(cron_file),
                'script_incorrect': not self.corrector.correct_script_file(script_file),
                'sales_incorrect': not self.corrector.correct_sales_file(sales_file)
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
        self._clean_extracted_files()

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

    corrector = BashLinuxExamCorrector(exams_folder, SimpleBashLinuxBackendCorrector())
    corrector.correct_candidate_files()
