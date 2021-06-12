encoding="UTF-8"

import numpy as np
import pyautogui
import cv2
import time
from datetime import date
import config
import logManager
import random

def main():
    logManager.cmsLogger('Запущен модуль валидации экранов')
    # Запись статуса вхождения пользователя
    d = date.today()
    userStateFile = open('{}userState.txt'.format(config.tempPath, str(d)), 'w')
    userStateFile.write('1')
    userStateFile.close()
    chanelSumArr = []

    if config.screenNum == 1:
        while True:
            while len(chanelSumArr) < 2 :
                # Функциональная часть снимка экрана и подсчета интнсивности каналов
                screenShot = pyautogui.screenshot(region=(config.regiondict[0])) # Снимок экрана
                chanelIntens = cv2.cvtColor(np.array(screenShot), cv2.COLOR_RGB2BGR)      # передача изображения на анализ каналов
                commonIntens = chanelIntens.sum(axis=2)                                 # посмотреть что делает эта строка
                chanelSum = np.sum(commonIntens)                               # Сумма интенсивности по каналам
                if len(chanelSumArr) < 2 :
                    chanelSumArr.append(chanelSum)
            # Часть проверок значений, записи состояний
            if len(chanelSumArr) == 2:
                f = open('{}screenState.txt'.format(config.tempPath), 'w') # Пишу состояние экрана
                if (chanelSumArr[0] == chanelSumArr[1]):
                    f.write('1')
                else:
                    f.write('0')
                f.close()
                del chanelSumArr[0] # Удаляю из словаря запись с индексом 0

            time.sleep(random.randint(30, 90))
    else:
        pass









    # if config.screen_num == 2:
    #
    #     while True:
    #         a = 0
    #         while a < config.screen_num:
    #             image = pyautogui.screenshot(region=(config.regiondict[a]))
    #             img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #             x+=1
    #             intensity = img.sum(axis=2)
    #             chanelsum = np.sum(intensity)
    #             if a == 0:
    #                 chanel_sum_1.append(chanelsum)
    #             if a == 1:
    #                 chanel_sum_2.append(chanelsum)
    #             a += 1
    #
    #         if b == 1:
    #             f = open('{}screenState.txt'.format(config.tempPath), 'w')
    #
    #             if (chanel_sum_1[0] == chanel_sum_1[1]) and (chanel_sum_2[0] == chanel_sum_2[1]):
    #                 f.write('1')
    #             else:
    #                 f.write('0')
    #             f.close()
    #             del chanel_sum_1[0]
    #             del chanel_sum_2[0]
    #         if b == 0:
    #             b = 1
    #
    #         time.sleep(66)



if __name__ == '__main__':
    main()