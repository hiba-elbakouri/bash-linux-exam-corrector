import argparse

from correction_backends.bash_linux_backend_correctors import SimpleBashLinuxBackendCorrector
from correction_backends.fastapi.fastapi_backend_correctors import SimpleFastApiBackendCorrector
from exams_correctors.bash_linux_exam_correctors import BashLinuxExamCorrector
from exams_correctors.fastapi_exam_correctors import FastApiExamCorrector

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bash Linux Exam Corrector')
    parser.add_argument('path_to_exams_folder', help='Path to the exams folder')
    parser.add_argument('--type', choices=['bash', 'fastapi'], default='bash',
                        help='Type of corrector to use (default: bash)')
    parser.add_argument('--show-only-failed-exams', action='store_true',
                        help='Show only the failed exams')
    args = parser.parse_args()

    exams_folder = args.path_to_exams_folder
    corrector_type = args.type

    backend_corrector = SimpleBashLinuxBackendCorrector() if corrector_type == 'bash' else (
        SimpleFastApiBackendCorrector())
    ExamCorrector = BashLinuxExamCorrector if corrector_type == 'bash' else FastApiExamCorrector

    # TODO check backend corrector typing
    corrector = ExamCorrector(exams_folder, backend_corrector, args.show_only_failed_exams)
    corrector.correct_candidate_files()
