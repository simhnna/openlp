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

from PyQt4 import QtGui

from openlp.core.common import translate
from openlp.core.lib.ui import create_button_box


class Ui_AddGroupDialog(object):
    def setupUi(self, add_group_dialog):
        add_group_dialog.setObjectName('add_group_dialog')
        add_group_dialog.resize(300, 10)
        self.dialog_layout = QtGui.QVBoxLayout(add_group_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.name_layout = QtGui.QFormLayout()
        self.name_layout.setObjectName('name_layout')
        self.parent_group_label = QtGui.QLabel(add_group_dialog)
        self.parent_group_label.setObjectName('parent_group_label')
        self.parent_group_combobox = QtGui.QComboBox(add_group_dialog)
        self.parent_group_combobox.setObjectName('parent_group_combobox')
        self.name_layout.addRow(self.parent_group_label, self.parent_group_combobox)
        self.name_label = QtGui.QLabel(add_group_dialog)
        self.name_label.setObjectName('name_label')
        self.name_edit = QtGui.QLineEdit(add_group_dialog)
        self.name_edit.setObjectName('name_edit')
        self.name_label.setBuddy(self.name_edit)
        self.name_layout.addRow(self.name_label, self.name_edit)
        self.dialog_layout.addLayout(self.name_layout)
        self.button_box = create_button_box(add_group_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(add_group_dialog)
        add_group_dialog.setMaximumHeight(add_group_dialog.sizeHint().height())

    def retranslateUi(self, add_group_dialog):
        add_group_dialog.setWindowTitle(translate('ImagePlugin.AddGroupForm', 'Add group'))
        self.parent_group_label.setText(translate('ImagePlugin.AddGroupForm', 'Parent group:'))
        self.name_label.setText(translate('ImagePlugin.AddGroupForm', 'Group name:'))
