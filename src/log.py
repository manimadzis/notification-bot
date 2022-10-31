import sys

import loguru

from config import config

logger = loguru.logger


def init(log_level: str):
    logger.remove(0)
    logger.add(sys.stdout, format="{time} | {level} | {message}", level=log_level)
    logger.add(open(config.log_path, "w"), format="{time} {level} {message}", level=log_level, colorize=False)
    # loguru.logger.level("TRACE")
