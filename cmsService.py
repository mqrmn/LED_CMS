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
import validateNova
import renewCms
import logManager



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


        userNotLoggedInCount, userLoggedIn, scrFreezCount, scrNotRunCount, isNovaRun, isScrRun = 0, 0, 0, 0, 0, '0'
        d = date.today()
        lastShutDown = 1

        logManager.cmsLogger('Служба CMS запущена')

        # Запуск задачи по обновлению контента
        try:
            contentRefresh.run()
        except:
            logManager.cmsLogger('Возникла ошибка в модуле contentRefresh')

        # Запускает задачу по обновлению модулей
        try:
            renewCms.CMSRenew()
        except:
            logManager.cmsLogger('Возникла ошибка в модуле renewerCms')

        # Считывает состояние последнего отключения
        try:
            f = open('{}lastShutDown.txt'.format(config.tempPath), 'r')
            lastShutDown = f.read()
            logManager.cmsLogger('lastShutDown = {}'.format(lastShutDown))
            f.close()
        except:
            pass

        # При некорректном состоянии отправляет e-mail
        if lastShutDown == '0':
            try:
                sendMail.sendmail('{} предыдущее отключение было выполнено некорректно'.format(time.ctime()))
            except:
                pass

        # Удаляет старые временные файлы
        for tempFile in os.listdir(config.tempPath):
            try:
                os.remove('{}{}'.format(config.tempPath, tempFile))
            except:
                pass

        # Обнуляет код сотояния последнего отключения
        try:
            f = open('{}lastShutDown.txt'.format(config.tempPath), 'w')
            f.write('0')
            f.close()
        except:
            pass

        # Обнуляет код сотояния входа пользователя
        try:
            f = open('{}userState.txt'.format(config.tempPath, str(d)), 'w')
            f.write('0')
            f.close()
        except:
            f.close()
            pass

        # Обнуляет код сотояния экрнана
        try:
            f = open('{}screenState.txt'.format(config.tempPath), 'w')
            f.write('2')
            f.close()
        except:
            f.close()
            pass

        # Запускает основной цикл
        while True:


            if (isScrRun == '0') and (userLoggedIn != 1):
                logManager.cmsLogger('Проверка вхождения пользователя')
                f = open('{}userState.txt'.format(config.tempPath, str(d)), 'r')
                userState = f.read()
                f.close()

                userNotLoggedInCount += 1

                # Отключен основной функционал
                if userNotLoggedInCount > 30:
                    try:
                        sendMail.sendmail('{} пользователь не вошел в систему. Система будет перезагружена.'.format(time.ctime()))
                    except:
                        pass
                    logManager.cmsLogger('Пользователь не вошел в систему')
                    logManager.cmsLogger('ППерезагрузка системы в связи с отсутсвим вхождения пользователя')

                    try:
                        f = open('{}lastShutDown.txt'.format(config.tempPath, 'w'))
                        f.write('1')
                        f.close()
                    except:
                        pass
                    #shutDown.reboot()

                if (userState == '1'):
                    logManager.cmsLogger('Пользователь вошел в систему')
                    userNotLoggedInCount = 0
                    userLoggedIn = 1

            else:
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
                            try:
                                sendMail.sendmail('{} не запущена проверка экрана'.format(time.ctime()))
                            except:
                                pass
                            logManager.cmsLogger('Не запущена проверка экрана')

                            scrNotRunCount = 0
                    else:
                        scrFreezCount += 1
                        if scrFreezCount >= 45:
                            try:
                                sendMail.sendmail('{} экран не обновлялся продолжительное время'.format(time.ctime()))
                            except:
                                pass
                            logManager.cmsLogger('Экран не обновлялся продолжительное время')
                            scrFreezCount = 0

                else:
                    pass
            if isNovaRun == 0:
                try:
                    isNovaRun = validateNova.run()
                except:
                    logManager.cmsLogger('Возникла ошибка в модуле validateNova')
                if isNovaRun == 1:
                    logManager.cmsLogger('NovaStar запущен')
                else:
                    logManager.cmsLogger('NovaStar не запущен')

            # Таймаут до следующей итерации цикла
            time.sleep(10)







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