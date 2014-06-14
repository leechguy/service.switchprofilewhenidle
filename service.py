import os
import time
import xbmc
import xbmcaddon
import profilesxml
import settingsxml

### get addon info
__addon__       = xbmcaddon.Addon(id='service.switchprofilewhenidle')
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__version__     = __addon__.getAddonInfo('version')


CHECK_TIME_DISABLED = 1893477600 # unix timestamp for 1/1/2030
RESUME_TIMEOUT = 5
SLEEP_TIME = 1000

class activityMonitor(xbmc.Monitor):

    autologin_profile = ""
    check_time = 0
    max_idle_time = 0
    screensaverActivated = False
    use_idle_timer = True
    use_login_screen = False
    profiles = None
    settings = None

    def __init__(self):
        self.profiles = profilesxml.ProfilesXml(os.path.join(xbmc.translatePath('special://masterprofile'), 'profiles.xml'))
        self.settings = settingsxml.SettingsXml(os.path.join(xbmc.translatePath('special://masterprofile'), 'addon_data', __addonid__, 'settings.xml'))

        self.autologin_profile = self.profiles.getAutoLoginProfileName()
        self.settings.parse()
        self.max_idle_time = self.getMaxIdleTime()
        self.use_idle_timer = (self.settings.getSetting('useIdleTimer') == 'true')
        self.use_login_screen = self.profiles.getUseLoginScreen()
        log("auto login profile: " + self.autologin_profile)

    def __del__(self):
        del self.profiles
        del self.settings


    def process(self):

        if not self.use_idle_timer:
            # skip all, go to sleep
            pass
        elif xbmc.Player().isPlaying():
            # while playing media we reset the check_time to prevent that we're being
            # logged out immediately after playing stops
            self.check_time = time.time()
        elif xbmc.getGlobalIdleTime() == 0:
            # user activity so we reset the check_time to 'now'
            self.check_time = time.time()
        elif (time.time() - self.check_time) > self.max_idle_time and xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
            idle_time = time.time() - self.check_time
            # set check_time to 1/1/2030 so we only swap profiles / perform logout once
            # until the user comes back
            self.check_time = CHECK_TIME_DISABLED
            # Activate window to disable the screensaver
            if self.screensaverActivated:
                xbmc.executebuiltin("XBMC.ActivateWindow(home)")

            active_profile = xbmc.getInfoLabel('System.ProfileName')
            if self.use_login_screen:
                log("System idle for %d seconds; logging %s out." % (idle_time, active_profile))
                xbmc.executebuiltin('System.LogOff')
            elif xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
                log("System idle for %d seconds; switching from %s to auto login profile %s" % (idle_time, active_profile, self.autologin_profile))
                xbmc.executebuiltin("XBMC.LoadProfile(" + self.autologin_profile + ", prompt)")


#    def resumeWatchdog(self):
#         if use_resume_watchdog:
#            if (time.time() - resume_watchdog_time) > RESUME_TIMEOUT and xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
#                if self.use_login_screen:
#                    log("System resuming after suspend; logging out.")
#                    xbmc.executebuiltin('System.LogOff')
#                elif xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
#                    log("System resuming after suspend; switching to default profile")
#                    xbmc.executebuiltin("XBMC.LoadProfile(" + self.autologin_profile + ", prompt)")
#            resume_watchdog_time = time.time()



    def getMaxIdleTime(self):
        max_idle_time = self.settings.getSetting('maxIdleTime') #.rstrip('0').rstrip('.')
        if max_idle_time == "":
            max_idle_time = "5"
        return int(max_idle_time) * 60


    # xbmc.Monitor method implementations

    def onNotification(self, sender, method, data):
        #log("onNotification(sender=" + sender + ", method=" + method + ", data=" + data)

        if method == "System.OnSleep" and xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
            if self.use_login_screen:
                log("System going to sleep; logging out.")
                xbmc.executebuiltin('System.LogOff')
            elif xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
                log("System going to sleep; switching to default profile")
                xbmc.executebuiltin("XBMC.LoadProfile(" + self.autologin_profile + ", prompt)")

        if method == "System.OnWake" and xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
            if self.use_login_screen:
                log("System resuming; logging out.")
                xbmc.executebuiltin('System.LogOff')
            elif xbmc.getInfoLabel('System.ProfileName') != self.autologin_profile:
                log("System resuming; switching to default profile")
                xbmc.executebuiltin("XBMC.LoadProfile(" + self.autologin_profile + ", prompt)")


    def onScreensaverActivated(self):
        #log("onScreensaverActivated")
        self.screensaverActivated = True


    def onScreensaverDeactivated(self):
        #log("onScreensaverDeactivated")
        self.screensaverActivated = False


    def onSettingsChanged(self):
        #log("onSettingsChanged")
        self.settings.parse()
        self.max_idle_time = self.getMaxIdleTime()
        self.use_idle_timer = (self.settings.getSetting('useIdleTimer') == 'true')



def log(message):
    xbmc.log(__addonid__ + ': ' + message)


if (__name__ == "__main__"):

    log('Starting: ' + __addonname__ + ' v' + __version__)

    # only allow configuration of the addon by the master user
    isMasterProfile = (xbmc.translatePath('special://masterprofile') == xbmc.translatePath('special://profile'))
    if isMasterProfile:
        __addon__.setSetting('isMasterUser', 'true')
    else:
        __addon__.setSetting('isMasterUser', 'false')

    activityMonitor = activityMonitor()
    while (not xbmc.abortRequested):

        activityMonitor.process()

        if not xbmc.abortRequested:
            xbmc.sleep(SLEEP_TIME)


    del activityMonitor

    log('Stopped: ' + __addonname__ + ' v' + __version__)

