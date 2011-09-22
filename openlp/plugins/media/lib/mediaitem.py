# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,    #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund             #
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

import logging
import os
import locale

from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

from openlp.core.lib import MediaManagerItem, build_icon, ItemCapabilities, \
    SettingsManager, translate, check_item_selected, Receiver, MediaType
from openlp.core.lib.ui import UiStrings, critical_error_message_box, \
    media_item_combo_box
from openlp.core.ui import Controller, Display
from openlp.plugins.media.forms import MediaOpenForm

log = logging.getLogger(__name__)

CLAPPERBOARD = QtGui.QPixmap(u':/media/media_video.png').toImage()

class MediaMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Media Slides.
    """
    log.info(u'%s MediaMediaItem loaded', __name__)

    def __init__(self, parent, plugin, icon):
        self.iconPath = u'images/image'
        self.background = False
        self.PreviewFunction = CLAPPERBOARD
        self.Automatic = u''
        MediaManagerItem.__init__(self, parent, plugin, icon)
        self.singleServiceItem = False
        self.mediaOpenForm = MediaOpenForm(self.plugin.formparent)
        self.hasSearch = True
        self.mediaObject = None
        self.mediaController = Controller(parent)
        self.mediaController.controllerLayout = QtGui.QVBoxLayout()
        self.plugin.mediaController.add_controller_items(self.mediaController, \
            self.mediaController.controllerLayout)
        self.plugin.mediaController.set_controls_visible(self.mediaController, \
            False)
        self.mediaController.previewDisplay = Display(self.mediaController, \
            False, self.mediaController, self.plugin.pluginManager.plugins)
        self.mediaController.previewDisplay.setup()
        self.plugin.mediaController.setup_display( \
            self.mediaController.previewDisplay)
        self.mediaController.previewDisplay.hide()

        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'video_background_replaced'),
            self.videobackgroundReplaced)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'mediaitem_media_rebuild'), self.rebuild)
        # Allow DnD from the desktop
        self.listView.activateDnD()

    def retranslateUi(self):
        self.onNewPrompt = translate('MediaPlugin.MediaItem', 'Select Media')
        self.onNewFileMasks = unicode(translate('MediaPlugin.MediaItem',
            'Videos (%s);;Audio (%s);;%s (*)')) % (
            u' '.join(self.plugin.video_extensions_list),
            u' '.join(self.plugin.audio_extensions_list), UiStrings().AllFiles)
        self.replaceAction.setText(UiStrings().ReplaceBG)
        self.replaceAction.setToolTip(UiStrings().ReplaceLiveBG)
        self.resetAction.setText(UiStrings().ResetBG)
        self.resetAction.setToolTip(UiStrings().ResetLiveBG)
        self.Automatic = translate('MediaPlugin.MediaItem',
            'Automatic')
        self.displayTypeLabel.setText(
            translate('MediaPlugin.MediaItem', 'Use Api:'))

    def requiredIcons(self):
        MediaManagerItem.requiredIcons(self)
        self.hasFileIcon = True
        apiSettings = str(QtCore.QSettings().value(u'media/apis',
            QtCore.QVariant(u'Webkit')).toString())
        usedAPIs = apiSettings.split(u',')
        for title in usedAPIs:
            api = self.plugin.mediaController.APIs[title]
        self.hasNewIcon = False
        self.hasEditIcon = False

    def addListViewToToolBar(self):
        MediaManagerItem.addListViewToToolBar(self)
        self.listView.addAction(self.replaceAction)

# TODO activate own media open menu
#    def addStartHeaderBar(self):
#        self.replaceAction = self.addToolbarButton(u'', u'',
#            u':/general/general_open.png', self.onMediaOpenClick, False)

    def addEndHeaderBar(self):
        # Replace backgrounds do not work at present so remove functionality.
        self.replaceAction = self.addToolbarButton(u'', u'',
            u':/slides/slide_blank.png', self.onReplaceClick, False)
        self.resetAction = self.addToolbarButton(u'', u'',
            u':/system/system_close.png', self.onResetClick, False)
        self.resetAction.setVisible(False)
        self.mediaWidget = QtGui.QWidget(self)
        self.mediaWidget.setObjectName(u'mediaWidget')
        self.displayLayout = QtGui.QFormLayout(self.mediaWidget)
        self.displayLayout.setMargin(self.displayLayout.spacing())
        self.displayLayout.setObjectName(u'displayLayout')
        self.displayTypeLabel = QtGui.QLabel(self.mediaWidget)
        self.displayTypeLabel.setObjectName(u'displayTypeLabel')
        self.displayTypeComboBox = media_item_combo_box(
            self.mediaWidget, u'displayTypeComboBox')
        self.displayTypeLabel.setBuddy(self.displayTypeComboBox)
        self.displayLayout.addRow(self.displayTypeLabel,
            self.displayTypeComboBox)
        # Add the Media widget to the page layout
        self.pageLayout.addWidget(self.mediaWidget)
        QtCore.QObject.connect(self.displayTypeComboBox,
            QtCore.SIGNAL(u'currentIndexChanged (int)'), self.overrideApiChanged)

    def onMediaOpenClick(self):
        """
        Add a folder to the list widget to make it available for showing
        """
        self.mediaOpenForm.exec_()
#        folder = QtGui.QFileDialog.getExistingDirectory (
#            self, self.onNewPrompt,
#            SettingsManager.get_last_dir(self.settingsSection))
#        log.info(u'New folder(s) %s', unicode(folder))

    def overrideApiChanged(self, index):
        Receiver.send_message(u'media_overrideApi', \
            u'%s' % self.displayTypeComboBox.currentText())

    def onResetClick(self):
        """
        Called to reset the Live background with the media selected,
        """
        self.plugin.liveController.mediaController.video_reset( \
            self.plugin.liveController)
        self.resetAction.setVisible(False)

    def videobackgroundReplaced(self):
        """
        Triggered by main display on change of serviceitem
        """
        self.resetAction.setVisible(False)

    def onReplaceClick(self):
        """
        Called to replace Live background with the media selected.
        """
        if check_item_selected(self.listView,
            translate('MediaPlugin.MediaItem',
            'You must select a media file to replace the background with.')):
            item = self.listView.currentItem()
            filename = unicode(item.data(QtCore.Qt.UserRole).toString())
            if os.path.exists(filename):
                if self.plugin.liveController.mediaController.video( \
                    self.plugin.liveController, filename, True, True):
                    self.resetAction.setVisible(True)
                else:
                    critical_error_message_box(UiStrings().LiveBGError,
                        translate('MediaPlugin.MediaItem',
                        'There was no display item to amend.'))
            else:
                critical_error_message_box(UiStrings().LiveBGError,
                    unicode(translate('MediaPlugin.MediaItem',
                    'There was a problem replacing your background, '
                    'the media file "%s" no longer exists.')) % filename)

    def generateSlideData(self, service_item, item=None, xmlVersion=False,
        remote=False):
        if item is None:
            item = self.listView.currentItem()
            if item is None:
                return False
        filename = unicode(item.data(QtCore.Qt.UserRole).toString())
        if not os.path.exists(filename):
            if not remote:
                # File is no longer present
                critical_error_message_box(
                    translate('MediaPlugin.MediaItem', 'Missing Media File'),
                        unicode(translate('MediaPlugin.MediaItem',
                            'The file %s no longer exists.')) % filename)
            return False
        self.mediaLength = 0
        if self.plugin.mediaController.video( \
                    self.mediaController, filename, False, False):
            self.mediaLength = self.mediaController.media_info.length
            service_item.media_length = self.mediaLength
            self.plugin.mediaController.video_reset(self.mediaController)
            if self.mediaLength > 0:
                service_item.add_capability(
                    ItemCapabilities.HasVariableStartTime)
        else:
            return False
        service_item.media_length = self.mediaLength
        service_item.title = unicode(self.plugin.nameStrings[u'singular'])
        service_item.add_capability(ItemCapabilities.RequiresMedia)
        # force a non-existent theme
        service_item.theme = -1
        frame = u':/media/image_clapperboard.png'
        (path, name) = os.path.split(filename)
        service_item.add_from_command(path, name, frame)
        return True

    def initialise(self):
        self.listView.clear()
        self.listView.setIconSize(QtCore.QSize(88, 50))
        self.loadList(SettingsManager.load_list(self.settingsSection, u'media'))
        self.populateDisplayTypes()

    def rebuild(self):
        """
        Rebuild the tab in the media manager when changes are made in
        the settings
        """
        self.populateDisplayTypes()

    def populateDisplayTypes(self):
        """
        Load the combobox with the enabled media apis,
        allowing user to select a specific api if settings allow
        """
        self.displayTypeComboBox.clear()
        apiSettings = str(QtCore.QSettings().value(u'media/apis',
            QtCore.QVariant(u'Webkit')).toString())
        usedAPIs = apiSettings.split(u',')
        for title in usedAPIs:
            # load the drop down selection
            self.displayTypeComboBox.addItem(title)
        if self.displayTypeComboBox.count() > 1:
            self.displayTypeComboBox.insertItem(0, self.Automatic)
            self.displayTypeComboBox.setCurrentIndex(0)
        if QtCore.QSettings().value(self.settingsSection + u'/override api',
            QtCore.QVariant(QtCore.Qt.Unchecked)) == QtCore.Qt.Checked:
            self.mediaWidget.show()
        else:
            self.mediaWidget.hide()


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
                u'media', self.getFileList())

    def loadList(self, media):
        # Sort the themes by its filename considering language specific
        # characters. lower() is needed for windows!
        media.sort(cmp=locale.strcoll,
            key=lambda filename: os.path.split(unicode(filename))[1].lower())
        for track in media:
            track_info = QtCore.QFileInfo(track)
            if not track_info.isFile():
                filename = os.path.split(unicode(track))[1]
                item_name = QtGui.QListWidgetItem(filename)
                item_name.setIcon(build_icon(CLAPPERBOARD))
                item_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(track))
            else:
                filename = os.path.split(unicode(track))[1]
                item_name = QtGui.QListWidgetItem(filename)
                #imageFile = u'F:/Computer/Platform/pythonDev/openlp/branches/media/media-optical-dvd-video.png'
                #thumbFile = u'F:/Computer/Platform/pythonDev/openlp/branches/media/media-optical-dvd-video_thumb.png'
                #icon = self.iconFromFile(imageFile, thumbFile)
                #item_name.setIcon(icon)
                item_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(track))
            item_name.setToolTip(track)
            self.listView.addItem(item_name)

    def getList(self, type=MediaType.Audio):
        media = SettingsManager.load_list(self.settingsSection, u'media')
        media.sort(cmp=locale.strcoll,
            key=lambda filename: os.path.split(unicode(filename))[1].lower())
        ext = []
        if type == MediaType.Audio:
            ext = self.plugin.audio_extensions_list
        else:
            ext = self.plugin.video_extensions_list
        ext = map(lambda x: x[1:], ext)
        media = filter(lambda x: os.path.splitext(x)[1] in ext, media)
        return media

    def search(self, string):
        files = SettingsManager.load_list(self.settingsSection, u'media')
        results = []
        string = string.lower()
        for file in files:
            filename = os.path.split(unicode(file))[1]
            if filename.lower().find(string) > -1:
                results.append([file, filename])
        return results
