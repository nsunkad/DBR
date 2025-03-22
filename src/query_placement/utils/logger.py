import logging


class Logger(logging.Logger):
    """
    Implements a custom logger which prints date and time with messages
    """

    def __init__(
        self,
        level=logging.INFO,
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ):
        super().__init__(__name__, level)

        # Set the logging format
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        # Add handler to logger
        self.addHandler(handler)
