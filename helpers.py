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
import subprocess
import tarfile
import time
from pathlib import Path


class TarFileHelper:
    @staticmethod
    def _fetch_tar_files_from_folder(folder):
        return list(folder.rglob('*.tar'))

    @staticmethod
    def _extract_tar_file(tar_file, destination):
        try:
            with tarfile.open(tar_file, 'r') as tar:
                tar.extractall(path=destination)
            # print("Extraction completed successfully!")
        except FileNotFoundError:
            print("The specified file does not exist.")
        except tarfile.ReadError:
            print("The file is not a valid tar file.")
        except Exception as e:
            print(f"An error occurred: {e}")


class ProcessRunnerHelper:
    @staticmethod
    def release_port(port):
        try:
            # Check for processes using the port
            process = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if process.returncode != 0:
                return f"Failed to release port {port}."
            pids = process.stdout.split()
            # Kill the processes using the port
            for pid in pids:
                subprocess.run(['kill', pid])
            return f"Port {port} released successfully."
        except Exception as e:
            return f"Error while releasing port {port}: {e}"

    @staticmethod
    def _run_script(script_file: Path, timeout=3) -> str:
        try:
            # Execute the script with timeout
            process = subprocess.Popen([script_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            start_time = time.time()

            while process.poll() is None:
                time.sleep(0.1)
                if time.time() - start_time > timeout:
                    process.kill()
                    return "Execution timed out after 3 seconds."

            # Capture output
            stdout, stderr = process.communicate()

            # Check if there was any error during execution
            if process.returncode != 0:
                return f"Error: {stderr.decode()}"

            # Return the output
            return stdout.decode()
        except Exception as e:
            return f"Error during execution: {e}"
