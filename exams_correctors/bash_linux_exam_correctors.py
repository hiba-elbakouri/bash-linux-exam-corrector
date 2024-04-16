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
import sys

from correction_backends.bash_linux_backend_backend_correctors import SimpleBashLinuxBackendCorrector
from exams_correctors.interfaces import ExamCorrector


class BashLinuxExamCorrector(ExamCorrector):
    """
     A class to correct Linux exam files for candidates.

     This class provides methods to fetch, extract, correct, and clean up exam files for candidates.
     It includes functionality to handle cron, sales, and script files, and processes candidate files in a structured
     manner.

     Raises:
         FileNotFoundError: If the cron, sales, or script file is not found during processing.

     Returns:
         None
     """

    _CRON_FILE = 'cron.txt'
    _SALES_FILE = '../sales.txt'
    _SCRIPT_FILE = 'exam.sh'

    _FILES_TO_CORRECT = [_CRON_FILE, _SALES_FILE, _SCRIPT_FILE]


class MongoDBExamCorrector(ExamCorrector):
    """
     A class to correct Linux exam files for candidates.

     This class provides methods to fetch, extract, correct, and clean up exam files for candidates.
     It includes functionality to handle cron, sales, and script files, and processes candidate files in a structured
     manner.

     Raises:
         FileNotFoundError: If the cron, sales, or script file is not found during processing.

     Returns:
         None
     """

    _FILE_1 = 'hiba.txt'
    _FILE_2 = 'simo.txt'
    _FILE_2 = 'fo9ma.sh'

    _FILES_TO_CORRECT = [_FILE_1, _FILE_2, _FILE_2]


if __name__ == '__main__':
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python bash_linux_exam_corrector.py <path_to_exams_folder>")
        sys.exit(1)

    exams_folder = sys.argv[1]  # Get the argument from command line

    corrector = BashLinuxExamCorrector(exams_folder, SimpleBashLinuxBackendCorrector())
    corrector.correct_candidate_files()
