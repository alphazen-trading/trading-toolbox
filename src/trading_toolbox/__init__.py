from sdk.logger import print, logger


def main() -> int:
    print("Hello")
    logger.warning("Warning")
    logger.error("Error message")
    return 0
