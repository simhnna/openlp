# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Armin Köhler, Andreas Preikschat,  #
# Christian Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon  #
# Tibble, Carsten Tinggaard, Frode Woldsund                                   #
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

from datetime import datetime
import logging
import os

from PyQt4 import QtCore, QtGui

from openlp.core.lib import MediaManagerItem, build_icon, ItemCapabilities, \
    SettingsManager, translate, check_item_selected, Receiver
from openlp.core.lib.ui import UiStrings, critical_error_message_box
from PyQt4.phonon import Phonon

log = logging.getLogger(__name__)

class MediaMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Media Slides.
    """
    log.info(u'%s MediaMediaItem loaded', __name__)

    def __init__(self, parent, plugin, icon):
        self.IconPath = u'images/image'
        self.background = False
        self.PreviewFunction = QtGui.QPixmap(
            u':/media/media_video.png').toImage()
        MediaManagerItem.__init__(self, parent, self, icon)
        self.singleServiceItem = False
        self.mediaObject = Phonon.MediaObject(self)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'video_background_replaced'),
            self.videobackgroundReplaced)
        QtCore.QObject.connect(self.mediaObject,
            QtCore.SIGNAL(u'stateChanged(Phonon::State, Phonon::State)'),
            self.videoStart)

    def retranslateUi(self):
        self.onNewPrompt = translate('MediaPlugin.MediaItem', 'Select Media')
        self.onNewFileMasks = unicode(translate('MediaPlugin.MediaItem',
            'Videos (%s);;Audio (%s);;%s (*)')) % (
            u' '.join(self.parent.video_extensions_list),
            u' '.join(self.parent.audio_extensions_list), UiStrings.AllFiles)
        self.replaceAction.setText(UiStrings.ReplaceBG)
        self.replaceAction.setToolTip(UiStrings.ReplaceLiveBG)
        self.resetAction.setText(UiStrings.ResetBG)
        self.resetAction.setToolTip(UiStrings.ResetLiveBG)

    def requiredIcons(self):
        MediaManagerItem.requiredIcons(self)
        self.hasFileIcon = True
        self.hasNewIcon = False
        self.hasEditIcon = False

    def addListViewToToolBar(self):
        MediaManagerItem.addListViewToToolBar(self)
        self.listView.addAction(self.replaceAction)

    def addEndHeaderBar(self):
        # Replace backgrounds do not work at present so remove functionality.
        self.replaceAction = self.addToolbarButton(u'', u'',
            u':/slides/slide_blank.png', self.onReplaceClick, False)
        self.resetAction = self.addToolbarButton(u'', u'',
            u':/system/system_close.png', self.onResetClick, False)
        self.resetAction.setVisible(False)

    def onResetClick(self):
        """
        Called to reset the Live backgound with the media selected,
        """
        self.resetAction.setVisible(False)
        self.parent.liveController.display.resetVideo()

    def videobackgroundReplaced(self):
        """
        Triggered by main display on change of serviceitem
        """
        self.resetAction.setVisible(False)

    def onReplaceClick(self):
        """
        Called to replace Live backgound with the media selected.
        """
        if check_item_selected(self.listView,
            translate('MediaPlugin.MediaItem',
            'You must select a media file to replace the background with.')):
            item = self.listView.currentItem()
            filename = unicode(item.data(QtCore.Qt.UserRole).toString())
            if os.path.exists(filename):
                (path, name) = os.path.split(filename)
                self.parent.liveController.display.video(filename, 0, True)
                self.resetAction.setVisible(True)
            else:
                critical_error_message_box(UiStrings.LiveBGError,
                    unicode(translate('MediaPlugin.MediaItem',
                    'There was a problem replacing your background, '
                    'the media file "%s" no longer exists.')) % filename)

    def generateSlideData(self, service_item, item=None, xmlVersion=False):
        if item is None:
            item = self.listView.currentItem()
            if item is None:
                return False
        filename = unicode(item.data(QtCore.Qt.UserRole).toString())
        if os.path.exists(filename):
            self.mediaState = None
            self.mediaObject.stop()
            self.mediaObject.clearQueue()
            self.mediaObject.setCurrentSource(Phonon.MediaSource(filename))
            self.mediaObject.play()
            service_item.title = unicode(self.plugin.nameStrings[u'singular'])
            service_item.add_capability(ItemCapabilities.RequiresMedia)
            # force a nonexistent theme
            service_item.theme = -1
            frame = u':/media/image_clapperboard.png'
            (path, name) = os.path.split(filename)
            file_size = os.path.getsize(filename)
            # File too big for processing
            if file_size <= 52428800: # 50MiB
                start = datetime.now()
                while not self.mediaState:
                    Receiver.send_message(u'openlp_process_events')
                    end = datetime.now()
                    tme = end - start
                    if tme.total_seconds() > 5:
                       break
                if self.mediaLength > 0:
                    service_item.media_length = self.mediaLength
                    service_item.add_capability(
                        ItemCapabilities.AllowsVariableStartTime)
            service_item.add_from_command(path, name, frame)
            return True
        else:
            # File is no longer present
            critical_error_message_box(
                translate('MediaPlugin.MediaItem', 'Missing Media File'),
                unicode(translate('MediaPlugin.MediaItem',
                'The file %s no longer exists.')) % filename)
            return False

    def initialise(self):
        self.listView.clear()
        self.listView.setIconSize(QtCore.QSize(88, 50))
        self.loadList(SettingsManager.load_list(self.settingsSection,
            self.settingsSection))

    def onDeleteClick(self):
        """
        Remove a media item from the list
        """
        if check_item_selected(self.listView, translate('MediaPlugin.MediaItem',
            'You must select a media file to delete.')):
            row_list = [item.row() for item in self.listView.selectedIndexes()]
            row_list.sort(reverse=True)
            for row in row_list:
                self.listView.takeItem(row)
            SettingsManager.set_list(self.settingsSection,
                self.settingsSection, self.getFileList())

    def loadList(self, list):
        for file in list:
            filename = os.path.split(unicode(file))[1]
            item_name = QtGui.QListWidgetItem(filename)
            img = QtGui.QPixmap(u':/media/media_video.png').toImage()
            item_name.setIcon(build_icon(img))
            item_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(file))
            self.listView.addItem(item_name)

    def videoStart(self, newState, oldState):
        """
        Start the video at a predetermined point.
        """
        if newState == Phonon.PlayingState:
            self.mediaState = newState
            self.mediaLength = self.mediaObject.totalTime()/1000
            self.mediaObject.stop()
