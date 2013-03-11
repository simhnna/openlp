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

from openlp.core.lib import SpellTextEdit, build_icon, translate
from openlp.core.lib.ui import UiStrings, create_button_box
from openlp.plugins.songs.lib import VerseType


class Ui_EditVerseDialog(object):
    def setupUi(self, edit_verse_dialog):
        edit_verse_dialog.setObjectName(u'editVerseDialog')
        edit_verse_dialog.resize(400, 400)
        edit_verse_dialog.setModal(True)
        self.dialog_layout = QtGui.QVBoxLayout(edit_verse_dialog)
        self.dialog_layout.setObjectName(u'dialog_layout')
        self.verse_text_edit = SpellTextEdit(edit_verse_dialog)
        self.verse_text_edit.setObjectName(u'verseTextEdit')
        self.dialog_layout.addWidget(self.verse_text_edit)
        self.verse_type_layout = QtGui.QHBoxLayout()
        self.verse_type_layout.setObjectName(u'verseTypeLayout')
        self.split_button = QtGui.QPushButton(edit_verse_dialog)
        self.split_button.setIcon(build_icon(u':/general/general_add.png'))
        self.split_button.setObjectName(u'splitButton')
        self.verse_type_layout.addWidget(self.split_button)
        self.verse_type_label = QtGui.QLabel(edit_verse_dialog)
        self.verse_type_label.setObjectName(u'verseTypeLabel')
        self.verse_type_layout.addWidget(self.verse_type_label)
        self.verse_type_combo_box = QtGui.QComboBox(edit_verse_dialog)
        self.verse_type_combo_box.addItems([u'', u'', u'', u'', u'', u'', u''])
        self.verse_type_combo_box.setObjectName(u'verseTypeComboBox')
        self.verse_type_label.setBuddy(self.verse_type_combo_box)
        self.verse_type_layout.addWidget(self.verse_type_combo_box)
        self.verse_number_box = QtGui.QSpinBox(edit_verse_dialog)
        self.verse_number_box.setMinimum(1)
        self.verse_number_box.setObjectName(u'verseNumberBox')
        self.verse_type_layout.addWidget(self.verse_number_box)
        self.insert_button = QtGui.QPushButton(edit_verse_dialog)
        self.insert_button.setIcon(build_icon(u':/general/general_add.png'))
        self.insert_button.setObjectName(u'insertButton')
        self.verse_type_layout.addWidget(self.insert_button)
        self.verse_type_layout.addStretch()
        self.dialog_layout.addLayout(self.verse_type_layout)
        self.button_box = create_button_box(edit_verse_dialog, u'button_box', [u'cancel', u'ok'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(edit_verse_dialog)

    def retranslateUi(self, edit_verse_dialog):
        edit_verse_dialog.setWindowTitle(translate('SongsPlugin.EditVerseForm', 'Edit Verse'))
        self.verse_type_label.setText(translate('SongsPlugin.EditVerseForm', '&Verse type:'))
        self.verse_type_combo_box.setItemText(VerseType.Verse, VerseType.translated_names[VerseType.Verse])
        self.verse_type_combo_box.setItemText(VerseType.Chorus, VerseType.translated_names[VerseType.Chorus])
        self.verse_type_combo_box.setItemText(VerseType.Bridge, VerseType.translated_names[VerseType.Bridge])
        self.verse_type_combo_box.setItemText(VerseType.PreChorus, VerseType.translated_names[VerseType.PreChorus])
        self.verse_type_combo_box.setItemText(VerseType.Intro, VerseType.translated_names[VerseType.Intro])
        self.verse_type_combo_box.setItemText(VerseType.Ending, VerseType.translated_names[VerseType.Ending])
        self.verse_type_combo_box.setItemText(VerseType.Other, VerseType.translated_names[VerseType.Other])
        self.split_button.setText(UiStrings().Split)
        self.split_button.setToolTip(UiStrings().SplitToolTip)
        self.insert_button.setText(translate('SongsPlugin.EditVerseForm', '&Insert'))
        self.insert_button.setToolTip(translate('SongsPlugin.EditVerseForm',
            'Split a slide into two by inserting a verse splitter.'))
