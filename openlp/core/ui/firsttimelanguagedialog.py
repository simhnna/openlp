# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Armin Köhler, Andreas Preikschat,  #
# Christian Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon  #
# Tibble, Carsten Tinggaard, Frode Woldsund                                   #
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

from openlp.core.lib import translate
from openlp.core.lib.ui import create_accept_reject_button_box

class Ui_FirstTimeLanguageDialog(object):
    def setupUi(self, firstTimeLanguageDialog):
        firstTimeLanguageDialog.setObjectName(u'firstTimeLanguageDialog')
        firstTimeLanguageDialog.resize(300, 10)
        self.dialogLayout = QtGui.QGridLayout(firstTimeLanguageDialog)
        self.dialogLayout.setObjectName(u'dialogLayout')
        self.fileNameLabel = QtGui.QLabel(firstTimeLanguageDialog)
        self.fileNameLabel.setObjectName(u'fileNameLabel')
        self.dialogLayout.addWidget(self.fileNameLabel, 0, 0)
        self.LanguageComboBox = QtGui.QComboBox(firstTimeLanguageDialog)
        self.LanguageComboBox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.LanguageComboBox.setObjectName("LanguageComboBox")
        self.dialogLayout.addWidget(self.LanguageComboBox, 0, 1)
        self.buttonBox = create_accept_reject_button_box(firstTimeLanguageDialog, True)
        self.dialogLayout.addWidget(self.buttonBox, 1, 0, 1, 2)
        self.retranslateUi(firstTimeLanguageDialog)
        self.setMaximumHeight(self.sizeHint().height())
        QtCore.QMetaObject.connectSlotsByName(firstTimeLanguageDialog)

    def retranslateUi(self, firstTimeLanguageDialog):
        self.setWindowTitle(translate('OpenLP.FirstTimeLanguageForm',
                'Initial Set up Language'))
        self.fileNameLabel.setText(translate('OpenLP.FirstTimeLanguageForm',
            'Initial Language:'))
