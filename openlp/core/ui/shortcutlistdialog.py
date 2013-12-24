# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
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
The list of shortcuts within a dialog.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class CaptureShortcutButton(QtGui.QPushButton):
    """
    A class to encapsulate a ``QPushButton``.
    """
    def __init__(self, *args):
        """
        Constructor
        """
        super(CaptureShortcutButton, self).__init__(*args)
        self.setCheckable(True)

    def keyPressEvent(self, event):
        """
        Block the ``Key_Space`` key, so that the button will not change the
        checked state.
        """
        if event.key() == QtCore.Qt.Key_Space and self.isChecked():
            # Ignore the event, so that the parent can take care of this.
            event.ignore()


class Ui_ShortcutListDialog(object):
    """
    The UI widgets for the shortcut dialog.
    """
    def setupUi(self, shortcutListDialog):
        """
        Set up the UI
        """
        shortcutListDialog.setObjectName('shortcutListDialog')
        shortcutListDialog.resize(500, 438)
        self.shortcutListLayout = QtGui.QVBoxLayout(shortcutListDialog)
        self.shortcutListLayout.setObjectName('shortcutListLayout')
        self.description_label = QtGui.QLabel(shortcutListDialog)
        self.description_label.setObjectName('description_label')
        self.description_label.setWordWrap(True)
        self.shortcutListLayout.addWidget(self.description_label)
        self.treeWidget = QtGui.QTreeWidget(shortcutListDialog)
        self.treeWidget.setObjectName('treeWidget')
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setColumnWidth(0, 250)
        self.shortcutListLayout.addWidget(self.treeWidget)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsLayout.setObjectName('detailsLayout')
        self.detailsLayout.setContentsMargins(-1, 0, -1, -1)
        self.defaultRadioButton = QtGui.QRadioButton(shortcutListDialog)
        self.defaultRadioButton.setObjectName('defaultRadioButton')
        self.defaultRadioButton.setChecked(True)
        self.detailsLayout.addWidget(self.defaultRadioButton, 0, 0, 1, 1)
        self.customRadioButton = QtGui.QRadioButton(shortcutListDialog)
        self.customRadioButton.setObjectName('customRadioButton')
        self.detailsLayout.addWidget(self.customRadioButton, 1, 0, 1, 1)
        self.primaryLayout = QtGui.QHBoxLayout()
        self.primaryLayout.setObjectName('primaryLayout')
        self.primaryPushButton = CaptureShortcutButton(shortcutListDialog)
        self.primaryPushButton.setObjectName('primaryPushButton')
        self.primaryPushButton.setMinimumSize(QtCore.QSize(84, 0))
        self.primaryPushButton.setIcon(build_icon(':/system/system_configure_shortcuts.png'))
        self.primaryLayout.addWidget(self.primaryPushButton)
        self.clearPrimaryButton = QtGui.QToolButton(shortcutListDialog)
        self.clearPrimaryButton.setObjectName('clearPrimaryButton')
        self.clearPrimaryButton.setMinimumSize(QtCore.QSize(0, 16))
        self.clearPrimaryButton.setIcon(build_icon(':/system/clear_shortcut.png'))
        self.primaryLayout.addWidget(self.clearPrimaryButton)
        self.detailsLayout.addLayout(self.primaryLayout, 1, 1, 1, 1)
        self.alternateLayout = QtGui.QHBoxLayout()
        self.alternateLayout.setObjectName('alternateLayout')
        self.alternatePushButton = CaptureShortcutButton(shortcutListDialog)
        self.alternatePushButton.setObjectName('alternatePushButton')
        self.alternatePushButton.setIcon(build_icon(':/system/system_configure_shortcuts.png'))
        self.alternateLayout.addWidget(self.alternatePushButton)
        self.clearAlternateButton = QtGui.QToolButton(shortcutListDialog)
        self.clearAlternateButton.setObjectName('clearAlternateButton')
        self.clearAlternateButton.setIcon(build_icon(':/system/clear_shortcut.png'))
        self.alternateLayout.addWidget(self.clearAlternateButton)
        self.detailsLayout.addLayout(self.alternateLayout, 1, 2, 1, 1)
        self.primaryLabel = QtGui.QLabel(shortcutListDialog)
        self.primaryLabel.setObjectName('primaryLabel')
        self.detailsLayout.addWidget(self.primaryLabel, 0, 1, 1, 1)
        self.alternateLabel = QtGui.QLabel(shortcutListDialog)
        self.alternateLabel.setObjectName('alternateLabel')
        self.detailsLayout.addWidget(self.alternateLabel, 0, 2, 1, 1)
        self.shortcutListLayout.addLayout(self.detailsLayout)
        self.button_box = create_button_box(shortcutListDialog, 'button_box', ['cancel', 'ok', 'defaults'])
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.shortcutListLayout.addWidget(self.button_box)
        self.retranslateUi(shortcutListDialog)

    def retranslateUi(self, shortcutListDialog):
        """
        Translate the UI on the fly
        """
        shortcutListDialog.setWindowTitle(translate('OpenLP.ShortcutListDialog', 'Configure Shortcuts'))
        self.description_label.setText(
            translate('OpenLP.ShortcutListDialog', 'Select an action and click one of the buttons below to start '
                'capturing a new primary or alternate shortcut, respectively.'))
        self.treeWidget.setHeaderLabels([translate('OpenLP.ShortcutListDialog', 'Action'),
            translate('OpenLP.ShortcutListDialog', 'Shortcut'),
            translate('OpenLP.ShortcutListDialog', 'Alternate')])
        self.defaultRadioButton.setText(translate('OpenLP.ShortcutListDialog', 'Default'))
        self.customRadioButton.setText(translate('OpenLP.ShortcutListDialog', 'Custom'))
        self.primaryPushButton.setToolTip(translate('OpenLP.ShortcutListDialog', 'Capture shortcut.'))
        self.alternatePushButton.setToolTip(translate('OpenLP.ShortcutListDialog', 'Capture shortcut.'))
        self.clearPrimaryButton.setToolTip(translate('OpenLP.ShortcutListDialog',
            'Restore the default shortcut of this action.'))
        self.clearAlternateButton.setToolTip(translate('OpenLP.ShortcutListDialog',
            'Restore the default shortcut of this action.'))
