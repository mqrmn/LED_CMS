# v.1.1.1

from App.Config import Config
from App import Validation
import threading
import queue
import logging
import time
from App import Config
from App import Var
import numpy as np
import pyautogui
import cv2
import random
from App.Config import Config


ScreenState = 0


def main():
    q = queue.Queue()
    Validation_ = Validation.System()

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    ScreenValidationTread = threading.Thread(target=Validation_.ScreenValidation, args=(q, ))

    logging.info("Main    : before running thread")
    ScreenValidationTread.start()
    logging.info("Main    : wait for the thread to finish")
    #ScreenValidationTread.join()
    logging.info("Main    : all done")

    while True:
        print('parent', q.get())
        time.sleep(10)



if __name__ == '__main__':
    main()