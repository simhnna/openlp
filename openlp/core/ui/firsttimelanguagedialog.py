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
The UI widgets of the language selection dialog.
"""
from PyQt4 import QtGui

from openlp.core.common import translate
from openlp.core.lib.ui import create_button_box


class Ui_FirstTimeLanguageDialog(object):
    """
    The UI widgets of the language selection dialog.
    """
    def setupUi(self, language_dialog):
        """
        Set up the UI.
        """
        language_dialog.setObjectName('language_dialog')
        language_dialog.resize(300, 50)
        self.dialog_layout = QtGui.QVBoxLayout(language_dialog)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setObjectName('dialog_layout')
        self.info_label = QtGui.QLabel(language_dialog)
        self.info_label.setObjectName('info_label')
        self.dialog_layout.addWidget(self.info_label)
        self.language_layout = QtGui.QHBoxLayout()
        self.language_layout.setObjectName('language_layout')
        self.language_label = QtGui.QLabel(language_dialog)
        self.language_label.setObjectName('language_label')
        self.language_layout.addWidget(self.language_label)
        self.language_combo_box = QtGui.QComboBox(language_dialog)
        self.language_combo_box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.language_combo_box.setObjectName("language_combo_box")
        self.language_layout.addWidget(self.language_combo_box)
        self.dialog_layout.addLayout(self.language_layout)
        self.button_box = create_button_box(language_dialog, 'button_box', ['cancel', 'ok'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(language_dialog)
        self.setMaximumHeight(self.sizeHint().height())

    def retranslateUi(self, language_dialog):
        """
        Translate the UI on the fly.
        """
        self.setWindowTitle(translate('OpenLP.FirstTimeLanguageForm', 'Select Translation'))
        self.info_label.setText(
            translate('OpenLP.FirstTimeLanguageForm', 'Choose the translation you\'d like to use in OpenLP.'))
        self.language_label.setText(translate('OpenLP.FirstTimeLanguageForm', 'Translation:'))
