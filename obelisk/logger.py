import sys

from loguru import logger


def extra_formatter(record):
    compact = ",".join(f"{key}={value}" for key, value in record["extra"].items())
    record["extra"]["compact"] = compact + " " if compact else ""


logger.configure(patcher=extra_formatter)
logger.remove()
logger.add(sys.stderr, format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> <yellow>{extra[compact]}</yellow>- <level>{message}</level>')