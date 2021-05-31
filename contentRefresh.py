encoding="UTF-8"

import xml.etree.ElementTree as ET
import os
import psutil
import shutil
import config
import logManager

def create_plym(file_path_arr, file_name_arr):


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
    Window = ET.SubElement(Page, 'Window', Name=config.objType, X="0", Y="0", Width="320", Height="120", Tag="Common")
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
        string_5 = ET.SubElement(BorderUnitData, 'string').text = '''424d960000000000000036000000280000002000000001000000010018000000000000000000202e0000202e00000000000000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ffff00ffff00ffff00ffff00ffff00ffff00ffff00ffff'''
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

def prettify(element, ident='   '):
    queue = [(0, element)]
    while queue:
        level, element = queue.pop(0)
        children = [(level + 1, child) for child in list(element)]
        if children:
            element.text = '\n' + ident * (level+1)
        if queue:
            element.tail = '\n' + ident * queue[0][0]
        else:
            element.tail = '\n' + ident * (level-1)
        queue[0:0] = children


def generate():


    for formatPath in config.screenFormat:

        allFilePathList = []
        allFileNameList = []

        print(formatPath)

        localListFilesUnex = os.listdir(config.localFilesUnex + formatPath)
        localListFilesEx = os.listdir(config.localFilesEx + formatPath)


        for file in localListFilesUnex:
            print(file)
            allFilePathList.append(config.localFilesUnex + formatPath + '\\' + file)
            allFileNameList.append(file)

        for file in localListFilesEx:
            print(file)
            allFilePathList.append(config.localFilesEx + formatPath + '\\' + file)
            allFileNameList.append(file)


        PlayProgram = create_plym(allFilePathList, allFileNameList)
        prettify(PlayProgram)
        tree = ET.ElementTree(PlayProgram)
        tree.write('{}{}_playerConfig.plym'.format(config.configTargetPath, formatPath), encoding='UTF-8', xml_declaration=True)
        logManager.cmsLogger('Файл плелиста успешно сгенерирован: {}_playerConfig.plym'.format(formatPath))



# Проверяет обновление контента и обновляет файлы
def RefreshContent():

    refreshStatus = 0

    for formatPath in config.screenFormat:

        yaListFilesExcept = os.listdir(config.yaFilesExcept + formatPath)
        yaListFilesUnex = os.listdir(config.yaFilesUnex + formatPath)
        yaListFilesEx = os.listdir(config.yaFilesEx + formatPath)
        localListFilesUnex = os.listdir(config.localFilesUnex + formatPath)
        localListFilesEx = os.listdir(config.localFilesEx + formatPath)

        if yaListFilesExcept:

            for file in yaListFilesExcept:

                if file in localListFilesUnex:
                    logManager.cmsLogger('Удаление файла {}{}{}{} по исключению'.format(config.localFilesUnex, formatPath, '\\', file))

                    os.remove(config.localFilesUnex + formatPath + '\\' + file)
                    refreshStatus = 1



        if yaListFilesUnex != localListFilesUnex:

            for file in yaListFilesUnex:

                if file not in yaListFilesExcept:
                    if file not in localListFilesUnex:
                        logManager.cmsLogger('Обновление общего контента: Добавление файла {}{}{}'.format(config.yaFilesUnex, formatPath, file))

                        shutil.copy(config.yaFilesUnex + formatPath + '\\' + file, config.localFilesUnex + formatPath)
                        refreshStatus = 1
            for file in localListFilesUnex:

                if file not in yaListFilesUnex:
                    logManager.cmsLogger('Обновление общего контента: Удаление файла {}{}{}'.format(config.localFilesUnex, formatPath, file))

                    os.remove(config.localFilesUnex + formatPath + '\\' + file)
                    refreshStatus = 1
        if yaListFilesEx != localListFilesEx:
            logManager.cmsLogger('Обновление уникального контента')

            for file in yaListFilesEx:
                if file not in localListFilesEx:
                    logManager.cmsLogger('Обновление уникального контента: Добавление файла {}{}{}'.format(config.yaFilesEx, formatPath, file))

                    shutil.copy(config.yaFilesEx + formatPath + '\\' + file, config.localFilesEx + formatPath)
                    refreshStatus = 1
            for file in localListFilesEx:

                if file not in yaListFilesEx:
                    logManager.cmsLogger('ООбновление уникального контента: Удаление файла {}{}{}'.format(config.yaFilesEx, formatPath, file))

                    os.remove(config.localFilesEx + formatPath + '\\' + file)
                    refreshStatus = 1
        if refreshStatus == 0:
            logManager.cmsLogger('Нет заданий на обновление контента')

    return refreshStatus

def run():


    for proc in psutil.process_iter():
        processName = proc.as_dict(attrs=['name'])
        if processName['name'] == 'NovaStudio.exe':
            isNova = 1
            break
        else:
            isNova = 0


    if isNova == 0:
        logManager.cmsLogger('NovaStudio.exe не запущен. Проверка наличия обновленного контента')
        refreshStatus = RefreshContent()
        if refreshStatus == 1:
            generate()
        else:
            logManager.cmsLogger('Файлов для обновления плейлиста не обнаружено')

    else:
        logManager.cmsLogger('{} запущен. Обновление плейлиста отменено'.format(processName['name']))

logManager.cmsLogger('lastShutdownValidation 0 ?')