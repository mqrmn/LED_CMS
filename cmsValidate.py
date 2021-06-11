encoding="UTF-8"

import numpy as np
import pyautogui
import cv2
import time
from datetime import date
import config
import logManager

def main():
    logManager.cmsLogger('Запущен модуль валидации экранов')


    # Запись статуса вхождения пользователя
    d = date.today()
    userStateFile = open('{}userState.txt'.format(config.tempPath, str(d)), 'w')
    userStateFile.write('1')
    userStateFile.close()


    # chanel_sum_1 = []
    chanelIntencArr = []
    # chanel_sum_2 = []

    if config.screenNum == 1:
        while True:
            while len(chanelIntencArr) < 2 :
                # Функциональная часть снимка экрана и подсчета интнсивности каналов
                image = pyautogui.screenshot(region=(config.regiondict[0])) # Снимок экрана
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)      # передача изображения на анализ каналов
                intensity = img.sum(axis=2)                                 # посмотреть что делает эта строка
                chanelsum = np.sum(intensity)                               # Сумма интенсивности по каналам

                if len(chanelIntencArr) < 2 :
                    chanelIntencArr.append(chanelsum)

            # Часть проверок значений, записи состояний
            if len(chanelIntencArr) == 2:
                f = open('{}screenState.txt'.format(config.tempPath), 'w') # Пишу состояние экрана
                if (chanelIntencArr[0] == chanelIntencArr[1]):
                    f.write('1')
                else:
                    f.write('0')
                f.close()
                del chanelIntencArr[0] # Удаляю из словаря запись с индексом 0

            time.sleep(43)
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