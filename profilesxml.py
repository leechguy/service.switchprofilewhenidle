import re
from xml.dom.minidom import parse

class ProfilesXml:
    """
    This class handles all interaction with XBMC's profiles.xml file.
    """
    def __init__(self, profilesXml):
        self.profilesXml = profilesXml
        self.dom = parse(self.profilesXml)


    def getUseLoginScreen(self):
        # dom = parse(self.profilesXml)
        return (self.getText(self.dom.getElementsByTagName('useloginscreen')[0].childNodes) == 'true')


    def getAutoLoginProfileId(self):
        return int(self.getText(self.dom.getElementsByTagName('autologin')[0].childNodes))


    def getAutoLoginProfileName(self):
        profile_id = self.getAutoLoginProfileId()
        if profile_id >= 0:
            return self.getProfileName(profile_id)

        # no autologin profile selected
        return ""


    def getProfileName(self, profile_id):
        id = 0
        for node in self.dom.getElementsByTagName('profile'):
            name = self.getText(node.getElementsByTagName('name')[0].childNodes)
            profile_id = self.getAutoLoginProfileId()
            if id == profile_id:
                return name
            id = id + 1

        # profile not found!
        return ""


    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


    def readProfileXml(self):
        fh = file(self.profilesXml, 'r')
        profileXml = fh.read()
        fh.close()
        return profileXml

