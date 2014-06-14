import sys
from xml.dom import minidom

class SettingsXml:
    """
    This class handles all interaction with this addons service.xml file.
    """    
    settings = {}

    def __init__(self, settingsXml):

        self.settingsXml = settingsXml

    def parse(self):

        dom = minidom.parse(self.settingsXml)
        settingsList = dom.getElementsByTagName('setting')

        self.settings.clear()
        for setting in settingsList:
            id = setting.attributes['id'].value
            value = setting.attributes['value'].value

            self.settings[id] = value
 
    def getSetting(self, name):

        try:
            value = self.settings[name]
        except Exception, err:
            value = ""

        return value

