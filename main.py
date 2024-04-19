import sys

from correction_backends.bash_linux_backend_correctors import SimpleBashLinuxBackendCorrector
from exams_correctors.bash_linux_exam_correctors import BashLinuxExamCorrector

if __name__ == '__main__':
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python bash_linux_exam_corrector.py <path_to_exams_folder>")
        sys.exit(1)

    exams_folder = sys.argv[1]  # Get the argument from command line

    corrector = BashLinuxExamCorrector(exams_folder, SimpleBashLinuxBackendCorrector())
    corrector.correct_candidate_files()
