import logging
import threading
import time
from App import Validation

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.info("Main    : before creating thread")
    val = Validation.System()

    thr = threading.Thread(target=val.ScreenValidation, args=())
    logging.info("Main    : before running thread")
    thr.start()
    logging.info("Main    : wait for the thread to finish")
    thr.join()
    logging.info("Main    : all done")