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

from openlp.core.lib import SettingsTab, Receiver, ThemeLevel

class ThemesTab(SettingsTab):
    """
    ThemesTab is the theme settings tab in the settings dialog.
    """
    def __init__(self, parent):
        self.parent = parent
        SettingsTab.__init__(self, u'Themes')

    def setupUi(self):
        self.setObjectName(u'ThemesTab')
        self.tabTitleVisible = self.trUtf8('Themes')
        self.ThemesTabLayout = QtGui.QHBoxLayout(self)
        self.ThemesTabLayout.setSpacing(8)
        self.ThemesTabLayout.setMargin(8)
        self.ThemesTabLayout.setObjectName(u'ThemesTabLayout')
        self.GlobalGroupBox = QtGui.QGroupBox(self)
        self.GlobalGroupBox.setObjectName(u'GlobalGroupBox')
        self.GlobalGroupBoxLayout = QtGui.QVBoxLayout(self.GlobalGroupBox)
        self.GlobalGroupBoxLayout.setSpacing(8)
        self.GlobalGroupBoxLayout.setMargin(8)
        self.GlobalGroupBoxLayout.setObjectName(u'GlobalGroupBoxLayout')
        self.DefaultComboBox = QtGui.QComboBox(self.GlobalGroupBox)
        self.DefaultComboBox.setObjectName(u'DefaultComboBox')
        self.GlobalGroupBoxLayout.addWidget(self.DefaultComboBox)
        self.DefaultListView = QtGui.QLabel(self.GlobalGroupBox)
        self.DefaultListView.setObjectName(u'DefaultListView')
        self.GlobalGroupBoxLayout.addWidget(self.DefaultListView)
        self.ThemesTabLayout.addWidget(self.GlobalGroupBox)
        self.LevelGroupBox = QtGui.QGroupBox(self)
        self.LevelGroupBox.setObjectName(u'LevelGroupBox')
        self.LevelLayout = QtGui.QFormLayout(self.LevelGroupBox)
        self.LevelLayout.setLabelAlignment(
            QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.LevelLayout.setFormAlignment(
            QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.LevelLayout.setMargin(8)
        self.LevelLayout.setSpacing(8)
        self.LevelLayout.setObjectName(u'LevelLayout')
        self.SongLevelRadioButton = QtGui.QRadioButton(self.LevelGroupBox)
        self.SongLevelRadioButton.setObjectName(u'SongLevelRadioButton')
        self.LevelLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.SongLevelRadioButton)
        self.SongLevelLabel = QtGui.QLabel(self.LevelGroupBox)
        self.SongLevelLabel.setWordWrap(True)
        self.SongLevelLabel.setObjectName(u'SongLevelLabel')
        self.LevelLayout.setWidget(0, QtGui.QFormLayout.FieldRole,
            self.SongLevelLabel)
        self.ServiceLevelRadioButton = QtGui.QRadioButton(self.LevelGroupBox)
        self.ServiceLevelRadioButton.setObjectName(u'ServiceLevelRadioButton')
        self.LevelLayout.setWidget(1, QtGui.QFormLayout.LabelRole,
            self.ServiceLevelRadioButton)
        self.ServiceLevelLabel = QtGui.QLabel(self.LevelGroupBox)
        self.ServiceLevelLabel.setWordWrap(True)
        self.ServiceLevelLabel.setObjectName(u'ServiceLevelLabel')
        self.LevelLayout.setWidget(1, QtGui.QFormLayout.FieldRole,
            self.ServiceLevelLabel)
        self.GlobalLevelRadioButton = QtGui.QRadioButton(self.LevelGroupBox)
        self.GlobalLevelRadioButton.setChecked(True)
        self.GlobalLevelRadioButton.setObjectName(u'GlobalLevelRadioButton')
        self.LevelLayout.setWidget(2, QtGui.QFormLayout.LabelRole,
            self.GlobalLevelRadioButton)
        self.GlobalLevelLabel = QtGui.QLabel(self.LevelGroupBox)
        self.GlobalLevelLabel.setWordWrap(True)
        self.GlobalLevelLabel.setObjectName(u'GlobalLevelLabel')
        self.LevelLayout.setWidget(2, QtGui.QFormLayout.FieldRole,
            self.GlobalLevelLabel)
        self.ThemesTabLayout.addWidget(self.LevelGroupBox)
        QtCore.QObject.connect(self.SongLevelRadioButton,
            QtCore.SIGNAL(u'pressed()'), self.onSongLevelButtonPressed)
        QtCore.QObject.connect(self.ServiceLevelRadioButton,
            QtCore.SIGNAL(u'pressed()'), self.onServiceLevelButtonPressed)
        QtCore.QObject.connect(self.GlobalLevelRadioButton,
            QtCore.SIGNAL(u'pressed()'), self.onGlobalLevelButtonPressed)
        QtCore.QObject.connect(self.DefaultComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.onDefaultComboBoxChanged)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'theme_update_list'), self.updateThemeList)

    def retranslateUi(self):
        self.GlobalGroupBox.setTitle(self.trUtf8('Global theme'))
        self.LevelGroupBox.setTitle(self.trUtf8('Theme level'))
        self.SongLevelRadioButton.setText(self.trUtf8('Song level'))
        self.SongLevelLabel.setText(self.trUtf8('Use the theme from each song '
            'in the database. If a song doesn\'t have a theme associated with '
            'it, then use the service\'s theme. If the service doesn\'t have '
            'a theme, then use the global theme.'))
        self.ServiceLevelRadioButton.setText(self.trUtf8('Service level'))
        self.ServiceLevelLabel.setText(self.trUtf8('Use the theme from the '
            'service, overriding any of the individual songs\' themes. If the '
            'service doesn\'t have a theme, then use the global theme.'))
        self.GlobalLevelRadioButton.setText(self.trUtf8('Global level'))
        self.GlobalLevelLabel.setText(self.trUtf8('Use the global theme, '
            'overriding any themes associated with either the service or the '
            'songs.'))

    def load(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        self.theme_level = settings.value(
            u'theme level', QtCore.QVariant(ThemeLevel.Global)).toInt()[0]
        self.global_theme = unicode(settings.value(
            u'global theme', QtCore.QVariant(u'')).toString())
        settings.endGroup()
        if self.theme_level == ThemeLevel.Global:
            self.GlobalLevelRadioButton.setChecked(True)
        elif self.theme_level == ThemeLevel.Service:
            self.ServiceLevelRadioButton.setChecked(True)
        else:
            self.SongLevelRadioButton.setChecked(True)

    def save(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        settings.setValue(u'theme level',
            QtCore.QVariant(self.theme_level))
        settings.setValue(u'global theme',
            QtCore.QVariant(self.global_theme))
        settings.endGroup()
        Receiver.send_message(u'theme_update_global', self.global_theme)
        self.parent.RenderManager.set_global_theme(
            self.global_theme, self.theme_level)

    def postSetUp(self):
        Receiver.send_message(u'theme_update_global', self.global_theme)

    def onSongLevelButtonPressed(self):
        self.theme_level = ThemeLevel.Song

    def onServiceLevelButtonPressed(self):
        self.theme_level = ThemeLevel.Service

    def onGlobalLevelButtonPressed(self):
        self.theme_level = ThemeLevel.Global

    def onDefaultComboBoxChanged(self, value):
        self.global_theme = unicode(self.DefaultComboBox.currentText())
        self.parent.RenderManager.set_global_theme(
            self.global_theme, self.theme_level)
        image = self.parent.ThemeManagerContents.getPreviewImage(
            self.global_theme)
        preview = QtGui.QPixmap(unicode(image))
        if not preview.isNull():
            preview = preview.scaled(300, 255, QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)
        self.DefaultListView.setPixmap(preview)

    def updateThemeList(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed
        """
        #reload as may have been triggered by the ThemeManager
        self.global_theme = unicode(QtCore.QSettings().value(
            self.settingsSection + u'/global theme',
            QtCore.QVariant(u'')).toString())
        self.DefaultComboBox.clear()
        for theme in theme_list:
            self.DefaultComboBox.addItem(theme)
        id = self.DefaultComboBox.findText(
            self.global_theme, QtCore.Qt.MatchExactly)
        if id == -1:
            id = 0 # Not Found
            self.global_theme = u''
        self.DefaultComboBox.setCurrentIndex(id)
        self.parent.RenderManager.set_global_theme(
            self.global_theme, self.theme_level)
        if self.global_theme is not u'':
            image = self.parent.ThemeManagerContents.getPreviewImage(
                self.global_theme)
            preview = QtGui.QPixmap(unicode(image))
            if not preview.isNull():
                preview = preview.scaled(300, 255, QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation)
            self.DefaultListView.setPixmap(preview)
