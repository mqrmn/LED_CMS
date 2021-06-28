#v.1.1.0

from App.Config import Config


class Default:

    def TempFiles(self):
        f = open('{}lastShutDown.txt'.format(Config.tempPath), 'w')
        f.write('0')
        f.close()

        f = open('{}userState.txt'.format(Config.tempPath), 'w')
        f.write('0')
        f.close()

        f = open('{}screenState.txt'.format(Config.tempPath), 'w')
        f.write('2')
        f.close()