encoding="UTF-8"

import numpy as np
import pyautogui
import cv2
import time
from datetime import date
import config
import logManager

def main():
    logManager.cmsLogger('Запущен модуль валидации системы')

    d = date.today()
    userStateFile = open('{}userState.txt'.format(config.tempPath, str(d)), 'w')
    userStateFile.write('1')
    logManager.cmsLogger('Зарегистрировано вхождение пользователя')
    userStateFile.close()

    chanel_sum_1 = []
    chanel_sum_2 = []
    
    x, b = 0, 0

    if config.screen_num == 1:
        while True:

            userStateFile = open('{}userState.txt'.format(config.tempPath, str(d)), 'r')
            userState = userStateFile.read()
            userStateFile.close()
            if userState == '0':
                userStateFile = open('{}userState.txt'.format(config.tempPath, str(d)), 'w')
                userStateFile.write('1')
                logManager.cmsLogger('Зарегистрировано вхождение пользователя')
                userStateFile.close()
            else:
                pass

            a = 0
            while a < config.screen_num:
                image = pyautogui.screenshot(region=(config.regiondict[a]))
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                x += 1
                intensity = img.sum(axis=2)
                chanelsum = np.sum(intensity)
                if a == 0:
                    chanel_sum_1.append(chanelsum)
                a += 1

            if b == 1:
                f = open('{}screenState.txt'.format(config.tempPath), 'w')
                if (chanel_sum_1[0] == chanel_sum_1[1]):
                    f.write('1')
                else:
                    f.write('0')
                f.close()
                del chanel_sum_1[0]
            if b == 0:
                b = 1

            time.sleep(66)

    if config.screen_num == 2:

        while True:
            a = 0
            while a < config.screen_num:
                image = pyautogui.screenshot(region=(config.regiondict[a]))
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                x+=1
                intensity = img.sum(axis=2)
                chanelsum = np.sum(intensity)
                if a == 0:
                    chanel_sum_1.append(chanelsum)
                if a == 1:
                    chanel_sum_2.append(chanelsum)
                a += 1

            if b == 1:
                f = open('{}screenState.txt'.format(config.tempPath), 'w')

                if (chanel_sum_1[0] == chanel_sum_1[1]) and (chanel_sum_2[0] == chanel_sum_2[1]):
                    f.write('1')
                else:
                    f.write('0')
                f.close()
                del chanel_sum_1[0]
                del chanel_sum_2[0]
            if b == 0:
                b = 1

            time.sleep(66)



if __name__ == '__main__':
    main()