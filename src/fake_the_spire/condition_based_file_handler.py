import logging
from pathlib import Path
import datetime


class ConditionBasedFileHandler(logging.FileHandler):
    def __init__(self, mode='a', encoding=None, delay=False):
        # Set the initial log file based on current time
        filename = self.generate_filename()
        super().__init__(filename, mode, encoding, delay)
        self.baseFilePath = Path(filename)

    @staticmethod
    def generate_filename():
        # Generate a filename based on the current timestamp
        directory = Path(__file__).resolve().parent.parent.parent / 'logs'
        directory.mkdir(exist_ok=True)  # Ensure directory exists
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return str(directory / f"log_{current_time}.log")

    def emit(self, record):
        """
        Overwrite the emit method to check the condition before logging.
        """
        if self.check_condition(record):
            self.rotate_log()
        logging.FileHandler.emit(self, record)

    @staticmethod
    def check_condition(record):
        """
        Define your condition here. This function should return True when the log file needs to be rotated.
        """
        # Example condition: rotate the file if a specific error is logged
        if record.levelname == 'INFO' and 'GameOver' in record.getMessage():
            return True
        return False

    def rotate_log(self):
        self.close()
        new_filename = self.baseFilePath.with_name(self.namer())
        self.baseFilePath.rename(new_filename)
        if not self.delay:
            self.stream = self._open()

    @staticmethod
    def namer():
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return f"log_{current_time}.log"


def setup_logging():
    handler = ConditionBasedFileHandler()  # Initial log file name, will be renamed upon condition
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger('flask_app')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
