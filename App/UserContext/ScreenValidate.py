#v.1.1.0

import numpy as np
import pyautogui
import cv2
import time
from datetime import date
from App.Config import Config
from App import LogManager
import random
import os

logging = LogManager.LogManager()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

def main():
    # Запись статуса вхождения пользователя
    d = date.today()
    userStateFile = open('{}userState.txt'.format(Config.tempPath, str(d)), 'w')
    userStateFile.write('1')
    userStateFile.close()
    chanelSumArr = []

    if Config.screenNum == 1:  # По количеству областей будет допиливться
        while True:
            while len(chanelSumArr) < 2 :
                # Функциональная часть снимка экрана и подсчета интнсивности каналов
                screenShot = pyautogui.screenshot(region=(Config.regiondict[0])) # Снимок экрана
                chanelIntens = cv2.cvtColor(np.array(screenShot), cv2.COLOR_RGB2BGR)      # передача изображения на анализ каналов
                commonIntens = chanelIntens.sum(axis=2)                                 # посмотреть что делает эта строка
                chanelSum = np.sum(commonIntens)                               # Сумма интенсивности по каналам
                if len(chanelSumArr) < 2 :
                    chanelSumArr.append(chanelSum)
            # Часть проверок значений, записи состояний
            if len(chanelSumArr) == 2:
                f = open('{}screenState.txt'.format(Config.tempPath), 'w') # Пишу состояние экрана
                if (chanelSumArr[0] == chanelSumArr[1]):
                    f.write('1')
                else:
                    f.write('0')
                f.close()
                del chanelSumArr[0] # Удаляю из словаря запись с индексом 0

            time.sleep(random.randint(30, 90))
    else:
        pass

if __name__ == '__main__':
    main()