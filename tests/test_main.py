from sdk.logger import print, logger
import os


def test_main():
    # os.remove("./logs/logs.log")
    # print("Hello")
    logger.warning("Warning")
    logger.error("Error message")

    a = 4
    assert a == 4
