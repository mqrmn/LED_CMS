encoding="UTF-8"

import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
from datetime import date
import sendMail
import config
import contentRefresh
from userConext import validateNova
import logManager
import systemInit



class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "CMS"
    _svc_display_name_ = "CMS"
    _svc_description_ = "Обслуживает систему трансляции контента"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.hWaitResume = win32event.CreateEvent(None, 0, 0, None)
        self.timeout = 10000
        self.resumeTimeout = 1000
        self._paused = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_, ''))

    def SvcPause(self):
        self.ReportServiceStatus(win32service.SERVICE_PAUSE_PENDING)
        self._paused = True
        self.ReportServiceStatus(win32service.SERVICE_PAUSED)
        servicemanager.LogInfoMsg("The %s service has paused." % (self._svc_name_,))

    def SvcContinue(self):
        self.ReportServiceStatus(win32service.SERVICE_CONTINUE_PENDING)
        win32event.SetEvent(self.hWaitResume)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogInfoMsg("The %s service has resumed." % (self._svc_name_,))

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()



    def main(self):

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)


        # количество итераций цикла с отсутсвием вхождения пользователя
        userNotLoggedInCount = 0
        # Статус вхождния пользователя
        userLoggedIn = 0
        # количество итераций цикла с отсутсвием движения экрана
        scrFreezCount = 0
        # количество итераций цикла с отсутсвием запуска валидатора
        scrNotRunCount = 0
        # Статус запуска плеера
        isNovaRun = 0
        # Статус запуска валидатора экрана
        isScrRun = '0'

        d = date.today()

        # Блок действий при запуске системы
        #----------------------------------------------------

        # Создаю экземпляр класса инициализационных процессов
        systemInitOnRun = systemInit.onRun()

        # Проверка состояния последнего отключения
        systemInitOnRun.lastShutdownValidation()

        # Запускает задачу по обновлению модулей
        systemInitOnRun.cmsRenew()

        # Запуск задачи по обновлению контента
        contentRefresh.run()

        # Удаляет старые временные файлы
        systemInitOnRun.fileCleaner()

        # Обнуляет код сотояния последнего отключения
        systemInitOnRun.defaultStatusCode()

        # ----------------------------------------------------

        # Запускает основной цикл
        while True:

            # Если позователь не вошел в систему
            if (isScrRun == '0') and (userLoggedIn != 1):
                logManager.cmsLogger('Проверка вхождения пользователя')
                # Считываю статус проверки пользователя
                f = open('{}userState.txt'.format(config.tempPath, str(d)), 'r')
                userState = f.read()
                f.close()
                # Счетчик проверок
                userNotLoggedInCount += 1
                # Если пользователь не вошел после 30 проверок
                if userNotLoggedInCount > 30:
#                    sendMail.sendmail('{} пользователь не вошел в систему. Система будет перезагружена.'.format(time.ctime()))
                    logManager.cmsLogger('Пользователь не вошел в систему')
                    # Сброс счетчика
                    userNotLoggedInCount = 0

                if (userState == '1'):
                    logManager.cmsLogger('Пользователь вошел в систему')
                    # Сброс счетчика, регистрация статуса
                    userNotLoggedInCount = 0
                    userLoggedIn = 1


            else:
                # Проверяет состояние экрана
                isStateFile = os.path.exists('{}screenState.txt'.format(config.tempPath))
                if isStateFile == True:
                    f = open('{}screenState.txt'.format(config.tempPath), 'r')
                    screenState = f.read()
                    f.close()
                    if screenState == '0':
                        scrFreezCount = 0
                    if screenState == '2':
                        scrNotRunCount += 1
                        if scrNotRunCount >= 40:
                            sendMail.sendmail('{} не запущена проверка экрана'.format(time.ctime()))

                            logManager.cmsLogger('Не запущена проверка экрана')

                            scrNotRunCount = 0
                    else:
                        scrFreezCount += 1
                        if scrFreezCount >= 45:
                            sendMail.sendmail('{} экран не обновлялся продолжительное время'.format(time.ctime()))
                            logManager.cmsLogger('Экран не обновлялся продолжительное время')
                            scrFreezCount = 0

                else:
                    pass
            if isNovaRun == 0:
                isNovaRun = validateNova.run()
                logManager.cmsLogger('Возникла ошибка в модуле validateNova')
                if isNovaRun == 1:
                    logManager.cmsLogger('NovaStar запущен')
                else:
                    logManager.cmsLogger('NovaStar не запущен')

            # Таймаут до следующей итерации цикла
            time.sleep(10)

# Граница цикла
#----------------------------------------------------------------------


            # Проверяем не поступила ли команда завершения работы службы
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                # Здесь выполняем необходимые действия при остановке службы
                servicemanager.LogInfoMsg("Service finished")
                break

            # Здесь выполняем необходимые действия при приостановке службы
            if self._paused:
                servicemanager.LogInfoMsg("Service paused")
            # Приостановка работы службы
            while self._paused:
                # Проверям не поступила ли команда возобновления работы службы
                rc = win32event.WaitForSingleObject(self.hWaitResume, self.resumeTimeout)
                if rc == win32event.WAIT_OBJECT_0:
                    self._paused = False
                    # Здесь выполняем необходимые действия при возобновлении работы службы
                    servicemanager.LogInfoMsg("Service continue")
                    break

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)