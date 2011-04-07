# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan, Armin Köhler,        #
# Andreas Preikschat, Mattias Põldaru, Christian Richter, Philip Ridout,      #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import translate, build_icon

class Ui_ShortcutListDialog(object):
    def setupUi(self, shortcutListDialog):
        shortcutListDialog.setObjectName(u'shortcutListDialog')
        shortcutListDialog.resize(500, 438)
        self.shortcutListLayout = QtGui.QVBoxLayout(shortcutListDialog)
        self.shortcutListLayout.setObjectName(u'shortcutListLayout')
        self.treeWidget = QtGui.QTreeWidget(shortcutListDialog)
        self.treeWidget.setObjectName(u'treeWidget')
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setColumnCount(3)
        self.shortcutListLayout.addWidget(self.treeWidget)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsLayout.setObjectName(u'detailsLayout')
        self.detailsLayout.setContentsMargins(-1, 0, -1, -1)
        self.defaultRadioButton = QtGui.QRadioButton(shortcutListDialog)
        self.defaultRadioButton.setObjectName(u'defaultRadioButton')
        self.defaultRadioButton.setChecked(True)
        self.detailsLayout.addWidget(self.defaultRadioButton, 0, 0, 1, 1)
        self.customRadioButton = QtGui.QRadioButton(shortcutListDialog)
        self.customRadioButton.setObjectName(u'customRadioButton')
        self.detailsLayout.addWidget(self.customRadioButton, 1, 0, 1, 1)
        self.primaryLayout = QtGui.QHBoxLayout()
        self.primaryLayout.setObjectName(u'primaryLayout')
        self.primaryPushButton = QtGui.QPushButton(shortcutListDialog)
        self.primaryPushButton.setObjectName(u'primaryPushButton')
        self.primaryPushButton.setMinimumSize(QtCore.QSize(84, 0))
        self.primaryPushButton.setIcon(
            build_icon(u':/system/system_configure_shortcuts.png'))
        self.primaryPushButton.setCheckable(True)
        self.primaryLayout.addWidget(self.primaryPushButton)
        self.clearPrimaryButton = QtGui.QToolButton(shortcutListDialog)
        self.clearPrimaryButton.setObjectName(u'clearPrimaryButton')
        self.clearPrimaryButton.setMinimumSize(QtCore.QSize(0, 16))
        self.clearPrimaryButton.setIcon(
            build_icon(u':/system/clear_shortcut.png'))
        self.primaryLayout.addWidget(self.clearPrimaryButton)
        self.detailsLayout.addLayout(self.primaryLayout, 1, 1, 1, 1)
        self.alternateLayout = QtGui.QHBoxLayout()
        self.alternateLayout.setObjectName(u'alternateLayout')
        self.alternatePushButton = QtGui.QPushButton(shortcutListDialog)
        self.alternatePushButton.setObjectName(u'alternatePushButton')
        self.alternatePushButton.setCheckable(True)
        self.alternatePushButton.setIcon(
            build_icon(u':/system/system_configure_shortcuts.png'))
        self.alternateLayout.addWidget(self.alternatePushButton)
        self.clearAlternateButton = QtGui.QToolButton(shortcutListDialog)
        self.clearAlternateButton.setObjectName(u'clearAlternateButton')
        self.clearAlternateButton.setIcon(
            build_icon(u':/system/clear_shortcut.png'))
        self.alternateLayout.addWidget(self.clearAlternateButton)
        self.detailsLayout.addLayout(self.alternateLayout, 1, 2, 1, 1)
        self.primaryLabel = QtGui.QLabel(shortcutListDialog)
        self.primaryLabel.setObjectName(u'primaryLabel')
        self.detailsLayout.addWidget(self.primaryLabel, 0, 1, 1, 1)
        self.alternateLabel = QtGui.QLabel(shortcutListDialog)
        self.alternateLabel.setObjectName(u'alternateLabel')
        self.detailsLayout.addWidget(self.alternateLabel, 0, 2, 1, 1)
        self.shortcutListLayout.addLayout(self.detailsLayout)
        self.buttonBox = QtGui.QDialogButtonBox(shortcutListDialog)
        self.buttonBox.setObjectName(u'buttonBox')
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.RestoreDefaults)
        self.shortcutListLayout.addWidget(self.buttonBox)
        self.retranslateUi(shortcutListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(u'accepted()'),
            shortcutListDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(u'rejected()'),
            shortcutListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(shortcutListDialog)

    def retranslateUi(self, shortcutListDialog):
        shortcutListDialog.setWindowTitle(
            translate('OpenLP.ShortcutListDialog', 'Customize Shortcuts'))
        #self.descriptionLabel.setText(translate('OpenLP.ShortcutListDialog',
            #'Select an action and click the button below to start capturing '
            #'a new shortcut.'))
        self.treeWidget.setHeaderLabels([
            translate('OpenLP.ShortcutListDialog', 'Action'),
            translate('OpenLP.ShortcutListDialog', 'Shortcut'),
            translate('OpenLP.ShortcutListDialog', 'Alternate')])
        self.defaultRadioButton.setText(
            translate('OpenLP.ShortcutListDialog', 'Default'))
        self.customRadioButton.setText(
            translate('OpenLP.ShortcutListDialog', 'Custom'))
        self.primaryPushButton.setToolTip(
            translate('OpenLP.ShortcutListDialog', 'Capture shortcut.'))
        self.alternatePushButton.setToolTip(
            translate('OpenLP.ShortcutListDialog', 'Capture shortcut.'))
        self.clearPrimaryButton.setToolTip(
            translate('OpenLP.ShortcutListDialog',
            'Restore the default shortcut(s) of this action.'))
        self.clearAlternateButton.setToolTip(
            translate('OpenLP.ShortcutListDialog',
            'Restore the default shortcut(s) of this action.'))
