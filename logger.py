import logging
import os


class Logger:
    _logger_instance = None

    # default path for logs.
    log_folder = 'logs'

    @classmethod
    def get_logger(cls):
        if not cls._logger_instance:
            cls._logger_instance = cls._create_logger()
        return cls._logger_instance

    @classmethod
    def _create_logger(cls):
        # create the logs folder if it doesn't exist
        if not os.path.exists(cls.log_folder):
            os.makedirs(cls.log_folder)

        logger = logging.getLogger('logger')
        logger.setLevel(logging.DEBUG)

        # separate file handlers for each log level
        info_file_handler = logging.FileHandler(os.path.join(cls.log_folder, 'info_log_file.log'))
        error_file_handler = logging.FileHandler(os.path.join(cls.log_folder, 'error_log_file.log'))
        debug_file_handler = logging.FileHandler(os.path.join(cls.log_folder, 'debug_log_file.log'))

        # set the log levels for each file handler
        info_file_handler.setLevel(logging.INFO)
        error_file_handler.setLevel(logging.ERROR)
        debug_file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # set the formatter for each file handler
        info_file_handler.setFormatter(formatter)
        error_file_handler.setFormatter(formatter)
        debug_file_handler.setFormatter(formatter)

        # file handlers to the logger
        logger.addHandler(info_file_handler)
        logger.addHandler(error_file_handler)
        logger.addHandler(debug_file_handler)

        return logger
