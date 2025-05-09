# 1.1.1

import sys
import os
import xml.etree.ElementTree as Et
import time
import shutil
import pythoncom
import datetime
import re
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config as Con
from App import Resource, Log, API, Act, Database
from App import Resource as Res

LOG = Log.LogManager()


class CMSUpdate:

    def cms_updater(self, q_from_updater, q_internal):

        o_create_message = Resource.CreateMessage()
        c_api = API.Service()
        c_action = Act.System()
        pythoncom.CoInitialize()
        while True:
            if self.cms_upgrade(False) is True:
                LOG.cms_logger('Update detected')
                try:
                    c_api.stop_service('CMS')
                except:
                    LOG.cms_logger(sys.exc_info()[1])

                q_from_updater.put(True)
                LOG.cms_logger('CMS stopped')
                time.sleep(Con.cms_updater_delay2)
                self.cms_upgrade(True)
                table = Database.Tables()

                try:
                    table.SelfInitShutdown.create(trigger=getframeinfo(currentframe())[2],
                                                  key='reboot',
                                                  datetime=datetime.datetime.now(), )
                except:
                    LOG.cms_logger(sys.exc_info()[1])

                c_action.reboot_init()
                q_internal.put(o_create_message.send_mail('Выполнено обновление CMS'))


            else:
                time.sleep(Con.cms_updater_delay3)

    def cms_upgrade(self, key):
        current_v = None
        priorities = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0}
        versions = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0, 'CURRENT': 0}

        if Con.upgradePolitic == 1:
            # Reading the current version
            if os.path.exists(os.path.dirname(__file__) + '\\PACKAGE.ver'):
                file = open(os.path.dirname(__file__) + '\\PACKAGE.ver', 'r')
                current_v = file.read()
                file.close()
                versions['CURRENT'] = current_v

            priorities['GLOBAL'], versions['GLOBAL'] = self.check_cms_updates(Con.globalCmsRenew, 'GLOBAL')
            priorities['GROUP'], versions['GROUP'] = self.check_cms_updates(Con.groupCmsRenew, 'GROUP')
            priorities['LOCAL'], versions['LOCAL'] = self.check_cms_updates(Con.localCmsRenew, 'LOCAL')

            max_priority = sorted(priorities, key=priorities.__getitem__)[-1]
            LOG.cms_logger('The priority of the update catalog has been determined: ' + max_priority)

            if priorities[max_priority] > 200:
                current_v_arr = versions['CURRENT'].split('.')
                newt_v_arr = versions[max_priority].split('.')

                # Version comparison
                stop_check = 0
                if current_v_arr[0] == newt_v_arr[0]:
                    if current_v_arr[1] == newt_v_arr[1]:
                        if current_v_arr[2] == newt_v_arr[2]:
                            LOG.cms_logger('No updates found')
                        elif int(current_v_arr[2]) < int(newt_v_arr[2]):
                            LOG.cms_logger('Update detected ' + versions[max_priority])
                            if key is True:
                                self.current_cms_arch(current_v)
                                self.renew_cms_files(Con.globalCmsRenew)
                            else:
                                return True
                    elif int(current_v_arr[1]) < int(newt_v_arr[1]) and stop_check != 1:
                        if key is True:
                            LOG.cms_logger('Update detected ' + versions[max_priority])
                            self.current_cms_arch(current_v)
                            self.renew_cms_files(Con.groupCmsRenew)
                        else:
                            return True
                elif int(current_v_arr[0]) < int(newt_v_arr[0]) and stop_check != 1:
                    if key is True:
                        LOG.cms_logger('Update detected ' + versions[max_priority])
                        self.current_cms_arch(current_v)
                        self.renew_cms_files(Con.globalCmsRenew)
                    else:
                        return True
            else:
                LOG.cms_logger('The priority is insufficient. Cancel update.')
        else:
            pass
        # Checks CMS update keys

    @staticmethod
    def check_cms_updates(path, type_f):

        upgrade_score_key = {'IGNORE': 0, 'FREE': 200, 'FORCE': 300, 'LOCK': 400}
        upgrade_score_type = {'GLOBAL': 30, 'GROUP': 20, 'LOCAL': 10}
        upgrade_score_type_loc = {'GLOBAL': 10, 'GROUP': 20, 'LOCAL': 30}

        if os.path.exists(path + 'PACKAGE.ver'):
            file = open(path + 'PACKAGE.ver', 'r')
            version = file.read()
            file.close()

            file = open(path + 'UPGRADE.key', 'r')
            key = file.read()
            file.close()

            score = upgrade_score_key[key]
            if key == 'LOCK':
                score += upgrade_score_type_loc[type_f]
            else:
                score += upgrade_score_type[type_f]
        else:
            score, version = 0, '0.0.0'
        return score, version

        # Archives the current CMS package

    @staticmethod
    def current_cms_arch(version):

        if not os.path.exists(Con.CMSArchPath + str(version)):
            shutil.copytree(os.getcwd(), Con.CMSArchPath + str(version))
            LOG.cms_logger('The current package is archived')

        # Updates CMS files directly

    @staticmethod
    def renew_cms_files(path):
        shutil.rmtree(os.path.dirname(__file__))
        shutil.copytree(path, os.path.dirname(__file__))

        LOG.cms_logger('Update completed')


class RenewContent:

    def dynamic_renew_cont(self, q_prepare_to_send, q_internal):
        cr_msg = Resource.CreateMessage()
        list_f = None
        fix = False
        count_pass = 0
        while True:
            x = self.check_new_content()
            if x != list_f:
                list_f = x
                fix = True
                count_pass = 0

            if fix is True:
                count_pass += 1
            if count_pass >= Con.count_pass:
                self.content_renew_handle(q_prepare_to_send, )
                q_internal.put(cr_msg.send_mail('Выполнено обновление контента'))
                list_f = None
                fix = False
                count_pass = 0
            time.sleep(Con.dynamic_renew_cont_delay)

    def content_renew_handle(self, q_prepare_to_send, ):

        append_status = self.append_content()
        a = Res.CreateMessage.command_term_nova()
        q_prepare_to_send.put(a)
        time.sleep(Con.content_renew_handle_delay)
        remove_status = self.remove_content()
        if (append_status is True) or (remove_status is True):
            self.generate()

        q_prepare_to_send.put(Res.CreateMessage.command_run_nova())

    @staticmethod
    def check_new_content():
        x = 0
        for formatPath in Con.screenFormat:
            ya_list_files_except = os.listdir(Con.yaFilesExcept + formatPath)
            ya_list_files_unex = os.listdir(Con.yaFilesUnex + formatPath)
            ya_list_files_ex = os.listdir(Con.yaFilesEx + formatPath)
            local_list_files_unex = os.listdir(Con.localFilesUnex + formatPath)
            local_list_files_ex = os.listdir(Con.localFilesEx + formatPath)

            for file in ya_list_files_except:
                if file in local_list_files_unex:
                    x = 1
                    break
                else:
                    pass

            for file in local_list_files_unex:
                if file in ya_list_files_except:
                    x = 1
                    break
                else:
                    pass

            if local_list_files_unex == ya_list_files_unex:
                pass
            else:
                c1 = ya_list_files_unex
                c2 = local_list_files_unex
                for file in list(set(c1) - set(c2)):
                    if file not in ya_list_files_except:
                        x = 1
                c1 = ya_list_files_unex
                c2 = local_list_files_unex
                if list(set(c2) - set(c1)):
                    x = 1

            if local_list_files_ex == ya_list_files_ex:
                pass
            else:
                x = 1

            if x == 1:
                return [ya_list_files_except, ya_list_files_unex, ya_list_files_ex, ]
            else:
                return None

    @staticmethod
    def append_content():

        refresh_status = False

        for formatPath in Con.screenFormat:
            ya_list_files_except = os.listdir(Con.yaFilesExcept + formatPath)
            ya_list_files_unex = os.listdir(Con.yaFilesUnex + formatPath)
            ya_list_files_ex = os.listdir(Con.yaFilesEx + formatPath)
            local_list_files_unex = os.listdir(Con.localFilesUnex + formatPath)
            local_list_files_ex = os.listdir(Con.localFilesEx + formatPath)
            if ya_list_files_unex != local_list_files_unex:
                for file in ya_list_files_unex:
                    if file not in ya_list_files_except:
                        if file not in local_list_files_unex:
                            shutil.copy(Con.yaFilesUnex + formatPath + '\\' + file,
                                        Con.localFilesUnex + formatPath)
                            LOG.cms_logger('File added: ' + Con.yaFilesUnex + formatPath + '\\' + file)
                            refresh_status = True

            if ya_list_files_ex != local_list_files_ex:
                for file in ya_list_files_ex:
                    if file not in local_list_files_ex:
                        shutil.copy(Con.yaFilesEx + formatPath + '\\' + file, Con.localFilesEx + formatPath)
                        LOG.cms_logger('File added: ' + Con.yaFilesEx + formatPath + '\\' + file)
                        refresh_status = True

        return refresh_status

    @staticmethod
    def remove_content():

        refresh_status = False

        for formatPath in Con.screenFormat:
            ya_list_files_except = os.listdir(Con.yaFilesExcept + formatPath)
            ya_list_files_unex = os.listdir(Con.yaFilesUnex + formatPath)
            ya_list_files_ex = os.listdir(Con.yaFilesEx + formatPath)
            local_list_files_unex = os.listdir(Con.localFilesUnex + formatPath)
            local_list_files_ex = os.listdir(Con.localFilesEx + formatPath)

            for file in ya_list_files_except:
                if file in local_list_files_unex:
                    os.remove(Con.localFilesUnex + formatPath + '\\' + file)
                    LOG.cms_logger('File deleted by exception: ' + Con.localFilesUnex + formatPath + '\\' + file)
                    refresh_status = True

            if ya_list_files_unex != local_list_files_unex:
                for file in local_list_files_unex:
                    if file not in ya_list_files_unex:
                        os.remove(Con.localFilesUnex + formatPath + '\\' + file)
                        LOG.cms_logger('File deleted: ' + Con.localFilesUnex + formatPath + '\\' + file)
                        refresh_status = True
            if ya_list_files_ex != local_list_files_ex:
                for file in local_list_files_ex:
                    if file not in ya_list_files_ex:
                        os.remove(Con.localFilesEx + formatPath + '\\' + file)
                        LOG.cms_logger('File deleted: ' + Con.localFilesEx + formatPath + '\\' + file)
                        refresh_status = True
        return refresh_status

    def generate(self):
        format_path = None
        for format_path in Con.screenFormat:

            all_file_path_list = []
            all_file_name_list = []

            local_list_files_unex = os.listdir(Con.localFilesUnex + format_path)
            local_list_files_ex = os.listdir(Con.localFilesEx + format_path)

            for file in local_list_files_unex:
                all_file_path_list.append(Con.localFilesUnex + format_path + '\\' + file)
                LOG.cms_logger(
                    'The file is included in the playlist: ' + Con.localFilesUnex + format_path + '\\' + file)
                all_file_name_list.append(file)

            for file in local_list_files_ex:
                all_file_path_list.append(Con.localFilesEx + format_path + '\\' + file)
                LOG.cms_logger(
                    'ФThe file is included in the playlist: ' + Con.localFilesEx + format_path + '\\' + file)
                all_file_name_list.append(file)

            play_program = self.create_xml(all_file_path_list, all_file_name_list)
            self.prettify(play_program)
            tree = Et.ElementTree(play_program)
            tree.write('{}{}_playerConfig.plym'.format(Con.configTargetPath, format_path), encoding='UTF-8',
                       xml_declaration=True)
        LOG.cms_logger('Playlist generated: ' + '{}{}_playerConfig.plym'.format(Con.configTargetPath, format_path))

    @staticmethod
    def create_xml(file_path_arr, file_name_arr):

        x = 0
        play_program = Et.Element('PlayProgram', X="0", Y="0", Width="320", Height="120")
        playlist = Et.SubElement(play_program, 'Playlist', Type="TimeSegment", Name="General Segment1", Date="",
                                 Day="True#True#True#True#True#True#True", Time="", IsSpeficTimeZone="False",
                                 DiffToUTC="00:00:00", ID="0")
        context = Et.SubElement(playlist, 'Context')
        basic_page = Et.SubElement(context, 'BasicPage')
        page = Et.SubElement(basic_page, 'Page', Name="Program1", PlayType="Order", Duration="00:06:00", PlayTimes="1",
                             BackColor="255#0#0#0", BackgroundImage="", ImageLayout="Stretch", BackMusic="",
                             CustomString="")
        window = Et.SubElement(page, 'Window', Name=Con.objType, X="0", Y="0", Width="320", Height="120",
                               Tag="Common")
        for file_path in file_path_arr:
            item = Et.SubElement(window, 'Item', Type="0")
            media = Et.SubElement(item, 'Media')
            video_media = Et.SubElement(media, 'VideoMedia')
            Et.SubElement(video_media, 'Name').text = file_name_arr[x]
            play_duration = Et.SubElement(video_media, 'PlayDuration')
            Et.SubElement(play_duration, 'string').text = '0#0#0#15#0'
            Et.SubElement(video_media, 'BeginTime').text = '0001-01-01T00:00:00'
            Et.SubElement(video_media, 'EndTime').text = '0001-01-01T00:00:00'
            Et.SubElement(video_media, 'Times').text = '-1'
            back_color = Et.SubElement(video_media, 'BackColor')
            Et.SubElement(back_color, 'string').text = '255#0#0#0'
            Et.SubElement(video_media, 'BackImagePath')
            Et.SubElement(video_media, 'BackImageLayout').text = 'Stretch'
            Et.SubElement(video_media, 'Opacity').text = '1'
            Et.SubElement(video_media, 'ID').text = '{}'.format(x + 1)
            Et.SubElement(video_media, 'EnableBorderElement').text = 'false'
            border_element = Et.SubElement(video_media, 'BorderElement')
            Et.SubElement(border_element, 'BorderType').text = '6'
            Et.SubElement(border_element, 'IsClockWise').text = 'true'
            Et.SubElement(border_element, 'Speed').text = '5'
            Et.SubElement(border_element, 'BorderWidth').text = '1'
            back_color = Et.SubElement(border_element, 'BackColor')
            Et.SubElement(back_color, 'string').text = '255#0#0#0'
            fore_color = Et.SubElement(border_element, 'ForeColor')
            Et.SubElement(fore_color, 'string').text = '255#0#128#0'
            Et.SubElement(border_element, 'ColorType').text = '0'
            Et.SubElement(border_element, 'BorderDirectionStyle').text = '0'
            Et.SubElement(border_element, 'BorderSurroundedType').text = '0'
            border_unit_data = Et.SubElement(border_element, 'BorderUnitData')
            Et.SubElement(border_unit_data,
                          'string').text = '''424d9600000000000000360000002800000020000000010000000
                          10018000000000000000000202e0000202e00000000000000000000ff0000ff0000ff0000
                          ff0000ff0000ff0000ff0000ff00000000ff0000ff0000ff0000ff0000ff0000ff0000ff0
                          000ff00ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ffff00ffff00ffff00
                          ffff00ffff00ffff00ffff00ffff'''
            border_left_unit_data = Et.SubElement(border_element, 'BorderLeftUnitData')
            Et.SubElement(border_left_unit_data, 'string')
            border_right_unit_data = Et.SubElement(border_element, 'BorderRightUnitData')
            Et.SubElement(border_right_unit_data, 'string')
            border_bottom_unit_data = Et.SubElement(border_element, 'BorderBottomUnitData')
            Et.SubElement(border_bottom_unit_data, 'string')
            Et.SubElement(video_media, 'Tag')
            Et.SubElement(video_media, 'FinishedMode').text = 'PlayInSpecTime'
            Et.SubElement(video_media, 'RotateAngle').text = 'None'
            Et.SubElement(video_media, 'Path').text = file_path
            Et.SubElement(video_media, 'DispRatioType').text = 'Full'
            txt_element = Et.SubElement(video_media, 'TxtElement')
            text_font = Et.SubElement(txt_element, 'TextFont')
            Et.SubElement(text_font, 'string').text = 'Arial#12#Regular#Point#12'
            text_color = Et.SubElement(txt_element, 'TextColor')
            Et.SubElement(text_color, 'string').text = '255#255#0#0'
            Et.SubElement(txt_element, 'IsTextEffect').text = 'false'
            Et.SubElement(txt_element, 'TextEffectType').text = '0'
            text_effect_color = Et.SubElement(txt_element, 'TextEffectColor')
            Et.SubElement(text_effect_color, 'string').text = '255#255#255#0'
            Et.SubElement(txt_element, 'TextEffectWidth').text = '2'
            Et.SubElement(txt_element, 'TextAlignment').text = 'TopLeft'
            Et.SubElement(video_media, 'IsShowTextElement').text = 'false'
            Et.SubElement(video_media, 'VolumnPercent').text = '0'
            Et.SubElement(video_media, 'RotateType').text = 'None'
            Et.SubElement(video_media, 'IsStartFromSpecificPos').text = 'false'
            start_position = Et.SubElement(video_media, 'StartPosition')
            Et.SubElement(start_position, 'string').text = '0#0#0#0#0'
            end_position = Et.SubElement(video_media, 'EndPosition')
            Et.SubElement(end_position, 'string').text = '0#0#0#15#0'
            Et.SubElement(item, 'AdditionalInfo')
            x += 1
        global_page = Et.SubElement(context, 'GlobalPage')
        Et.SubElement(global_page, 'Page')

        return play_program

    @staticmethod
    def prettify(element, ident='   '):
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

    def backup_handle(self):
        if self.check_nova_file() is True:
            self.backup_nova_bin()
        else:
            LOG.cms_logger('NovaBin backup canceled')

    def restore_handle(self):
        c_nova = API.Nova()
        if self.check_nova_file() is not True:
            if c_nova.get_proc_state(Resource.ProcList[0]) is True:
                c_nova.terminate_nova()
            if self.restore_nova_bin() is True:
                LOG.cms_logger('NovaBin recovery completed')
            else:
                LOG.cms_logger('NovaBin restore canceled')
        else:
            LOG.cms_logger('NovaBin restore canceled')

    @staticmethod
    def check_nova_file():
        if os.path.exists(Con.novaBinFile):
            file = open(Con.novaBinFile, 'rb')
            string = file.read()
            if re.search('zh-CN', str(string)):
                return False
            else:
                return True
        else:
            return None

    @staticmethod
    def restore_nova_bin():
        if os.path.exists(Con.novaBinFileBak):
            shutil.copy(Con.novaBinFileBak, Con.novaBinFile)

            return True
        else:
            return False

    @staticmethod
    def backup_nova_bin():
        shutil.copy(Con.novaBinFile, Con.novaBinFileBak)
        LOG.cms_logger('NovaBin has been backed up')
