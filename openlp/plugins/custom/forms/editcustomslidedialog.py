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

from openlp.core.lib import SpellTextEdit, UiStrings, translate
from openlp.core.lib.ui import create_button, create_button_box

class Ui_CustomSlideEditDialog(object):
    def setupUi(self, custom_slide_edit_dialog):
        custom_slide_edit_dialog.setObjectName(u'custom_slide_edit_dialog')
        custom_slide_edit_dialog.resize(350, 300)
        self.dialog_layout = QtGui.QVBoxLayout(custom_slide_edit_dialog)
        self.slide_text_edit = SpellTextEdit(self)
        self.slide_text_edit.setObjectName(u'slide_text_edit')
        self.dialog_layout.addWidget(self.slide_text_edit)
        self.split_button = create_button(custom_slide_edit_dialog, u'splitButton', icon=u':/general/general_add.png')
        self.insert_button = create_button(custom_slide_edit_dialog, u'insertButton',
                                           icon=u':/general/general_add.png')
        self.button_box = create_button_box(custom_slide_edit_dialog, u'button_box', [u'cancel', u'save'],
            [self.split_button, self.insert_button])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(custom_slide_edit_dialog)

    def retranslateUi(self, custom_slide_edit_dialog):
        custom_slide_edit_dialog.setWindowTitle(translate('CustomPlugin.EditVerseForm', 'Edit Slide'))
        self.split_button.setText(UiStrings().Split)
        self.split_button.setToolTip(UiStrings().SplitToolTip)
        self.insert_button.setText(translate('CustomPlugin.EditCustomForm', 'Insert Slide'))
        self.insert_button.setToolTip(translate('CustomPlugin.EditCustomForm',
            'Split a slide into two by inserting a slide splitter.'))
