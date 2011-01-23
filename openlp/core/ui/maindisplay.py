# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
The :mod:`maindisplay` module provides the functionality to display screens
and play multimedia within OpenLP.
"""
import logging
import os

from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.phonon import Phonon

from openlp.core.lib import Receiver, build_html, ServiceItem, image_to_byte, \
    build_icon, translate

from openlp.core.ui import HideMode

log = logging.getLogger(__name__)

#http://www.steveheffernan.com/html5-video-player/demo-video-player.html
#http://html5demos.com/two-videos

class DisplayWidget(QtGui.QGraphicsView):
    """
    Customised version of QTableWidget which can respond to keyboard
    events.
    """
    log.info(u'Display Widget loaded')

    def __init__(self, live, parent=None):
        QtGui.QGraphicsView.__init__(self)
        self.parent = parent
        self.live = live


class MainDisplay(DisplayWidget):
    """
    This is the display screen.
    """
    def __init__(self, parent, screens, live):
        DisplayWidget.__init__(self, live, parent=None)
        self.parent = parent
        self.screens = screens
        self.isLive = live
        self.alertTab = None
        self.hideMode = None
        self.override_image = None
        mainIcon = build_icon(u':/icon/openlp-logo-16x16.png')
        self.setWindowIcon(mainIcon)
        self.retranslateUi()
        self.setStyleSheet(u'border: 0px; margin: 0px; padding: 0px;')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint)
        if self.isLive:
            QtCore.QObject.connect(Receiver.get_receiver(),
                QtCore.SIGNAL(u'maindisplay_hide'), self.hideDisplay)
            QtCore.QObject.connect(Receiver.get_receiver(),
                QtCore.SIGNAL(u'maindisplay_show'), self.showDisplay)

    def retranslateUi(self):
        """
        Setup the interface translation strings.
        """
        self.setWindowTitle(translate('OpenLP.MainDisplay', 'OpenLP Display'))

    def setup(self):
        """
        Set up and build the output screen
        """
        log.debug(u'Setup live = %s for monitor %s ' % (self.isLive,
            self.screens.monitor_number))
        self.usePhonon = QtCore.QSettings().value(
            u'media/use phonon', QtCore.QVariant(True)).toBool()
        self.phononActive = False
        self.screen = self.screens.current
        self.setVisible(False)
        self.setGeometry(self.screen[u'size'])
        self.videoWidget = Phonon.VideoWidget(self)
        self.videoWidget.setVisible(False)
        self.videoWidget.setGeometry(QtCore.QRect(0, 0,
            self.screen[u'size'].width(), self.screen[u'size'].height()))
        self.mediaObject = Phonon.MediaObject(self)
        self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self.mediaObject)
        Phonon.createPath(self.mediaObject, self.videoWidget)
        Phonon.createPath(self.mediaObject, self.audio)
        self.webView = QtWebKit.QWebView(self)
        self.webView.setGeometry(0, 0,
            self.screen[u'size'].width(), self.screen[u'size'].height())
        self.page = self.webView.page()
        self.frame = self.page.mainFrame()
        QtCore.QObject.connect(self.webView,
            QtCore.SIGNAL(u'loadFinished(bool)'), self.isLoaded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.frame.setScrollBarPolicy(QtCore.Qt.Vertical,
            QtCore.Qt.ScrollBarAlwaysOff)
        self.frame.setScrollBarPolicy(QtCore.Qt.Horizontal,
            QtCore.Qt.ScrollBarAlwaysOff)
        if self.isLive:
            # Build the initial frame.
            self.black = QtGui.QImage(
                self.screens.current[u'size'].width(),
                self.screens.current[u'size'].height(),
                QtGui.QImage.Format_ARGB32_Premultiplied)
            painter_image = QtGui.QPainter()
            painter_image.begin(self.black)
            painter_image.fillRect(self.black.rect(), QtCore.Qt.black)
            # Build the initial frame.
            initialFrame = QtGui.QImage(
                self.screens.current[u'size'].width(),
                self.screens.current[u'size'].height(),
                QtGui.QImage.Format_ARGB32_Premultiplied)
            splash_image = QtGui.QImage(u':/graphics/openlp-splash-screen.png')
            painter_image = QtGui.QPainter()
            painter_image.begin(initialFrame)
            painter_image.fillRect(initialFrame.rect(), QtCore.Qt.white)
            painter_image.drawImage(
                (self.screens.current[u'size'].width() - 
                splash_image.width()) / 2,
                (self.screens.current[u'size'].height()
                - splash_image.height()) / 2, splash_image)
            serviceItem = ServiceItem()
            serviceItem.bg_image_bytes = image_to_byte(initialFrame)
            self.webView.setHtml(build_html(serviceItem, self.screen,
                self.parent.alertTab, self.isLive))
            self.initialFrame = True
            # To display or not to display?
            if not self.screen[u'primary']:
                self.show()
                self.primary = False
            else:
                self.primary = True

    def text(self, slide):
        """
        Add the slide text from slideController

        `slide`
            The slide text to be displayed
        """
        log.debug(u'text to display')
        # Wait for the webview to update before displaying text.
        while not self.loaded:
            Receiver.send_message(u'openlp_process_events')
        self.frame.evaluateJavaScript(u'show_text("%s")' % \
            slide.replace(u'\\', u'\\\\').replace(u'\"', u'\\\"'))
        return self.preview()

    def alert(self, text):
        """
        Add the alert text

        `slide`
            The slide text to be displayed
        """
        log.debug(u'alert to display')
        if self.height() != self.screen[u'size'].height() \
            or not self.isVisible() or self.videoWidget.isVisible():
            shrink = True
        else:
            shrink = False
        js = u'show_alert("%s", "%s")' % (
            text.replace(u'\\', u'\\\\').replace(u'\"', u'\\\"'),
            u'top' if shrink else u'')
        height = self.frame.evaluateJavaScript(js)
        if shrink:
            if self.phononActive:
                shrinkItem = self.webView
            else:
                shrinkItem = self
            if text:
                shrinkItem.resize(self.width(), int(height.toString()))
                shrinkItem.setVisible(True)
            else:
                shrinkItem.setVisible(False)
                shrinkItem.resize(self.screen[u'size'].width(),
                    self.screen[u'size'].height())

    def directImage(self, name, path):
        """
        API for replacement backgrounds so Images are added directly to cache
        """
        self.imageManager.add_image(name, path)
        self.image(name)
        self.override_image = name

    def image(self, name):
        """
        Add an image as the background. The image has already been added
        to the cache.

        `Image`
            The name of the image to be displayed
        """
        log.debug(u'image to display')
        image = self.imageManager.get_image_bytes(name)
        self.resetVideo()
        self.displayImage(image)
        # show screen
        if self.isLive:
            self.setVisible(True)
        return self.preview()

    def displayImage(self, image):
        """
        Display an image, as is.
        """
        if image:
            js = u'show_image("data:image/png;base64,%s");' % image
        else:
            js = u'show_image("");'
        self.frame.evaluateJavaScript(js)
        # Update the preview frame.
        Receiver.send_message(u'maindisplay_active')

    def resetImage(self):
        """
        Reset the backgound image to the service item image.
        Used after Image plugin has changed the background
        """
        log.debug(u'resetImage')
        if hasattr(self, u'serviceItem'):
            self.displayImage(self.serviceItem.bg_image_bytes)
        else:
            self.displayImage(None)
        # Update the preview frame.
        Receiver.send_message(u'maindisplay_active')

    def resetVideo(self):
        """
        Used after Video plugin has changed the background
        """
        log.debug(u'resetVideo')
        if self.phononActive:
            self.mediaObject.stop()
            self.mediaObject.clearQueue()
            self.webView.setVisible(True)
            self.videoWidget.setVisible(False)
            self.phononActive = False
        else:
            self.frame.evaluateJavaScript(u'show_video("close");')
        # Update the preview frame.
        Receiver.send_message(u'maindisplay_active')

    def videoPlay(self):
        """
        Responds to the request to play a loaded video
        """
        log.debug(u'videoPlay')
        if self.phononActive:
            self.mediaObject.play()
        else:
            self.frame.evaluateJavaScript(u'show_video("play");')
        # show screen
        if self.isLive:
            self.setVisible(True)

    def videoPause(self):
        """
        Responds to the request to pause a loaded video
        """
        log.debug(u'videoPause')
        if self.phononActive:
            self.mediaObject.pause()
        else:
            self.frame.evaluateJavaScript(u'show_video("pause");')

    def videoStop(self):
        """
        Responds to the request to stop a loaded video
        """
        log.debug(u'videoStop')
        if self.phononActive:
            self.mediaObject.stop()
        else:
            self.frame.evaluateJavaScript(u'show_video("stop");')

    def videoVolume(self, volume):
        """
        Changes the volume of a running video
        """
        log.debug(u'videoVolume %d' % volume)
        vol = float(volume)/float(10)
        if self.phononActive:
            self.audio.setVolume(vol)
        else:
            self.frame.evaluateJavaScript(u'show_video(null, null, %s);' %
                str(vol))

    def video(self, videoPath, volume, isBackground=False):
        """
        Loads and starts a video to run with the option of sound
        """
        log.debug(u'video')
        self.loaded = True
        vol = float(volume)/float(10)
        if isBackground or not self.usePhonon:
            js = u'show_video("init", "%s", %s, true); show_video("play");' % \
                (videoPath.replace(u'\\', u'\\\\'), \
                str(vol))
            self.frame.evaluateJavaScript(js)
        else:
            self.phononActive = True
            self.mediaObject.stop()
            self.mediaObject.clearQueue()
            self.mediaObject.setCurrentSource(Phonon.MediaSource(videoPath))
            self.mediaObject.play()
            self.webView.setVisible(False)
            self.videoWidget.setVisible(True)
            self.audio.setVolume(vol)
        # Update the preview frame.
        Receiver.send_message(u'maindisplay_active')
        return self.preview()

    def isLoaded(self):
        """
        Called by webView event to show display is fully loaded
        """
        log.debug(u'loaded')
        self.loaded = True

    def preview(self):
        """
        Generates a preview of the image displayed.
        """
        log.debug(u'preview for %s', self.isLive)
        Receiver.send_message(u'openlp_process_events')
        # We must have a service item to preview
        if self.isLive and hasattr(self, u'serviceItem'):
            # Wait for the fade to finish before geting the preview.
            # Important otherwise preview will have incorrect text if at all!
            if self.serviceItem.themedata and \
                self.serviceItem.themedata.display_slide_transition:
                while self.frame.evaluateJavaScript(u'show_text_complete()') \
                    .toString() == u'false':
                    Receiver.send_message(u'openlp_process_events')
        # Wait for the webview to update before geting the preview.
        # Important otherwise first preview will miss the background !
        while not self.loaded:
            Receiver.send_message(u'openlp_process_events')
        # if was hidden keep it hidden
        if self.isLive:
            self.setVisible(True)
            if self.hideMode:
                self.hideDisplay(self.hideMode)
        preview = QtGui.QImage(self.screen[u'size'].width(),
            self.screen[u'size'].height(),
            QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(preview)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.frame.render(painter)
        painter.end()
        return preview

    def buildHtml(self, serviceItem):
        """
        Store the serviceItem and build the new HTML from it. Add the
        HTML to the display
        """
        log.debug(u'buildHtml')
        self.loaded = False
        self.initialFrame = False
        self.serviceItem = serviceItem
        if self.serviceItem.themedata.background_filename:
            self.serviceItem.bg_image_bytes = self.imageManager. \
                get_image_bytes(self.serviceItem.themedata.theme_name)
        html = build_html(self.serviceItem, self.screen, self.parent.alertTab,
            self.isLive)
        log.debug(u'buildHtml - pre setHtml')
        self.webView.setHtml(html)
        log.debug(u'buildHtml - post setHtml')
        if serviceItem.foot_text and serviceItem.foot_text:
            self.footer(serviceItem.foot_text)
        # if was hidden keep it hidden
        if self.hideMode and self.isLive:
            self.hideDisplay(self.hideMode)
        # Hide mouse cursor when moved over display if enabled in settings
        settings = QtCore.QSettings()
        if settings.value(u'advanced/hide mouse',
            QtCore.QVariant(False)).toBool():
            self.setCursor(QtCore.Qt.BlankCursor)
            self.frame.evaluateJavaScript('document.body.style.cursor = "none"')
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.frame.evaluateJavaScript('document.body.style.cursor = "auto"')

    def footer(self, text):
        """
        Display the Footer
        """
        log.debug(u'footer')
        js = u'show_footer(\'' + \
            text.replace(u'\\', u'\\\\').replace(u'\'', u'\\\'') + u'\')'
        self.frame.evaluateJavaScript(js)

    def hideDisplay(self, mode=HideMode.Screen):
        """
        Hide the display by making all layers transparent
        Store the images so they can be replaced when required
        """
        log.debug(u'hideDisplay mode = %d', mode)
        if self.phononActive:
            self.videoPause()
        if mode == HideMode.Screen:
            self.frame.evaluateJavaScript(u'show_blank("desktop");')
            self.setVisible(False)
        elif mode == HideMode.Blank or self.initialFrame:
            self.frame.evaluateJavaScript(u'show_blank("black");')
        else:
            self.frame.evaluateJavaScript(u'show_blank("theme");')
        if mode != HideMode.Screen:
            if self.isHidden():
                self.setVisible(True)
            if self.phononActive:
                self.webView.setVisible(True)
        self.hideMode = mode

    def showDisplay(self):
        """
        Show the stored layers so the screen reappears as it was
        originally.
        Make the stored images None to release memory.
        """
        log.debug(u'showDisplay')
        self.frame.evaluateJavaScript('show_blank("show");')
        if self.isHidden():
            self.setVisible(True)
        if self.phononActive:
            self.webView.setVisible(False)
            self.videoPlay()
        self.hideMode = None
        # Trigger actions when display is active again
        Receiver.send_message(u'maindisplay_active')


class AudioPlayer(QtCore.QObject):
    """
    This Class will play audio only allowing components to work with a
    soundtrack independent of the user interface.
    """
    log.info(u'AudioPlayer Loaded')

    def __init__(self, parent):
        """
        The constructor for the display form.

        ``parent``
            The parent widget.

        ``screens``
            The list of screens.
        """
        log.debug(u'AudioPlayer Initialisation started')
        QtCore.QObject.__init__(self, parent)
        self.message = None
        self.mediaObject = Phonon.MediaObject()
        self.audioObject = Phonon.AudioOutput(Phonon.VideoCategory)
        Phonon.createPath(self.mediaObject, self.audioObject)

    def setup(self):
        """
        Sets up the Audio Player for use
        """
        log.debug(u'AudioPlayer Setup')

    def close(self):
        """
        Shutting down so clean up connections
        """
        self.onMediaStop()
        for path in self.mediaObject.outputPaths():
            path.disconnect()

    def onMediaQueue(self, message):
        """
        Set up a video to play from the serviceitem.
        """
        log.debug(u'AudioPlayer Queue new media message %s' % message)
        mfile = os.path.join(message[0].get_frame_path(),
            message[0].get_frame_title())
        self.mediaObject.setCurrentSource(Phonon.MediaSource(mfile))
        self.onMediaPlay()

    def onMediaPlay(self):
        """
        We want to play the play so start it
        """
        log.debug(u'AudioPlayer _play called')
        self.mediaObject.play()

    def onMediaPause(self):
        """
        Pause the Audio
        """
        log.debug(u'AudioPlayer Media paused by user')
        self.mediaObject.pause()

    def onMediaStop(self):
        """
        Stop the Audio and clean up
        """
        log.debug(u'AudioPlayer Media stopped by user')
        self.message = None
        self.mediaObject.stop()
        self.onMediaFinish()

    def onMediaFinish(self):
        """
        Clean up the Object queue
        """
        log.debug(u'AudioPlayer Reached end of media playlist')
        self.mediaObject.clearQueue()
