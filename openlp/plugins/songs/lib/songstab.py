# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

from openlp.core.lib import SettingsTab, translate

class SongsTab(SettingsTab):
    """
    SongsTab is the Songs settings tab in the settings dialog.
    """
    def __init__(self, title):
        SettingsTab.__init__(self, title)

    def setupUi(self):
        self.setObjectName(u'SongsTab')
        self.tabTitleVisible = translate(u'SongsPlugin.SongsTab', u'Songs')
        self.SongsLayout = QtGui.QFormLayout(self)
        self.SongsLayout.setObjectName(u'SongsLayout')
        self.SongsModeGroupBox = QtGui.QGroupBox(self)
        self.SongsModeGroupBox.setObjectName(u'SongsModeGroupBox')
        self.SongsModeLayout = QtGui.QVBoxLayout(self.SongsModeGroupBox)
        self.SongsModeLayout.setSpacing(8)
        self.SongsModeLayout.setMargin(8)
        self.SongsModeLayout.setObjectName(u'SongsModeLayout')
        self.SearchAsTypeCheckBox = QtGui.QCheckBox(self.SongsModeGroupBox)
        self.SearchAsTypeCheckBox.setObjectName(u'SearchAsTypeCheckBox')
        self.SongsModeLayout.addWidget(self.SearchAsTypeCheckBox)
        self.SongBarActiveCheckBox = QtGui.QCheckBox(self.SongsModeGroupBox)
        self.SongBarActiveCheckBox.setObjectName(u'SearchAsTypeCheckBox')
        self.SongsModeLayout.addWidget(self.SongBarActiveCheckBox)
        self.SongsLayout.setWidget(
            0, QtGui.QFormLayout.LabelRole, self.SongsModeGroupBox)
        QtCore.QObject.connect(self.SearchAsTypeCheckBox,
            QtCore.SIGNAL(u'stateChanged(int)'),
            self.onSearchAsTypeCheckBoxChanged)
        QtCore.QObject.connect(self.SongBarActiveCheckBox,
            QtCore.SIGNAL(u'stateChanged(int)'),
            self.SongBarActiveCheckBoxChanged)

    def retranslateUi(self):
        self.SongsModeGroupBox.setTitle(
            translate(u'SongsPlugin.SongsTab', u'Songs Mode'))
        self.SearchAsTypeCheckBox.setText(
            translate(u'SongsPlugin.SongsTab', u'Enable search as you type'))
        self.SongBarActiveCheckBox.setText(
            translate(u'SongsPlugin.SongsTab', u'Display Verses on Live Tool bar'))

    def onSearchAsTypeCheckBoxChanged(self, check_state):
        self.song_search = False
        # we have a set value convert to True/False
        if check_state == QtCore.Qt.Checked:
            self.song_search = True

    def SongBarActiveCheckBoxChanged(self, check_state):
        self.song_bar = False
        # we have a set value convert to True/False
        if check_state == QtCore.Qt.Checked:
            self.song_bar = True

    def load(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        self.song_search = settings.value(
            u'search as type', QtCore.QVariant(False)).toBool()
        self.song_bar = settings.value(
            u'display songbar', QtCore.QVariant(True)).toBool()
        self.SearchAsTypeCheckBox.setChecked(self.song_search)
        self.SongBarActiveCheckBox.setChecked(self.song_bar)
        settings.endGroup()

    def save(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        settings.setValue(u'search as type', QtCore.QVariant(self.song_search))
        settings.setValue(u'display songbar', QtCore.QVariant(self.song_bar))
        settings.endGroup()
