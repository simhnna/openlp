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

import logging

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Receiver, SettingsTab, translate

log = logging.getLogger(__name__)

class BiblesTab(SettingsTab):
    """
    BiblesTab is the Bibles settings tab in the settings dialog.
    """
    log.info(u'Bible Tab loaded')

    def __init__(self, title, visible_title):
        self.paragraph_style = True
        self.show_new_chapters = False
        self.display_style = 0
        SettingsTab.__init__(self, title, visible_title)

    def setupUi(self):
        self.setObjectName(u'BiblesTab')
        self.BibleLayout = QtGui.QHBoxLayout(self)
        self.BibleLayout.setObjectName(u'BibleLayout')
        self.LeftWidget = QtGui.QWidget(self)
        self.LeftWidget.setObjectName(u'LeftWidget')
        self.LeftLayout = QtGui.QVBoxLayout(self.LeftWidget)
        self.LeftLayout.setMargin(0)
        self.LeftLayout.setObjectName(u'LeftLayout')
        self.VerseDisplayGroupBox = QtGui.QGroupBox(self.LeftWidget)
        self.VerseDisplayGroupBox.setObjectName(u'VerseDisplayGroupBox')
        self.VerseDisplayLayout = QtGui.QFormLayout(self.VerseDisplayGroupBox)
        self.VerseDisplayLayout.setObjectName(u'VerseDisplayLayout')
        self.NewChaptersCheckBox = QtGui.QCheckBox(self.VerseDisplayGroupBox)
        self.NewChaptersCheckBox.setObjectName(u'NewChaptersCheckBox')
        self.VerseDisplayLayout.addRow(self.NewChaptersCheckBox)
        self.DisplayStyleLabel = QtGui.QLabel(self.VerseDisplayGroupBox)
        self.DisplayStyleLabel.setObjectName(u'DisplayStyleLabel')
        self.DisplayStyleComboBox = QtGui.QComboBox(self.VerseDisplayGroupBox)
        self.DisplayStyleComboBox.addItems([u'', u'', u'', u''])
        self.DisplayStyleComboBox.setObjectName(u'DisplayStyleComboBox')
        self.VerseDisplayLayout.addRow(self.DisplayStyleLabel,
            self.DisplayStyleComboBox)
        self.LayoutStyleLabel = QtGui.QLabel(self.VerseDisplayGroupBox)
        self.LayoutStyleLabel.setObjectName(u'LayoutStyleLabel')
        self.LayoutStyleComboBox = QtGui.QComboBox(self.VerseDisplayGroupBox)
        self.LayoutStyleComboBox.setObjectName(u'LayoutStyleComboBox')
        self.LayoutStyleComboBox.addItems([u'', u'', u''])
        self.VerseDisplayLayout.addRow(self.LayoutStyleLabel,
            self.LayoutStyleComboBox)
        self.BibleSecondCheckBox = QtGui.QCheckBox(self.VerseDisplayGroupBox)
        self.BibleSecondCheckBox.setObjectName(u'BibleSecondCheckBox')
        self.VerseDisplayLayout.addRow(self.BibleSecondCheckBox)
        self.BibleThemeLabel = QtGui.QLabel(self.VerseDisplayGroupBox)
        self.BibleThemeLabel.setObjectName(u'BibleThemeLabel')
        self.BibleThemeComboBox = QtGui.QComboBox(self.VerseDisplayGroupBox)
        self.BibleThemeComboBox.addItem(u'')
        self.BibleThemeComboBox.setObjectName(u'BibleThemeComboBox')
        self.VerseDisplayLayout.addRow(self.BibleThemeLabel,
            self.BibleThemeComboBox)
        self.ChangeNoteLabel = QtGui.QLabel(self.VerseDisplayGroupBox)
        self.ChangeNoteLabel.setWordWrap(True)
        self.ChangeNoteLabel.setObjectName(u'ChangeNoteLabel')
        self.VerseDisplayLayout.addRow(self.ChangeNoteLabel)
        self.LeftLayout.addWidget(self.VerseDisplayGroupBox)
        self.LeftLayout.addStretch()
        self.BibleLayout.addWidget(self.LeftWidget)
        self.RightWidget = QtGui.QWidget(self)
        self.RightWidget.setObjectName(u'RightWidget')
        self.RightLayout = QtGui.QVBoxLayout(self.RightWidget)
        self.RightLayout.setMargin(0)
        self.RightLayout.setObjectName(u'RightLayout')
        self.RightLayout.addStretch()
        self.BibleLayout.addWidget(self.RightWidget)
        # Signals and slots
        QtCore.QObject.connect(
            self.NewChaptersCheckBox, QtCore.SIGNAL(u'stateChanged(int)'),
            self.onNewChaptersCheckBoxChanged)
        QtCore.QObject.connect(
            self.DisplayStyleComboBox, QtCore.SIGNAL(u'activated(int)'),
            self.onDisplayStyleComboBoxChanged)
        QtCore.QObject.connect(
            self.BibleThemeComboBox, QtCore.SIGNAL(u'activated(int)'),
            self.onBibleThemeComboBoxChanged)
        QtCore.QObject.connect(
            self.LayoutStyleComboBox, QtCore.SIGNAL(u'activated(int)'),
            self.onLayoutStyleComboBoxChanged)
        QtCore.QObject.connect(
            self.BibleSecondCheckBox, QtCore.SIGNAL(u'stateChanged(int)'),
            self.onBibleSecondCheckBox)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'theme_update_list'), self.updateThemeList)

    def retranslateUi(self):
        self.VerseDisplayGroupBox.setTitle(
            translate('BiblesPlugin.BiblesTab', 'Verse Display'))
        self.NewChaptersCheckBox.setText(
            translate('BiblesPlugin.BiblesTab',
            'Only show new chapter numbers'))
        self.LayoutStyleLabel.setText(
            translate('BiblesPlugin.BiblesTab', 'Layout style:'))
        self.DisplayStyleLabel.setText(
            translate('BiblesPlugin.BiblesTab', 'Display style:'))
        self.BibleThemeLabel.setText(
            translate('BiblesPlugin.BiblesTab', 'Bible theme:'))
        self.LayoutStyleComboBox.setItemText(0,
            translate('BiblesPlugin.BiblesTab', 'Verse Per Slide'))
        self.LayoutStyleComboBox.setItemText(1,
            translate('BiblesPlugin.BiblesTab', 'Verse Per Line'))
        self.LayoutStyleComboBox.setItemText(2,
            translate('BiblesPlugin.BiblesTab', 'Continuous'))
        self.DisplayStyleComboBox.setItemText(0,
            translate('BiblesPlugin.BiblesTab', 'No Brackets'))
        self.DisplayStyleComboBox.setItemText(1,
            translate('BiblesPlugin.BiblesTab', '( And )'))
        self.DisplayStyleComboBox.setItemText(2,
            translate('BiblesPlugin.BiblesTab', '{ And }'))
        self.DisplayStyleComboBox.setItemText(3,
            translate('BiblesPlugin.BiblesTab', '[ And ]'))
        self.ChangeNoteLabel.setText(translate('BiblesPlugin.BiblesTab',
            'Note:\nChanges do not affect verses already in the service.'))
        self.BibleSecondCheckBox.setText(
            translate('BiblesPlugin.BiblesTab', 'Display second Bible verses'))

    def resizeEvent(self, event=None):
        """
        Resize the sides in two equal halves if the layout allows this.
        """
        if event:
            SettingsTab.resizeEvent(self, event)
        width = self.width() - self.BibleLayout.spacing() - \
            self.BibleLayout.contentsMargins().left() - \
            self.BibleLayout.contentsMargins().right()
        left_width = min(width - self.RightWidget.minimumSizeHint().width(),
            width / 2)
        left_width = max(left_width, self.LeftWidget.minimumSizeHint().width())
        self.LeftWidget.setMinimumWidth(left_width)

    def onBibleThemeComboBoxChanged(self):
        self.bible_theme = self.BibleThemeComboBox.currentText()

    def onDisplayStyleComboBoxChanged(self):
        self.display_style = self.DisplayStyleComboBox.currentIndex()

    def onLayoutStyleComboBoxChanged(self):
        self.layout_style = self.LayoutStyleComboBox.currentIndex()

    def onNewChaptersCheckBoxChanged(self, check_state):
        self.show_new_chapters = False
        # We have a set value convert to True/False.
        if check_state == QtCore.Qt.Checked:
            self.show_new_chapters = True

    def onBibleSecondCheckBox(self, check_state):
        self.second_bibles = False
        # We have a set value convert to True/False.
        if check_state == QtCore.Qt.Checked:
            self.second_bibles = True

    def load(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        self.show_new_chapters = settings.value(
            u'display new chapter', QtCore.QVariant(False)).toBool()
        self.display_style = settings.value(
            u'display brackets', QtCore.QVariant(0)).toInt()[0]
        self.layout_style = settings.value(
            u'verse layout style', QtCore.QVariant(0)).toInt()[0]
        self.bible_theme = unicode(
            settings.value(u'bible theme', QtCore.QVariant(u'')).toString())
        self.second_bibles = settings.value(
            u'second bibles', QtCore.QVariant(True)).toBool()
        self.NewChaptersCheckBox.setChecked(self.show_new_chapters)
        self.DisplayStyleComboBox.setCurrentIndex(self.display_style)
        self.LayoutStyleComboBox.setCurrentIndex(self.layout_style)
        self.BibleSecondCheckBox.setChecked(self.second_bibles)
        settings.endGroup()

    def save(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.settingsSection)
        settings.setValue(u'display new chapter',
            QtCore.QVariant(self.show_new_chapters))
        settings.setValue(u'display brackets',
            QtCore.QVariant(self.display_style))
        settings.setValue(u'verse layout style',
            QtCore.QVariant(self.layout_style))
        settings.setValue(u'second bibles', QtCore.QVariant(self.second_bibles))
        settings.setValue(u'bible theme', QtCore.QVariant(self.bible_theme))
        settings.endGroup()

    def updateThemeList(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed.

        ``theme_list``
            The list of available themes::

                [u'Bible Theme', u'Song Theme']
        """
        self.BibleThemeComboBox.clear()
        self.BibleThemeComboBox.addItem(u'')
        for theme in theme_list:
            self.BibleThemeComboBox.addItem(theme)
        index = self.BibleThemeComboBox.findText(
            unicode(self.bible_theme), QtCore.Qt.MatchExactly)
        if index == -1:
            # Not Found.
            index = 0
            self.bible_theme = u''
        self.BibleThemeComboBox.setCurrentIndex(index)
