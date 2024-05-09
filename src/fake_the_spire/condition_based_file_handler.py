import logging
from pathlib import Path
import datetime
import socket


class ConditionBasedFileHandler(logging.FileHandler):
    _file_count = 0

    def __init__(self, mode='a', encoding=None, delay=False):
        # Set the initial log file based on current time
        _file_count = 0
        filename = self.generate_filename()
        super().__init__(filename, mode, encoding, delay)
        self.baseFilename = str(Path(filename))

    def emit(self, record):
        """
        Overwrite the emit method to check the condition before logging.
        """
        logging.FileHandler.emit(self, record)

        if self.check_condition(record):
            self.rotate_log()

    @staticmethod
    def check_condition(record):
        """
        Define your condition here. This function should return True when the log file needs to be rotated.
        """
        if record.levelname == 'INFO' and 'GameOver' in record.getMessage():
            return True
        return False

    def rotate_log(self):
        # Generate a new filename and rotate to it
        self.close()  # Close the current file
        new_filename = self.generate_filename()

        self.baseFilename = str(Path(new_filename))
        # Update the current file path
        if not self.delay:
            self.stream = self._open()  # Reopen the file stream

    @staticmethod
    def generate_filename():
        # Generate a filename based on the current timestamp with an incrementing counter
        directory = Path(__file__).resolve().parent.parent.parent / 'logs'
        directory.mkdir(exist_ok=True)  # Ensure the directory exists
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"log_{current_time}_{ConditionBasedFileHandler._file_count}.log"
        ConditionBasedFileHandler._file_count += 1  # Increment the counter
        return str(directory / filename)


def setup_logging():
    handler = ConditionBasedFileHandler()  # Initial log file name, will be renamed upon condition
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger('flask_app')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
