import sys

import loguru

from config import config

logger = loguru.logger


def init():
    logger.remove(0)
    logger.add(sys.stdout, format="{time} | {level} | {message}", level="TRACE")
    logger.add(open(config.log_path, "w"), format="{time} {level} {message}", level="INFO", colorize=False)
    # loguru.logger.level("TRACE")
