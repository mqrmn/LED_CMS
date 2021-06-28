#v.1.1.0
import sys
sys.path.append("C:\\MOBILE\\Local\\CMS")

import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
from App.Config import Config
from App import LogManager, Restore, Validation, FileManager
from inspect import currentframe, getframeinfo

logging = LogManager.LogManager()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])



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
        # Инициализация
        # --------------------------------------------------------------------
        # Создаю экземпляры классов
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], '0')
        Validation_ = Validation.System()
        File_Manager = FileManager.System()
        Default_ = Restore.Default()

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], '3')

        # Обновляю CMS
        File_Manager.CMSUpgrade()
        # Проверяю NovaStudio
        Validation_.NovaStudio()
        # Обновляю контент
        File_Manager.ContentRenewHandler()

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], '6')

        # Проверяю статус последнего выключения
        Validation_.LastShutdown()
        # Обнуляю временные файлы
        File_Manager.TempDeleter()
        Default_.TempFiles()

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], '9')

        # Чищу логи
        File_Manager.LogArchiever()
        File_Manager.LogDeleter()

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], '12')

        # Удаляю экземпляры классов
        Validation_ = None
        File_Manager = None
        Default_ = None

#        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], '15')


        # количество итераций цикла с отсутсвием вхождения пользователя
        userNotLoggedInCount = 0
        # Статус вхождния пользователя
        userState = '0'
        # количество итераций цикла с отсутсвием движения экрана
        scrFreezCount = 0
        # количество итераций цикла с отсутсвием запуска валидатора
        scrNotRunCount = 0

        # Цикл проверок
        # --------------------------------------------------------------------
        while True:
            # ПРОВЕРКА ВХОЖДЕНИЯ ПОЛЬЗОВАТЕЛЯ
            if userState == '0':
                f = open('{}userState.txt'.format(Config.tempPath), 'r')
                userState = f.read()
                f.close()
                userNotLoggedInCount += 1
                if userNotLoggedInCount > 30:
                    userNotLoggedInCount = 0
                if (userState == '1'):
                    userNotLoggedInCount = 0

            else:
                # Проверяет состояние экрана
                isStateFile = os.path.exists('{}screenState.txt'.format(Config.tempPath))
                if isStateFile == True:
                    f = open('{}screenState.txt'.format(Config.tempPath), 'r')
                    screenState = f.read()
                    f.close()
                    if screenState == '0':
                        scrFreezCount = 0
                    if screenState == '2':
                        scrNotRunCount += 1
                        if scrNotRunCount >= 40:
                            scrNotRunCount = 0
                    else:
                        scrFreezCount += 1
                        if scrFreezCount >= 45:
                            scrFreezCount = 0

                else:
                    pass

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