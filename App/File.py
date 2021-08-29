# 1.1.1

import sys
import os
import xml.etree.ElementTree as ET
import time
import shutil
import pythoncom
import datetime
import re
from inspect import currentframe, getframeinfo
sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Resource, Log, API, Act, Database

LOG = Log.Log_Manager()

class CMSUpdate:

    def CMSUpdater(self, Q_FromUpdater, q_internal):

        o_createMessage = Resource.CreateMessage()
        q_internal.put(o_createMessage.SendMail('Тест отправки уведомлений из контроллера'))
        C_API = API.Service()
        C_Action = Act.System()
        pythoncom.CoInitialize()
        while True:
            if self.CMSUpgrade(False) == True:
                LOG.CMSLogger('Update detected')
                time.sleep(180)
                stSvc = C_API.StopService('CMS')
                if stSvc[0] == 0:
                    Q_FromUpdater.put(True)
                    LOG.CMSLogger( 'CMS stopped')
                    time.sleep(30)
                    self.CMSUpgrade(True)
                    table = Database.Tables()
                    table.SelfInitShutdown.create(trigger=getframeinfo(currentframe())[2],
                                                  key='reboot',
                                                  datetime=datetime.datetime.now(), )

                    C_Action.RebootInit()
                    q_internal.put(o_createMessage.SendMail('Выполнено обновление CMS'))


                else:
                    LOG.CMSLogger('Cant stop CMS, code: {}'.format(stSvc), )
            else:
                time.sleep(1800)

    def CMSUpgrade(self, key):

        priorities = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0}
        versions = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0, 'CURRENT': 0}

        if Config.upgradePolitic == 1:
            # Reading the current version
            if os.path.exists(os.path.dirname(__file__) + '\\PACKAGE.ver'):
                file = open(os.path.dirname(__file__) + '\\PACKAGE.ver', 'r')
                currentV = file.read()
                file.close()
                versions['CURRENT'] = currentV

            priorities['GLOBAL'], versions['GLOBAL'] = self.CheckCMSUpdates(Config.globalCmsRenew, 'GLOBAL')
            priorities['GROUP'], versions['GROUP'] = self.CheckCMSUpdates(Config.groupCmsRenew, 'GROUP')
            priorities['LOCAL'], versions['LOCAL'] = self.CheckCMSUpdates(Config.localCmsRenew, 'LOCAL')

            maxPriority = sorted(priorities, key=priorities.__getitem__)[-1]
            LOG.CMSLogger('The priority of the update catalog has been determined: ' + maxPriority)

            if priorities[maxPriority] > 200:
                currentVArr = versions['CURRENT'].split('.')
                newtVArr = versions[maxPriority].split('.')

                # Version comparison
                stopCheck = 0
                if currentVArr[0] == newtVArr[0]:
                    if currentVArr[1] == newtVArr[1]:
                        if currentVArr[2] == newtVArr[2]:
                            LOG.CMSLogger('No updates found')
                        elif int(currentVArr[2]) < int(newtVArr[2]):
                            LOG.CMSLogger('Update detected ' + versions[maxPriority])
                            if key == True:
                                self.CurrentCMSArch(currentV)
                                self.RenewCMSFiles(Config.globalCmsRenew)
                            else:
                                return True
                            stopCheck = 1
                    elif int(currentVArr[1]) < int(newtVArr[1]) and stopCheck != 1:
                        if key == True:
                            LOG.CMSLogger('ОUpdate detected ' + versions[maxPriority])
                            self.CurrentCMSArch(currentV)
                            self.RenewCMSFiles(Config.groupCmsRenew)
                        else:
                            return True
                elif int(currentVArr[0]) < int(newtVArr[0]) and stopCheck != 1:
                    if key == True:
                        LOG.CMSLogger('Update detected ' + versions[maxPriority])
                        self.CurrentCMSArch(currentV)
                        self.RenewCMSFiles(Config.globalCmsRenew)
                    else:
                        return True
            else:
                LOG.CMSLogger('The priority is insufficient. Cancel update.')
        else:
            pass
        # Checks CMS update keys

    def CheckCMSUpdates(self, path, type):

        upgradeScoreKey = {'IGNORE': 0, 'FREE': 200, 'FORCE': 300, 'LOCK': 400}
        upgradeScoreType = {'GLOBAL': 30, 'GROUP': 20, 'LOCAL': 10}
        upgradeScoreTypeLoc = {'GLOBAL': 10, 'GROUP': 20, 'LOCAL': 30}

        if os.path.exists(path + 'PACKAGE.ver'):
            file = open(path + 'PACKAGE.ver', 'r')
            version = file.read()
            file.close()

            file = open(path + 'UPGRADE.key', 'r')
            key = file.read()
            file.close()

            score = upgradeScoreKey[key]
            if key == 'LOCK':
                score += upgradeScoreTypeLoc[type]
            else:
                score += upgradeScoreType[type]
        else:
            score, version = 0, '0.0.0'
        return score, version

        # Archives the current CMS package

    def CurrentCMSArch(self, version):

        if not os.path.exists(Config.CMSArchPath + str(version)):
            shutil.copytree(os.getcwd(), Config.CMSArchPath + str(version))
            LOG.CMSLogger('The current package is archived')

        # Updates CMS files directly

    def RenewCMSFiles(self, path):
        # shutil.rmtree(os.path.dirname(__file__))
        # shutil.copytree(path, os.path.dirname(__file__))

        LOG.CMSLogger('Update completed')

class RenewContent:
    def CheckNewContent(self):
        x = 0
        for formatPath in Config.screenFormat:
            yaListFilesExcept = os.listdir(Config.yaFilesExcept + formatPath)
            yaListFilesUnex = os.listdir(Config.yaFilesUnex + formatPath)
            yaListFilesEx = os.listdir(Config.yaFilesEx + formatPath)
            localListFilesUnex = os.listdir(Config.localFilesUnex + formatPath)
            localListFilesEx = os.listdir(Config.localFilesEx + formatPath)

            for file in yaListFilesExcept:
                if file in localListFilesUnex:
                    x = 1
                    break
                else:
                    pass

            for file in localListFilesUnex:
                if file in yaListFilesExcept:
                    x = 1
                    break
                else:
                    pass

            if localListFilesUnex == yaListFilesUnex:
                pass
            else:
                c1 = yaListFilesUnex
                c2 = localListFilesUnex
                for file in list(set(c1) - set(c2)):
                    if file not in yaListFilesExcept:
                        x = 1
                c1 = yaListFilesUnex
                c2 = localListFilesUnex
                if list(set(c2) - set(c1)):
                    x = 1

            if localListFilesEx == yaListFilesEx:
                pass
            else:
                x = 1

            if x == 1:
                return [yaListFilesExcept, yaListFilesUnex, yaListFilesEx, ]
            else:
                return None

    def DynamicRenewCont(self, Q_out):

        list = None
        fix = False
        countPass = 0
        while True:
            x = self.CheckNewContent()
            if x != list:
                list = x
                fix = True
                countPass = 0

            if fix == True:
                countPass += 1
            if countPass >= 5:
                self.ContentRenewHandle(Q_out, )
                list = None
                fix = False
                countPass = 0
            time.sleep(10)

    def ContentRenewHandle(self, Q_out, ):

        appendStatus = self.AppendContent()
        Q_out.put(Resource.TerminateNova[0])
        time.sleep(5)
        removeStatus = self.RemoveContent()
        if (appendStatus == True) or (removeStatus == True):
            self.Generate()
        Q_out.put(Resource.RunNova[1])

    def AppendContent(self):

        refreshStatus = False

        for formatPath in Config.screenFormat:
            yaListFilesExcept = os.listdir(Config.yaFilesExcept + formatPath)
            yaListFilesUnex = os.listdir(Config.yaFilesUnex + formatPath)
            yaListFilesEx = os.listdir(Config.yaFilesEx + formatPath)
            localListFilesUnex = os.listdir(Config.localFilesUnex + formatPath)
            localListFilesEx = os.listdir(Config.localFilesEx + formatPath)
            if yaListFilesUnex != localListFilesUnex:
                for file in yaListFilesUnex:
                    if file not in yaListFilesExcept:
                        if file not in localListFilesUnex:
                            shutil.copy(Config.yaFilesUnex + formatPath + '\\' + file,
                                        Config.localFilesUnex + formatPath)
                            LOG.CMSLogger('File added: ' + Config.yaFilesUnex + formatPath + '\\' + file)
                            refreshStatus = True

            if yaListFilesEx != localListFilesEx:
                for file in yaListFilesEx:
                    if file not in localListFilesEx:
                        shutil.copy(Config.yaFilesEx + formatPath + '\\' + file, Config.localFilesEx + formatPath)
                        LOG.CMSLogger('File added: ' + Config.yaFilesEx + formatPath + '\\' + file)
                        refreshStatus = True

        return refreshStatus

    def RemoveContent(self):

        refreshStatus = False

        for formatPath in Config.screenFormat:
            yaListFilesExcept = os.listdir(Config.yaFilesExcept + formatPath)
            yaListFilesUnex = os.listdir(Config.yaFilesUnex + formatPath)
            yaListFilesEx = os.listdir(Config.yaFilesEx + formatPath)
            localListFilesUnex = os.listdir(Config.localFilesUnex + formatPath)
            localListFilesEx = os.listdir(Config.localFilesEx + formatPath)

            for file in yaListFilesExcept:
                if file in localListFilesUnex:
                    os.remove(Config.localFilesUnex + formatPath + '\\' + file)
                    LOG.CMSLogger('File deleted by exception: ' + Config.localFilesUnex + formatPath + '\\' + file)
                    refreshStatus = True

            if yaListFilesUnex != localListFilesUnex:
                for file in localListFilesUnex:
                    if file not in yaListFilesUnex:
                        os.remove(Config.localFilesUnex + formatPath + '\\' + file)
                        LOG.CMSLogger('File deleted: ' + Config.localFilesUnex + formatPath + '\\' + file)
                        refreshStatus = True
            if yaListFilesEx != localListFilesEx:
                for file in localListFilesEx:
                    if file not in yaListFilesEx:
                        os.remove(Config.localFilesEx + formatPath + '\\' + file)
                        LOG.CMSLogger('File deleted: ' + Config.localFilesEx + formatPath + '\\' + file)
                        refreshStatus = True
        return refreshStatus

    def Generate(self):

        for formatPath in Config.screenFormat:

            allFilePathList = []
            allFileNameList = []

            localListFilesUnex = os.listdir(Config.localFilesUnex + formatPath)
            localListFilesEx = os.listdir(Config.localFilesEx + formatPath)

            for file in localListFilesUnex:
                allFilePathList.append(Config.localFilesUnex + formatPath + '\\' + file)
                LOG.CMSLogger('The file is included in the playlist: ' + Config.localFilesUnex + formatPath + '\\' + file)
                allFileNameList.append(file)

            for file in localListFilesEx:
                allFilePathList.append(Config.localFilesEx + formatPath + '\\' + file)
                LOG.CMSLogger('ФThe file is included in the playlist: ' + Config.localFilesEx + formatPath + '\\' + file)
                allFileNameList.append(file)

            PlayProgram = self.CreateXML(allFilePathList, allFileNameList)
            self.Prettify(PlayProgram)
            tree = ET.ElementTree(PlayProgram)
            tree.write('{}{}_playerConfig.plym'.format(Config.configTargetPath, formatPath), encoding='UTF-8',
                       xml_declaration=True)
        LOG.CMSLogger('Playlist generated: ' + '{}{}_playerConfig.plym'.format(Config.configTargetPath, formatPath))

    def CreateXML(self, file_path_arr, file_name_arr):

        x = 0
        PlayProgram = ET.Element('PlayProgram', X="0", Y="0", Width="320", Height="120")
        Playlist = ET.SubElement(PlayProgram, 'Playlist', Type="TimeSegment", Name="General Segment1", Date="",
                                 Day="True#True#True#True#True#True#True", Time="", IsSpeficTimeZone="False",
                                 DiffToUTC="00:00:00", ID="0")
        Context = ET.SubElement(Playlist, 'Context')
        BasicPage = ET.SubElement(Context, 'BasicPage')
        Page = ET.SubElement(BasicPage, 'Page', Name="Program1", PlayType="Order", Duration="00:06:00", PlayTimes="1",
                             BackColor="255#0#0#0", BackgroundImage="", ImageLayout="Stretch", BackMusic="",
                             CustomString="")
        Window = ET.SubElement(Page, 'Window', Name=Config.objType, X="0", Y="0", Width="320", Height="120",
                               Tag="Common")
        for file_path in file_path_arr:
            Item = ET.SubElement(Window, 'Item', Type="0")
            Media = ET.SubElement(Item, 'Media')
            VideoMedia = ET.SubElement(Media, 'VideoMedia')
            Name = ET.SubElement(VideoMedia, 'Name').text = file_name_arr[x]
            PlayDuration = ET.SubElement(VideoMedia, 'PlayDuration')
            string = ET.SubElement(PlayDuration, 'string').text = '0#0#0#15#0'
            BeginTime = ET.SubElement(VideoMedia, 'BeginTime').text = '0001-01-01T00:00:00'
            EndTime = ET.SubElement(VideoMedia, 'EndTime').text = '0001-01-01T00:00:00'
            Times = ET.SubElement(VideoMedia, 'Times').text = '-1'
            BackColor = ET.SubElement(VideoMedia, 'BackColor')
            string_2 = ET.SubElement(BackColor, 'string').text = '255#0#0#0'
            BackImagePath = ET.SubElement(VideoMedia, 'BackImagePath')
            BackImageLayout = ET.SubElement(VideoMedia, 'BackImageLayout').text = 'Stretch'
            Opacity = ET.SubElement(VideoMedia, 'Opacity').text = '1'
            ID = ET.SubElement(VideoMedia, 'ID').text = '{}'.format(x + 1)
            EnableBorderElement = ET.SubElement(VideoMedia, 'EnableBorderElement').text = 'false'
            BorderElement = ET.SubElement(VideoMedia, 'BorderElement')
            BorderType = ET.SubElement(BorderElement, 'BorderType').text = '6'
            IsClockWise = ET.SubElement(BorderElement, 'IsClockWise').text = 'true'
            Speed = ET.SubElement(BorderElement, 'Speed').text = '5'
            BorderWidth = ET.SubElement(BorderElement, 'BorderWidth').text = '1'
            BackColor = ET.SubElement(BorderElement, 'BackColor')
            string_3 = ET.SubElement(BackColor, 'string').text = '255#0#0#0'
            ForeColor = ET.SubElement(BorderElement, 'ForeColor')
            string_4 = ET.SubElement(ForeColor, 'string').text = '255#0#128#0'
            ColorType = ET.SubElement(BorderElement, 'ColorType').text = '0'
            BorderDirectionStyle = ET.SubElement(BorderElement, 'BorderDirectionStyle').text = '0'
            BorderSurroundedType = ET.SubElement(BorderElement, 'BorderSurroundedType').text = '0'
            BorderUnitData = ET.SubElement(BorderElement, 'BorderUnitData')
            string_5 = ET.SubElement(BorderUnitData,
                                     'string').text = '''424d960000000000000036000000280000002000000001000000010018000000000000000000202e0000202e00000000000000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ffff00ffff00ffff00ffff00ffff00ffff00ffff00ffff'''
            BorderLeftUnitData = ET.SubElement(BorderElement, 'BorderLeftUnitData')
            string_6 = ET.SubElement(BorderLeftUnitData, 'string')
            BorderRightUnitData = ET.SubElement(BorderElement, 'BorderRightUnitData')
            string_7 = ET.SubElement(BorderRightUnitData, 'string')
            BorderBottomUnitData = ET.SubElement(BorderElement, 'BorderBottomUnitData')
            string_8 = ET.SubElement(BorderBottomUnitData, 'string')
            Tag = ET.SubElement(VideoMedia, 'Tag')
            FinishedMode = ET.SubElement(VideoMedia, 'FinishedMode').text = 'PlayInSpecTime'
            RotateAngle = ET.SubElement(VideoMedia, 'RotateAngle').text = 'None'
            Path = ET.SubElement(VideoMedia, 'Path').text = file_path
            DispRatioType = ET.SubElement(VideoMedia, 'DispRatioType').text = 'Full'
            TxtElement = ET.SubElement(VideoMedia, 'TxtElement')
            TextFont = ET.SubElement(TxtElement, 'TextFont')
            string_9 = ET.SubElement(TextFont, 'string').text = 'Arial#12#Regular#Point#12'
            TextColor = ET.SubElement(TxtElement, 'TextColor')
            string_10 = ET.SubElement(TextColor, 'string').text = '255#255#0#0'
            IsTextEffect = ET.SubElement(TxtElement, 'IsTextEffect').text = 'false'
            TextEffectType = ET.SubElement(TxtElement, 'TextEffectType').text = '0'
            TextEffectColor = ET.SubElement(TxtElement, 'TextEffectColor')
            string_11 = ET.SubElement(TextEffectColor, 'string').text = '255#255#255#0'
            TextEffectWidth = ET.SubElement(TxtElement, 'TextEffectWidth').text = '2'
            TextAlignment = ET.SubElement(TxtElement, 'TextAlignment').text = 'TopLeft'
            IsShowTextElement = ET.SubElement(VideoMedia, 'IsShowTextElement').text = 'false'
            VolumnPercent = ET.SubElement(VideoMedia, 'VolumnPercent').text = '0'
            RotateType = ET.SubElement(VideoMedia, 'RotateType').text = 'None'
            IsStartFromSpecificPos = ET.SubElement(VideoMedia, 'IsStartFromSpecificPos').text = 'false'
            StartPosition = ET.SubElement(VideoMedia, 'StartPosition')
            string_12 = ET.SubElement(StartPosition, 'string').text = '0#0#0#0#0'
            EndPosition = ET.SubElement(VideoMedia, 'EndPosition')
            string_13 = ET.SubElement(EndPosition, 'string').text = '0#0#0#15#0'
            AdditionalInfo = ET.SubElement(Item, 'AdditionalInfo')
            x += 1
        GlobalPage = ET.SubElement(Context, 'GlobalPage')
        Page = ET.SubElement(GlobalPage, 'Page')

        return PlayProgram

    def Prettify(self, element, ident='   '):
        queue = [(0, element)]
        while queue:
            level, element = queue.pop(0)
            children = [(level + 1, child) for child in list(element)]
            if children:
                element.text = '\n' + ident * (level + 1)
            if queue:
                element.tail = '\n' + ident * queue[0][0]
            else:
                element.tail = '\n' + ident * (level - 1)
            queue[0:0] = children

class NovaBin:

    def BackupHandle(self):
        if self.CheckNovaFile() == True:
            self.BackupNovaBin()
        else:
            LOG.CMSLogger('NovaBin backup canceled')

    def RestoreHandle(self):
        C_Nova = API.Nova()
        if self.CheckNovaFile() != True:
            if C_Nova.GetProcState(Resource.ProcList[0]) == True:
                C_Nova.TerminateNova()
            self.RestoreNovaBin()
        else:
            LOG.CMSLogger('NovaBin restore canceled')

    def CheckNovaFile(self):
        if os.path.exists(Config.novaBinFile):
            file = open(Config.novaBinFile, 'rb')
            string = file.read()
            if re.search('zh-CN', str(string)):
                return False
            else:
                return True
        else:
            return None

    def RestoreNovaBin(self):
        shutil.copy(Config.novaBinFileBak,  Config.novaBinFile)
        LOG.CMSLogger('NovaBin recovery completed')

    def BackupNovaBin(self):
        shutil.copy(Config.novaBinFile, Config.novaBinFileBak)
        LOG.CMSLogger('NovaBin has been backed up')