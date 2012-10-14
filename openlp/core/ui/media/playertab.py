# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Edwin Lunando, Joshua Miller, Stevan Pettit,  #
# Andreas Preikschat, Mattias Põldaru, Christian Richter, Philip Ridout,      #
# Simon Scudder, Jeffrey Smith, Maikel Stuivenberg, Martin Thompson, Jon      #
# Tibble, Dave Warnock, Frode Woldsund                                        #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import SettingsTab, translate, Receiver
from openlp.core.lib.ui import UiStrings, create_button
from openlp.core.lib.settings import Settings
from openlp.core.ui.media import get_media_players, set_media_players
class MediaQCheckBox(QtGui.QCheckBox):
    """
    MediaQCheckBox adds an extra property, playerName to the QCheckBox class.
    """
    def setPlayerName(self, name):
        self.playerName = name


class PlayerTab(SettingsTab):
    """
    MediaTab is the Media settings tab in the settings dialog.
    """
    def __init__(self, parent, mainWindow):
        self.settingsForm = parent
        self.mainWindow = mainWindow
        self.mediaPlayers = mainWindow.mediaController.mediaPlayers
        self.savedUsedPlayers = None
        self.iconPath = u':/system/system_settings.png'
        player_translated = translate('OpenLP.PlayerTab', 'Players')
        SettingsTab.__init__(self, parent, u'Players', player_translated)

    def setupUi(self):
        self.setObjectName(u'MediaTab')
        SettingsTab.setupUi(self)
        self.bgColorGroupBox = QtGui.QGroupBox(self.leftColumn)
        self.bgColorGroupBox.setObjectName(u'FontGroupBox')
        self.formLayout = QtGui.QFormLayout(self.bgColorGroupBox)
        self.formLayout.setObjectName(u'FormLayout')
        self.colorLayout = QtGui.QHBoxLayout()
        self.backgroundColorLabel = QtGui.QLabel(self.bgColorGroupBox)
        self.backgroundColorLabel.setObjectName(u'BackgroundColorLabel')
        self.colorLayout.addWidget(self.backgroundColorLabel)
        self.backgroundColorButton = QtGui.QPushButton(self.bgColorGroupBox)
        self.backgroundColorButton.setObjectName(u'BackgroundColorButton')
        self.colorLayout.addWidget(self.backgroundColorButton)
        self.formLayout.addRow(self.colorLayout)
        self.informationLabel = QtGui.QLabel(self.bgColorGroupBox)
        self.informationLabel.setObjectName(u'InformationLabel')
        self.informationLabel.setWordWrap(True)
        self.formLayout.addRow(self.informationLabel)
        self.leftLayout.addWidget(self.bgColorGroupBox)
        self.leftLayout.addStretch()
        self.rightColumn.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.rightLayout.addStretch()

        self.mediaPlayerGroupBox = QtGui.QGroupBox(self.leftColumn)
        self.mediaPlayerGroupBox.setObjectName(u'mediaPlayerGroupBox')
        self.mediaPlayerLayout = QtGui.QVBoxLayout(self.mediaPlayerGroupBox)
        self.mediaPlayerLayout.setObjectName(u'mediaPlayerLayout')
        self.playerCheckBoxes = {}
        self.leftLayout.addWidget(self.mediaPlayerGroupBox)
        self.playerOrderGroupBox = QtGui.QGroupBox(self.leftColumn)
        self.playerOrderGroupBox.setObjectName(u'playerOrderGroupBox')
        self.playerOrderLayout = QtGui.QHBoxLayout(self.playerOrderGroupBox)
        self.playerOrderLayout.setObjectName(u'playerOrderLayout')
        self.playerOrderlistWidget = QtGui.QListWidget(
            self.playerOrderGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playerOrderlistWidget.\
        sizePolicy().hasHeightForWidth())
        self.playerOrderlistWidget.setSizePolicy(sizePolicy)
        self.playerOrderlistWidget.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.playerOrderlistWidget.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.playerOrderlistWidget.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)
        self.playerOrderlistWidget.setObjectName(u'playerOrderlistWidget')
        self.playerOrderLayout.addWidget(self.playerOrderlistWidget)
        self.orderingButtonLayout = QtGui.QVBoxLayout()
        self.orderingButtonLayout.setObjectName(u'orderingButtonLayout')
        self.orderingButtonLayout.addStretch(1)
        self.orderingUpButton = create_button(self, u'orderingUpButton',
            role=u'up', click=self.onUpButtonClicked)
        self.orderingDownButton = create_button(self, u'orderingDownButton',
            role=u'down', click=self.onDownButtonClicked)
        self.orderingButtonLayout.addWidget(self.orderingUpButton)
        self.orderingButtonLayout.addWidget(self.orderingDownButton)
        self.orderingButtonLayout.addStretch(1)
        self.playerOrderLayout.addLayout(self.orderingButtonLayout)
        self.leftLayout.addWidget(self.playerOrderGroupBox)
        self.leftLayout.addStretch()
        self.rightLayout.addStretch()
        # Signals and slots
        QtCore.QObject.connect(self.backgroundColorButton,
            QtCore.SIGNAL(u'clicked()'), self.onbackgroundColorButtonClicked)

    def retranslateUi(self):
        self.mediaPlayerGroupBox.setTitle(
            translate('OpenLP.PlayerTab', 'Available Media Players'))
        self.playerOrderGroupBox.setTitle(
            translate('OpenLP.PlayerTab', 'Player Search Order'))
        self.bgColorGroupBox.setTitle(
            translate('ImagesPlugin.ImageTab', 'Background Color'))
        self.backgroundColorLabel.setText(
            translate('ImagesPlugin.ImageTab', 'Default Color:'))
        self.informationLabel.setText(
            translate('ImagesPlugin.ImageTab', 'Visible background for images '
            'with aspect ratio different to screen.'))
        self.retranslatePlayers()

    def onbackgroundColorButtonClicked(self):
        new_color = QtGui.QColorDialog.getColor(
            QtGui.QColor(self.bg_color), self)
        if new_color.isValid():
            self.bg_color = new_color.name()
            self.backgroundColorButton.setStyleSheet(
                u'background-color: %s' % self.bg_color)

    def onPlayerCheckBoxChanged(self, check_state):
        player = self.sender().playerName
        if check_state == QtCore.Qt.Checked:
            if player not in self.usedPlayers:
                self.usedPlayers.append(player)
        else:
            if player in self.usedPlayers:
                self.usedPlayers.remove(player)
        self.updatePlayerList()

    def updatePlayerList(self):
        self.playerOrderlistWidget.clear()
        for player in self.usedPlayers:
            if player in self.playerCheckBoxes.keys():
                if len(self.usedPlayers) == 1:
                    # At least one media player has to stay active
                    self.playerCheckBoxes[u'%s' % player].setEnabled(False)
                else:
                    self.playerCheckBoxes[u'%s' % player].setEnabled(True)
                self.playerOrderlistWidget.addItem(
                    self.mediaPlayers[unicode(player)].original_name)

    def onUpButtonClicked(self):
        row = self.playerOrderlistWidget.currentRow()
        if row <= 0:
            return
        item = self.playerOrderlistWidget.takeItem(row)
        self.playerOrderlistWidget.insertItem(row - 1, item)
        self.playerOrderlistWidget.setCurrentRow(row - 1)
        self.usedPlayers.insert(row - 1, self.usedPlayers.pop(row))

    def onDownButtonClicked(self):
        row = self.playerOrderlistWidget.currentRow()
        if row == -1 or row > self.playerOrderlistWidget.count() - 1:
            return
        item = self.playerOrderlistWidget.takeItem(row)
        self.playerOrderlistWidget.insertItem(row + 1, item)
        self.playerOrderlistWidget.setCurrentRow(row + 1)
        self.usedPlayers.insert(row + 1, self.usedPlayers.pop(row))

    def load(self):
        if self.savedUsedPlayers:
            self.usedPlayers = self.savedUsedPlayers
        self.usedPlayers = get_media_players()[0]
        self.savedUsedPlayers = self.usedPlayers

        settings = Settings()
        settings.beginGroup(self.settingsSection)
        self.updatePlayerList()
        self.bg_color = unicode(settings.value(
            u'background color', QtCore.QVariant(u'#000000')).toString())
        self.initial_color = self.bg_color
        settings.endGroup()
        self.backgroundColorButton.setStyleSheet(
            u'background-color: %s' % self.bg_color)

    def save(self):
        player_string_changed = False
        settings = Settings()
        settings.beginGroup(self.settingsSection)
        settings.setValue(u'background color', QtCore.QVariant(self.bg_color))
        settings.endGroup()
        if self.initial_color != self.bg_color:
            Receiver.send_message(u'image_updated')
        old_players, override_player = get_media_players()
        if self.usedPlayers != old_players:
            # clean old Media stuff
            set_media_players(self.usedPlayers, override_player)
            player_string_changed = True
        if player_string_changed:
            self.settingsForm.resetSupportedSuffixes()
            Receiver.send_message(u'mediaitem_media_rebuild')
            Receiver.send_message(u'config_screen_changed')

    def postSetUp(self, postUpdate=False):
        """
        Late stup for players as the MediaController has to be initialised
        firest.
        """
        for key, player in self.mediaPlayers.iteritems():
            player = self.mediaPlayers[key]
            checkbox = MediaQCheckBox(self.mediaPlayerGroupBox)
            checkbox.setEnabled(player.available)
            checkbox.setObjectName(player.name + u'CheckBox')
            self.playerCheckBoxes[player.name] = checkbox
            QtCore.QObject.connect(checkbox,QtCore.SIGNAL(u'stateChanged(int)'),
                self.onPlayerCheckBoxChanged)
            self.mediaPlayerLayout.addWidget(checkbox)
            if player.available and player.name in self.usedPlayers:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        self.retranslatePlayers()

    def retranslatePlayers(self):
        """
        Translations for players is dependent on  their setup as well
         """
        for key in self.mediaPlayers:
            player = self.mediaPlayers[key]
            checkbox = self.playerCheckBoxes[player.name]
            checkbox.setPlayerName(player.name)
            if player.available:
                checkbox.setText(player.display_name)
            else:
                checkbox.setText(
                    unicode(translate('OpenLP.PlayerTab',
                        '%s (unavailable)')) % player.display_name)