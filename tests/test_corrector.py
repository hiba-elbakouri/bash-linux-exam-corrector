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
from unittest.mock import patch, MagicMock
import pytest
from exams_correctors.bash_linux_exam_correctors import BashLinuxExamCorrector
from helpers import TarFileHelper, ProcessRunnerHelper


# Assuming the presence of a mock Corrector interface and necessary mock files for testing

class MockCorrector:
    pass


def create_mock_exam_files(num_files):
    return [f"exam_{i}.tar" for i in range(1, num_files + 1)]


def create_mock_sales_file(valid=True):
    content = "Thu Mar 3 12:00:00 UTC 2022\nrtx3060:5\nrtx3070:10\nrtx3080:15\nrtx3090:20\nrx6700:25"
    if not valid:
        content = "Invalid content"
    with open("mock_sales.txt", "w") as file:
        file.write(content)


# Parametrized test for the happy path of correct_candidate_files method
@pytest.mark.parametrize("exam_files, expected_result", [
    (create_mock_exam_files(num_files=3), "Passed"),
], ids=["happy-path-correct-candidate-files"])
def test_correct_candidate_files_happy_path(exam_files, expected_result):
    # Arrange
    corrector = BashLinuxExamCorrector(candidates_exams_path="/mock/path", corrector=MockCorrector())
    create_mock_sales_file(valid=True)  # Creates a mock sales file with valid content

    # Act
    with patch.object(TarFileHelper, '_fetch_tar_files_from_folder', return_value=exam_files), \
            patch.object(ProcessRunnerHelper, '_correct_sales_file', return_value=True), \
            patch('builtins.print', MagicMock()):
        result = corrector.correct_candidate_files()

    # Assert
    assert all(candidate['result'] == expected_result for candidate in result), "All candidates should pass"


# Parametrized test for various edge cases in correct_candidate_files method
@pytest.mark.parametrize("exam_files, expected_result", [
    (create_mock_exam_files(num_files=0), "Failed"),
], ids=["edge-case-no-exam-files"])
def test_correct_candidate_files_edge_cases(exam_files, expected_result):
    # Arrange
    corrector = BashLinuxExamCorrector(candidates_exams_path="/mock/path", corrector=MockCorrector())
    create_mock_sales_file(valid=False)  # Creates a mock sales file with invalid content

    # Act
    with patch.object(TarFileHelper, '_fetch_tar_files_from_folder', return_value=exam_files), \
            patch.object(ProcessRunnerHelper, '_correct_sales_file', return_value=False), \
            patch('builtins.print', MagicMock()):
        result = corrector.correct_candidate_files()

    # Assert
    assert all(
        candidate['result'] == expected_result for candidate in result), "All candidates should fail due to edge cases"


# Parametrized test for various error cases in correct_candidate_files method
@pytest.mark.parametrize("exception, expected_result", [
    (FileNotFoundError, "Failed"),
], ids=["error-case-file-not-found"])
def test_correct_candidate_files_error_cases(exception, expected_result):
    # Arrange
    corrector = BashLinuxExamCorrector(candidates_exams_path="/mock/path", corrector=MockCorrector())

    # Act
    with patch.object(TarFileHelper, '_fetch_tar_files_from_folder', side_effect=exception), \
            patch('builtins.print', MagicMock()):
        result = corrector.correct_candidate_files()

    # Assert
    assert all(candidate['result'] == expected_result for candidate in
               result), "All candidates should fail due to file not found error"
