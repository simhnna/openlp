# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2013 Raoul Snyman                                        #
# Portions copyright (c) 2008-2013 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
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
The :mod:`maindisplay` module provides the functionality to display screens and play multimedia within OpenLP.

Some of the code for this form is based on the examples at:

* `http://www.steveheffernan.com/html5-video-player/demo-video-player.html`_
* `http://html5demos.com/two-videos`_

"""
import cgi
import logging
import sys

from PyQt4 import QtCore, QtGui, QtWebKit, QtOpenGL
from PyQt4.phonon import Phonon

from openlp.core.lib import ServiceItem, Settings, ImageSource, Registry, build_html, expand_tags, \
    image_to_byte, translate
from openlp.core.lib.theme import BackgroundType

from openlp.core.lib import ScreenList
from openlp.core.ui import HideMode, AlertLocation

log = logging.getLogger(__name__)


class Display(QtGui.QGraphicsView):
    """
    This is a general display screen class. Here the general display settings
    will done. It will be used as specialized classes by Main Display and
    Preview display.
    """
    def __init__(self, parent, live, controller):
        """
        Constructor
        """
        if live:
            QtGui.QGraphicsView.__init__(self)
            # Overwrite the parent() method.
            self.parent = lambda: parent
        else:
            QtGui.QGraphicsView.__init__(self, parent)
        self.isLive = live
        self.controller = controller
        self.screen = {}
        # FIXME: On Mac OS X (tested on 10.7) the display screen is corrupt with
        # OpenGL. Only white blank screen is shown on the 2nd monitor all the
        # time. We need to investigate more how to use OpenGL properly on Mac OS
        # X.
        if sys.platform != 'darwin':
            self.setViewport(QtOpenGL.QGLWidget())

    def setup(self):
        """
        Set up and build the screen base
        """
        log.debug(u'Start Display base setup (live = %s)' % self.isLive)
        self.setGeometry(self.screen[u'size'])
        log.debug(u'Setup webView')
        self.webView = QtWebKit.QWebView(self)
        self.webView.setGeometry(0, 0, self.screen[u'size'].width(), self.screen[u'size'].height())
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        palette = self.webView.palette()
        palette.setBrush(QtGui.QPalette.Base, QtCore.Qt.transparent)
        self.webView.page().setPalette(palette)
        self.webView.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
        self.page = self.webView.page()
        self.frame = self.page.mainFrame()
        if self.isLive and log.getEffectiveLevel() == logging.DEBUG:
            self.webView.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        QtCore.QObject.connect(self.webView,
            QtCore.SIGNAL(u'loadFinished(bool)'), self.isWebLoaded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.frame.setScrollBarPolicy(QtCore.Qt.Vertical,
            QtCore.Qt.ScrollBarAlwaysOff)
        self.frame.setScrollBarPolicy(QtCore.Qt.Horizontal,
            QtCore.Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        """
        React to resizing of this display
        """
        self.webView.setGeometry(0, 0, self.width(), self.height())

    def isWebLoaded(self):
        """
        Called by webView event to show display is fully loaded
        """
        log.debug(u'Webloaded')
        self.webLoaded = True


class MainDisplay(Display):
    """
    This is the display screen as a specialized class from the Display class
    """
    def __init__(self, parent, live, controller):
        """
        Constructor
        """
        Display.__init__(self, parent, live, controller)
        self.screens = ScreenList()
        self.rebuildCSS = False
        self.hideMode = None
        self.override = {}
        self.retranslateUi()
        self.mediaObject = None
        if live:
            self.audioPlayer = AudioPlayer(self)
        else:
            self.audioPlayer = None
        self.firstTime = True
        self.webLoaded = True
        self.setStyleSheet(u'border: 0px; margin: 0px; padding: 0px;')
        windowFlags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint
        if Settings().value(u'advanced/x11 bypass wm'):
            windowFlags |= QtCore.Qt.X11BypassWindowManagerHint
        # TODO: The following combination of windowFlags works correctly
        # on Mac OS X. For next OpenLP version we should test it on other
        # platforms. For OpenLP 2.0 keep it only for OS X to not cause any
        # regressions on other platforms.
        if sys.platform == 'darwin':
            windowFlags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window
            # For primary screen ensure it stays above the OS X dock
            # and menu bar
            if self.screens.current[u'primary']:
                self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setWindowFlags(windowFlags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setTransparency(False)
        if self.isLive:
            Registry().register_function(u'live_display_hide', self.hide_display)
            Registry().register_function(u'live_display_show', self.show_display)
            Registry().register_function(u'update_display_css', self.css_changed)
            Registry().register_function(u'config_updated', self.config_changed)

    def setTransparency(self, enabled):
        """
        Set the transparency of the window
        """
        if enabled:
            self.setAutoFillBackground(False)
        else:
            self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, enabled)
        self.repaint()

    def css_changed(self):
        """
        We may need to rebuild the CSS on the live display.
        """
        self.rebuildCSS = True

    def config_changed(self):
        """
        Call the plugins to rebuild the Live display CSS as the screen has
        not been rebuild on exit of config.
        """
        if self.rebuildCSS and self.plugin_manager.plugins:
            for plugin in self.plugin_manager.plugins:
                plugin.refreshCss(self.frame)
        self.rebuildCSS = False

    def retranslateUi(self):
        """
        Setup the interface translation strings.
        """
        self.setWindowTitle(translate('OpenLP.MainDisplay', 'OpenLP Display'))

    def setup(self):
        """
        Set up and build the output screen
        """
        log.debug(u'Start MainDisplay setup (live = %s)' % self.isLive)
        self.screen = self.screens.current
        self.setVisible(False)
        Display.setup(self)
        if self.isLive:
            # Build the initial frame.
            background_color = QtGui.QColor()
            background_color.setNamedColor(Settings().value(u'advanced/default color'))
            if not background_color.isValid():
                background_color = QtCore.Qt.white
            image_file = Settings().value(u'advanced/default image')
            splash_image = QtGui.QImage(image_file)
            self.initialFrame = QtGui.QImage(
                self.screen[u'size'].width(),
                self.screen[u'size'].height(),
                QtGui.QImage.Format_ARGB32_Premultiplied)
            painter_image = QtGui.QPainter()
            painter_image.begin(self.initialFrame)
            painter_image.fillRect(self.initialFrame.rect(), background_color)
            painter_image.drawImage(
                (self.screen[u'size'].width() - splash_image.width()) / 2,
                (self.screen[u'size'].height() - splash_image.height()) / 2,
                splash_image)
            serviceItem = ServiceItem()
            serviceItem.bg_image_bytes = image_to_byte(self.initialFrame)
            self.webView.setHtml(build_html(serviceItem, self.screen, self.isLive, None,
                plugins=self.plugin_manager.plugins))
            self.__hideMouse()
        log.debug(u'Finished MainDisplay setup')

    def text(self, slide, animate=True):
        """
        Add the slide text from slideController

        ``slide``
            The slide text to be displayed

        ``animate``
            Perform transitions if applicable when setting the text
        """
        log.debug(u'text to display')
        # Wait for the webview to update before displaying text.
        while not self.webLoaded:
            self.application.process_events()
        self.setGeometry(self.screen[u'size'])
        if animate:
            self.frame.evaluateJavaScript(u'show_text("%s")' % slide.replace(u'\\', u'\\\\').replace(u'\"', u'\\\"'))
        else:
            # This exists for https://bugs.launchpad.net/openlp/+bug/1016843
            # For unknown reasons if evaluateJavaScript is called
            # from the themewizard, then it causes a crash on
            # Windows if there are many items in the service to re-render.
            # Setting the div elements direct seems to solve the issue
            self.frame.findFirstElement("#lyricsmain").setInnerXml(slide)
            self.frame.findFirstElement("#lyricsoutline").setInnerXml(slide)
            self.frame.findFirstElement("#lyricsshadow").setInnerXml(slide)

    def alert(self, text, location):
        """
        Display an alert.

        ``text``
            The text to be displayed.
        """
        log.debug(u'alert to display')
        # First we convert <>& marks to html variants, then apply
        # formattingtags, finally we double all backslashes for JavaScript.
        text_prepared = expand_tags(cgi.escape(text)).replace(u'\\', u'\\\\').replace(u'\"', u'\\\"')
        if self.height() != self.screen[u'size'].height() or not self.isVisible():
            shrink = True
            js = u'show_alert("%s", "%s")' % (text_prepared, u'top')
        else:
            shrink = False
            js = u'show_alert("%s", "")' % text_prepared
        height = self.frame.evaluateJavaScript(js)
        if shrink:
            if text:
                alert_height = int(height)
                self.resize(self.width(), alert_height)
                self.setVisible(True)
                if location == AlertLocation.Middle:
                    self.move(self.screen[u'size'].left(), (self.screen[u'size'].height() - alert_height) / 2)
                elif location == AlertLocation.Bottom:
                    self.move(self.screen[u'size'].left(), self.screen[u'size'].height() - alert_height)
            else:
                self.setVisible(False)
                self.setGeometry(self.screen[u'size'])

    def directImage(self, path, background):
        """
        API for replacement backgrounds so Images are added directly to cache.
        """
        self.image_manager.add_image(path, ImageSource.ImagePlugin, background)
        if not hasattr(self, u'serviceItem'):
            return False
        self.override[u'image'] = path
        self.override[u'theme'] = self.serviceItem.themedata.background_filename
        self.image(path)
        # Update the preview frame.
        if self.isLive:
            self.parent().updatePreview()
        return True

    def image(self, path):
        """
        Add an image as the background. The image has already been added to the
        cache.

        ``path``
            The path to the image to be displayed. **Note**, the path is only
            passed to identify the image. If the image has changed it has to be
            re-added to the image manager.
        """
        log.debug(u'image to display')
        image = self.image_manager.get_image_bytes(path, ImageSource.ImagePlugin)
        self.controller.media_controller.media_reset(self.controller)
        self.displayImage(image)

    def displayImage(self, image):
        """
        Display an image, as is.
        """
        self.setGeometry(self.screen[u'size'])
        if image:
            js = u'show_image("data:image/png;base64,%s");' % image
        else:
            js = u'show_image("");'
        self.frame.evaluateJavaScript(js)

    def resetImage(self):
        """
        Reset the backgound image to the service item image. Used after the
        image plugin has changed the background.
        """
        log.debug(u'resetImage')
        if hasattr(self, u'serviceItem'):
            self.displayImage(self.serviceItem.bg_image_bytes)
        else:
            self.displayImage(None)
        # clear the cache
        self.override = {}

    def preview(self):
        """
        Generates a preview of the image displayed.
        """
        log.debug(u'preview for %s', self.isLive)
        self.application.process_events()
        # We must have a service item to preview.
        if self.isLive and hasattr(self, u'serviceItem'):
            # Wait for the fade to finish before geting the preview.
            # Important otherwise preview will have incorrect text if at all!
            if self.serviceItem.themedata and self.serviceItem.themedata.display_slide_transition:
                while self.frame.evaluateJavaScript(u'show_text_complete()') == u'false':
                    self.application.process_events()
        # Wait for the webview to update before getting the preview.
        # Important otherwise first preview will miss the background !
        while not self.webLoaded:
            self.application.process_events()
        # if was hidden keep it hidden
        if self.isLive:
            if self.hideMode:
                self.hide_display(self.hideMode)
            else:
                # Single screen active
                if self.screens.display_count == 1:
                    # Only make visible if setting enabled.
                    if Settings().value(u'general/display on monitor'):
                        self.setVisible(True)
                else:
                    self.setVisible(True)
        return QtGui.QPixmap.grabWidget(self)

    def buildHtml(self, serviceItem, image_path=u''):
        """
        Store the serviceItem and build the new HTML from it. Add the
        HTML to the display
        """
        log.debug(u'buildHtml')
        self.webLoaded = False
        self.initialFrame = None
        self.serviceItem = serviceItem
        background = None
        # We have an image override so keep the image till the theme changes.
        if self.override:
            # We have an video override so allow it to be stopped.
            if u'video' in self.override:
                Registry().execute(u'video_background_replaced')
                self.override = {}
            # We have a different theme.
            elif self.override[u'theme'] != serviceItem.themedata.background_filename:
                Registry().execute(u'live_theme_changed')
                self.override = {}
            else:
                # replace the background
                background = self.image_manager.get_image_bytes(self.override[u'image'], ImageSource.ImagePlugin)
        self.setTransparency(self.serviceItem.themedata.background_type ==
            BackgroundType.to_string(BackgroundType.Transparent))
        if self.serviceItem.themedata.background_filename:
            self.serviceItem.bg_image_bytes = self.image_manager.get_image_bytes(
                self.serviceItem.themedata.background_filename,
                ImageSource.Theme
            )
        if image_path:
            image_bytes = self.image_manager.get_image_bytes(image_path, ImageSource.ImagePlugin)
        else:
            image_bytes = None
        html = build_html(self.serviceItem, self.screen, self.isLive, background, image_bytes,
            plugins=self.plugin_manager.plugins)
        log.debug(u'buildHtml - pre setHtml')
        self.webView.setHtml(html)
        log.debug(u'buildHtml - post setHtml')
        if serviceItem.foot_text:
            self.footer(serviceItem.foot_text)
        # if was hidden keep it hidden
        if self.hideMode and self.isLive and not serviceItem.is_media():
            if Settings().value(u'general/auto unblank'):
                Registry().execute(u'slidecontroller_live_unblank')
            else:
                self.hide_display(self.hideMode)
        self.__hideMouse()

    def footer(self, text):
        """
        Display the Footer
        """
        log.debug(u'footer')
        js = u'show_footer(\'' + text.replace(u'\\', u'\\\\').replace(u'\'', u'\\\'') + u'\')'
        self.frame.evaluateJavaScript(js)

    def hide_display(self, mode=HideMode.Screen):
        """
        Hide the display by making all layers transparent
        Store the images so they can be replaced when required
        """
        log.debug(u'hide_display mode = %d', mode)
        if self.screens.display_count == 1:
            # Only make visible if setting enabled.
            if not Settings().value(u'general/display on monitor'):
                return
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
                self.webView.setVisible(True)
        self.hideMode = mode

    def show_display(self):
        """
        Show the stored layers so the screen reappears as it was
        originally.
        Make the stored images None to release memory.
        """
        log.debug(u'show_display')
        if self.screens.display_count == 1:
            # Only make visible if setting enabled.
            if not Settings().value(u'general/display on monitor'):
                return
        self.frame.evaluateJavaScript('show_blank("show");')
        if self.isHidden():
            self.setVisible(True)
        self.hideMode = None
        # Trigger actions when display is active again.
        if self.isLive:
            Registry().execute(u'live_display_active')

    def __hideMouse(self):
        """
        Hide mouse cursor when moved over display.
        """
        if Settings().value(u'advanced/hide mouse'):
            self.setCursor(QtCore.Qt.BlankCursor)
            self.frame.evaluateJavaScript('document.body.style.cursor = "none"')
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.frame.evaluateJavaScript('document.body.style.cursor = "auto"')

    def _get_plugin_manager(self):
        """
        Adds the Renderer to the class dynamically
        """
        if not hasattr(self, u'_plugin_manager'):
            self._plugin_manager = Registry().get(u'plugin_manager')
        return self._plugin_manager

    plugin_manager = property(_get_plugin_manager)

    def _get_image_manager(self):
        """
        Adds the image manager to the class dynamically
        """
        if not hasattr(self, u'_image_manager'):
            self._image_manager = Registry().get(u'image_manager')
        return self._image_manager

    image_manager = property(_get_image_manager)

    def _get_application(self):
        """
        Adds the openlp to the class dynamically
        """
        if not hasattr(self, u'_application'):
            self._application = Registry().get(u'application')
        return self._application

    application = property(_get_application)


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
        """
        log.debug(u'AudioPlayer Initialisation started')
        QtCore.QObject.__init__(self, parent)
        self.currentIndex = -1
        self.playlist = []
        self.repeat = False
        self.mediaObject = Phonon.MediaObject()
        self.mediaObject.setTickInterval(100)
        self.audioObject = Phonon.AudioOutput(Phonon.VideoCategory)
        Phonon.createPath(self.mediaObject, self.audioObject)
        QtCore.QObject.connect(self.mediaObject, QtCore.SIGNAL(u'aboutToFinish()'), self.onAboutToFinish)
        QtCore.QObject.connect(self.mediaObject, QtCore.SIGNAL(u'finished()'), self.onFinished)

    def __del__(self):
        """
        Shutting down so clean up connections
        """
        self.stop()
        for path in self.mediaObject.outputPaths():
            path.disconnect()

    def onAboutToFinish(self):
        """
        Just before the audio player finishes the current track, queue the next
        item in the playlist, if there is one.
        """
        self.currentIndex += 1
        if len(self.playlist) > self.currentIndex:
            self.mediaObject.enqueue(self.playlist[self.currentIndex])

    def onFinished(self):
        """
        When the audio track finishes.
        """
        if self.repeat:
            log.debug(u'Repeat is enabled... here we go again!')
            self.mediaObject.clearQueue()
            self.mediaObject.clear()
            self.currentIndex = -1
            self.play()

    def connectVolumeSlider(self, slider):
        """
        Connect the volume slider to the output channel.
        """
        slider.setAudioOutput(self.audioObject)

    def reset(self):
        """
        Reset the audio player, clearing the playlist and the queue.
        """
        self.currentIndex = -1
        self.playlist = []
        self.stop()
        self.mediaObject.clear()

    def play(self):
        """
        We want to play the file so start it
        """
        log.debug(u'AudioPlayer.play() called')
        if self.currentIndex == -1:
            self.onAboutToFinish()
        self.mediaObject.play()

    def pause(self):
        """
        Pause the Audio
        """
        log.debug(u'AudioPlayer.pause() called')
        self.mediaObject.pause()

    def stop(self):
        """
        Stop the Audio and clean up
        """
        log.debug(u'AudioPlayer.stop() called')
        self.mediaObject.stop()

    def addToPlaylist(self, filenames):
        """
        Add another file to the playlist.

        ``filenames``
            A list with files to be added to the playlist.
        """
        if not isinstance(filenames, list):
            filenames = [filenames]
        self.playlist.extend(map(Phonon.MediaSource, filenames))

    def next(self):
        """
        Skip forward to the next track in the list
        """
        if not self.repeat and self.currentIndex + 1 >= len(self.playlist):
            return
        isPlaying = self.mediaObject.state() == Phonon.PlayingState
        self.currentIndex += 1
        if self.repeat and self.currentIndex == len(self.playlist):
            self.currentIndex = 0
        self.mediaObject.clearQueue()
        self.mediaObject.clear()
        self.mediaObject.enqueue(self.playlist[self.currentIndex])
        if isPlaying:
            self.mediaObject.play()

    def goTo(self, index):
        """
        Go to a particular track in the list
        """
        isPlaying = self.mediaObject.state() == Phonon.PlayingState
        self.mediaObject.clearQueue()
        self.mediaObject.clear()
        self.currentIndex = index
        self.mediaObject.enqueue(self.playlist[self.currentIndex])
        if isPlaying:
            self.mediaObject.play()

    #@todo is this used?
    def connectSlot(self, signal, slot):
        """
        Connect a slot to a signal on the media object
        """
        QtCore.QObject.connect(self.mediaObject, signal, slot)
