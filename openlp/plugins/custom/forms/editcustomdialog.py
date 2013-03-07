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

from PyQt4 import QtGui

from openlp.core.lib import UiStrings, build_icon, translate
from openlp.core.lib.ui import create_button_box, create_button


class Ui_CustomEditDialog(object):
    def setupUi(self, custom_edit_dialog):
        custom_edit_dialog.setObjectName(u'custom_edit_dialog')
        custom_edit_dialog.resize(450, 350)
        custom_edit_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo-16x16.png'))
        self.dialog_layout = QtGui.QVBoxLayout(custom_edit_dialog)
        self.dialog_layout.setObjectName(u'dialog_layout')
        self.title_layout = QtGui.QHBoxLayout()
        self.title_layout.setObjectName(u'title_layout')
        self.title_label = QtGui.QLabel(custom_edit_dialog)
        self.title_label.setObjectName(u'title_label')
        self.title_layout.addWidget(self.title_label)
        self.title_edit = QtGui.QLineEdit(custom_edit_dialog)
        self.title_label.setBuddy(self.title_edit)
        self.title_edit.setObjectName(u'title_edit')
        self.title_layout.addWidget(self.title_edit)
        self.dialog_layout.addLayout(self.title_layout)
        self.central_layout = QtGui.QHBoxLayout()
        self.central_layout.setObjectName(u'central_layout')
        self.slide_list_view = QtGui.QListWidget(custom_edit_dialog)
        self.slide_list_view.setAlternatingRowColors(True)
        self.slide_list_view.setObjectName(u'slide_list_view')
        self.central_layout.addWidget(self.slide_list_view)
        self.button_layout = QtGui.QVBoxLayout()
        self.button_layout.setObjectName(u'button_layout')
        self.add_button = QtGui.QPushButton(custom_edit_dialog)
        self.add_button.setObjectName(u'add_button')
        self.button_layout.addWidget(self.add_button)
        self.edit_button = QtGui.QPushButton(custom_edit_dialog)
        self.edit_button.setEnabled(False)
        self.edit_button.setObjectName(u'edit_button')
        self.button_layout.addWidget(self.edit_button)
        self.edit_all_button = QtGui.QPushButton(custom_edit_dialog)
        self.edit_all_button.setObjectName(u'edit_all_button')
        self.button_layout.addWidget(self.edit_all_button)
        self.delete_button = create_button(custom_edit_dialog, u'delete_button', role=u'delete',
            click=custom_edit_dialog.on_delete_button_clicked)
        self.delete_button.setEnabled(False)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()
        self.up_button = create_button(custom_edit_dialog, u'up_button', role=u'up', enabled=False,
            click=custom_edit_dialog.on_up_button_clicked)
        self.down_button = create_button(custom_edit_dialog, u'down_button', role=u'down', enabled=False,
            click=custom_edit_dialog.on_down_button_clicked)
        self.button_layout.addWidget(self.up_button)
        self.button_layout.addWidget(self.down_button)
        self.central_layout.addLayout(self.button_layout)
        self.dialog_layout.addLayout(self.central_layout)
        self.bottom_form_layout = QtGui.QFormLayout()
        self.bottom_form_layout.setObjectName(u'bottom_form_layout')
        self.theme_label = QtGui.QLabel(custom_edit_dialog)
        self.theme_label.setObjectName(u'theme_label')
        self.theme_combo_box = QtGui.QComboBox(custom_edit_dialog)
        self.theme_combo_box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.theme_combo_box.setObjectName(u'theme_combo_box')
        self.theme_label.setBuddy(self.theme_combo_box)
        self.bottom_form_layout.addRow(self.theme_label, self.theme_combo_box)
        self.credit_label = QtGui.QLabel(custom_edit_dialog)
        self.credit_label.setObjectName(u'credit_label')
        self.credit_edit = QtGui.QLineEdit(custom_edit_dialog)
        self.credit_edit.setObjectName(u'credit_edit')
        self.credit_label.setBuddy(self.credit_edit)
        self.bottom_form_layout.addRow(self.credit_label, self.credit_edit)
        self.dialog_layout.addLayout(self.bottom_form_layout)
        self.preview_button = QtGui.QPushButton()
        self.button_box = create_button_box(custom_edit_dialog, u'button_box', [u'cancel', u'save'],
            [self.preview_button])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(custom_edit_dialog)
        
    def retranslateUi(self, custom_edit_dialog):
        custom_edit_dialog.setWindowTitle(translate('CustomPlugin.EditCustomForm', 'Edit Custom Slides'))
        self.title_label.setText(translate('CustomPlugin.EditCustomForm', '&Title:'))
        self.add_button.setText(UiStrings().Add)
        self.add_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Add a new slide at bottom.'))
        self.edit_button.setText(UiStrings().Edit)
        self.edit_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Edit the selected slide.'))
        self.edit_all_button.setText(translate('CustomPlugin.EditCustomForm', 'Ed&it All'))
        self.edit_all_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Edit all the slides at once.'))
        self.theme_label.setText(translate('CustomPlugin.EditCustomForm', 'The&me:'))
        self.credit_label.setText(translate('CustomPlugin.EditCustomForm', '&Credits:'))
        self.preview_button.setText(UiStrings().SaveAndPreview)
            