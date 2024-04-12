import pytest

from correction_backends.simple_backend_corrector import SimpleBashLinuxBackendCorrector


@pytest.mark.parametrize("output,expected", [
    # ID: HappyPath-ValidOutput
    ("Thu Mar 04 12:00:00 UTC 2021\nrtx3060: 5\nrtx3070: 10\nrtx3080: 15\nrtx3090: 20\nrx6700: 25\n", True),
    # ID: EdgeCase-MinimalValidOutput
    ("Thu Mar 04 12:00:00 UTC 2021\nrtx3060: 1\nrtx3070: 1\nrtx3080: 1\nrtx3090: 1\nrx6700: 1\n", True),
    # ID: ErrorCase-InvalidDate
    ("Invalid Date\nrtx3060: 5\nrtx3070: 10\nrtx3080: 15\nrtx3090: 20\nrx6700: 25\n", False),
    # ID: ErrorCase-MissingGPUType
    ("Thu Mar 04 12:00:00 UTC 2021\nrtx3060: 5\nrtx3070: 10\nrtx3080: 15\nrtx3090: 20\n", False),
    # ID: ErrorCase-ExtraGPUType
    ("Thu Mar 04 12:00:00 UTC 2021\nrtx3060: 5\nrtx3070: 10\nrtx3080: 15\nrtx3090: 20\nrx6700: 25\nrx6800: 30\n", True),
    # ID: ErrorCase-EmptyOutput
    ("", False),
], ids=["HappyPath-ValidOutput", "EdgeCase-MinimalValidOutput", "ErrorCase-InvalidDate", "ErrorCase-MissingGPUType",
        "ErrorCase-ExtraGPUType", "ErrorCase-EmptyOutput"])
def test_correct_script_output(output, expected):
    # Arrange
    corrector = SimpleBashLinuxBackendCorrector()

    # Act
    result = corrector._correct_script_output(output)

    # Assert
    assert result == expected


@pytest.mark.parametrize("file_content,expected", [
    # ID: HappyPath-ValidSalesFile
    ("Thu Mar 04 12:00:00 UTC 2021\nrtx3060: 5\nrtx3070: 10\nrtx3080: 15\nrtx3090: 20\nrx6700: 25\n", True),
    # ID: ErrorCase-InvalidSalesFile
    ("Invalid content", False),
], ids=["HappyPath-ValidSalesFile", "ErrorCase-InvalidSalesFile"])
def test_correct_sales_file(tmp_path, file_content, expected):
    # Arrange
    sales_file = tmp_path / "sales.txt"
    sales_file.write_text(file_content)
    corrector = SimpleBashLinuxBackendCorrector()

    # Act
    result = corrector.correct_sales_file(sales_file)

    # Assert
    assert result == expected


@pytest.mark.parametrize("cron_content,expected", [
    # ID: HappyPath-ValidCron
    ("* * * * * /path/to/script.sh", True),
    # ID: ErrorCase-InvalidCronFormat
    ("invalid cron format", False),
    # ID: ErrorCase-InvalidCronSchedule
    ("* * * * /path/to/script.sh", False),
], ids=["HappyPath-ValidCron", "ErrorCase-InvalidCronFormat", "ErrorCase-InvalidCronSchedule"])
def test_correct_cron_file(tmp_path, cron_content, expected):
    # Arrange
    cron_file = tmp_path / "cron.txt"
    cron_file.write_text(cron_content)
    corrector = SimpleBashLinuxBackendCorrector()

    # Act
    result = corrector.correct_cron_file(cron_file)

    # Assert
    assert result == expected
