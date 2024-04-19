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
#
import concurrent
import os
import shutil
from abc import ABC, ABCMeta
from concurrent import futures
from pathlib import Path

import tqdm
from tabulate import tabulate

from correction_backends.bash_linux_backend_correctors import BashLinuxBackendCorrector
from helpers import TarFileHelper


class ExamCorrectorMeta(ABCMeta):
    def __init__(cls, name, bases, namespace):
        if '_FILES_TO_CORRECT' not in namespace:
            raise AttributeError(f"{cls.__name__} class must define '_FILES_TO_CORRECT'")
        super().__init__(name, bases, namespace)


class ExamCorrector(ABC, TarFileHelper, metaclass=ExamCorrectorMeta):
    _EXAM_FILES_EXTRACTION_TARGET_FOLDER = Path('../extracted_exam_files')
    _FILES_TO_CORRECT = None

    def __init__(self, candidates_exams_path: str, backend_corrector: BashLinuxBackendCorrector):
        self.backend_corrector = backend_corrector
        self._ROOT_DIRECTORY = Path(__file__).parent.absolute()
        self.candidates_exams_path = Path(candidates_exams_path)

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
        try:
            return folder_path.name.split('.')[0].split('_')[1]
        except IndexError:
            return folder_path.name.split('.')[0]

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

    def _clean_environment(self):
        self._clean_extracted_files()

    @staticmethod
    def _fetch_method_name_from_file_name(file_name):
        return f"correct_{file_name.split('.')[0]}_file"

    def _generate_exception_classes(self):
        for file in self._FILES_TO_CORRECT:
            exception_name = f'{file.capitalize()}FileNotFound'
            exception_class = type(exception_name, (FileNotFoundError,), {})
            setattr(self, exception_name, exception_class)

    def _fetch_candidate_files(self, candidate_folder_path):
        self._generate_exception_classes()

        files_found = {file: None for file in self._FILES_TO_CORRECT}
        for root, directories, files in os.walk(candidate_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file in self._FILES_TO_CORRECT:
                    files_found[file] = file_path

        if exceptions := [
            getattr(self, f'{file.capitalize()}FileNotFound')()
            for file, file_path in files_found.items()
            if not file_path
        ]:
            raise ExceptionGroup('Some files were not found', exceptions)
        return files_found

    def _process_candidate(self, candidate_folder_path):
        self._generate_exception_classes()

        candidate_name = self._fetch_candidate_name_from_folder_path(candidate_folder_path)
        description = ''
        error_description_map = {
            f'{file.capitalize()}FileNotFound': f'- {file} file not found'
            for file in self._FILES_TO_CORRECT
        }

        try:
            files_found = self._fetch_candidate_files(candidate_folder_path)
        except ExceptionGroup as e:
            result = 'Failed'
            for exception in e.exceptions:
                description += error_description_map[type(exception).__name__]
        else:
            file_checks = {
                'incorrect': {file: not getattr(self.backend_corrector, f'correct_{file.split('.')[0]}_file')(
                    files_found.get(file))
                              for file
                              in self._FILES_TO_CORRECT}
            }
            for file, failed in file_checks['incorrect'].items():
                if failed:
                    description += error_description_map[f'{file.capitalize()}FileNotFound']

            result = 'Failed' if any(file_checks['incorrect'].values()) else 'Passed'

        return {
            'candidate_name': candidate_name,
            'result': result,
            'remarques supplémentaires': description,
        }

    def correct_candidate_files(self):
        exam_files = self._fetch_exam_files_from_exams_folder()
        for exam_file in exam_files:
            self._extract_exam_file_to_destination(exam_file)
        candidates_folders = self._fetch_candidates_folders()

        # TODO think about making all candidates files processing asynchronous
        with futures.ThreadPoolExecutor() as executor:
            results = list(
                tqdm.tqdm(executor.map(self._process_candidate, candidates_folders),
                          total=len(candidates_folders)))

        candidates_result = list(results)
        self._print_as_table(candidates_result)
        self._clean_environment()
