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
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from helpers import TarFileHelper


# Test _fetch_tar_files_from_folder method
@pytest.mark.parametrize("test_id, folder_path, expected_files", [
    ("happy_path_1", "tests/folder_with_tar", ["file1.tar", "file2.tar"]),
    ("edge_case_empty_folder", "tests/empty_folder", []),
    ("edge_case_nested_folders", "tests/nested_folders", ["nested/file3.tar"]),
])
def test_fetch_tar_files_from_folder(test_id, folder_path, expected_files, tmp_path):
    # Arrange
    folder = tmp_path / folder_path
    folder.mkdir(parents=True, exist_ok=True)
    for file in expected_files:
        (folder / file).touch()

    # Act
    result_files = TarFileHelper._fetch_tar_files_from_folder(Path(folder))

    # Assert
    assert len(result_files) == len(expected_files)
    assert all(
        [Path(folder / file).name in [result_file.name for result_file in result_files] for file in expected_files])


# Test _extract_tar_file method
@pytest.mark.parametrize("test_id, tar_file_setup, destination_setup, expected_output, expected_exception", [
    ("happy_path_valid_tar", "valid.tar", "destination_folder", "Extraction completed successfully!\n", None),
    ("error_case_file_not_found", "nonexistent.tar", "destination_folder", "The specified file does not exist.\n",
     FileNotFoundError),
    ("error_case_invalid_tar", "invalid.tar", "destination_folder", "The file is not a valid tar file.\n",
     tarfile.ReadError),
    ("error_case_unexpected_error", "unexpected_error.tar", "destination_folder",
     "An error occurred: Mocked exception\n", Exception),
])
def test_extract_tar_file(test_id, tar_file_setup, destination_setup, expected_output, expected_exception, tmp_path,
                          capsys):
    # Arrange
    tar_file = tmp_path / tar_file_setup
    destination = tmp_path / destination_setup
    destination.mkdir(parents=True, exist_ok=True)
    if test_id == "happy_path_valid_tar":
        tar_file.write_text("content")
    elif test_id == "error_case_unexpected_error":
        with patch("tarfile.open", side_effect=Exception("Mocked exception")):
            TarFileHelper._extract_tar_file(tar_file, destination)
            captured = capsys.readouterr()
            assert captured.out == expected_output
            return

    # Act
    if expected_exception:
        with pytest.raises(expected_exception):
            TarFileHelper._extract_tar_file(tar_file, destination)
    else:
        TarFileHelper._extract_tar_file(tar_file, destination)

    # Assert
    captured = capsys.readouterr()
    assert captured.out == expected_output
