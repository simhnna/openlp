# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Maikel Stuivenberg, Martin Thompson, Jon Tibble,   #
# Carsten Tinggaard                                                           #
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

class Ui_OpenSongImportDialog(object):
    def setupUi(self, OpenSongImportDialog):
        OpenSongImportDialog.setObjectName(u'OpenSongImportDialog')
        OpenSongImportDialog.resize(481, 172)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(u':/icon/openlp.org-icon-32.bmp'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OpenSongImportDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(OpenSongImportDialog)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setMargin(8)
        self.verticalLayout.setObjectName(u'verticalLayout')
        self.ImportFileWidget = QtGui.QWidget(OpenSongImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ImportFileWidget.sizePolicy().hasHeightForWidth())
        self.ImportFileWidget.setSizePolicy(sizePolicy)
        self.ImportFileWidget.setObjectName(u'ImportFileWidget')
        self.horizontalLayout = QtGui.QHBoxLayout(self.ImportFileWidget)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(u'horizontalLayout')
        self.ImportFileLabel = QtGui.QLabel(self.ImportFileWidget)
        self.ImportFileLabel.setObjectName(u'ImportFileLabel')
        self.horizontalLayout.addWidget(self.ImportFileLabel)
        self.ImportFileLineEdit = QtGui.QLineEdit(self.ImportFileWidget)
        self.ImportFileLineEdit.setObjectName(u'ImportFileLineEdit')
        self.horizontalLayout.addWidget(self.ImportFileLineEdit)
        self.ImportFileSelectPushButton = QtGui.QPushButton(self.ImportFileWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(u':/imports/import_load.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ImportFileSelectPushButton.setIcon(icon1)
        self.ImportFileSelectPushButton.setObjectName(u'ImportFileSelectPushButton')
        self.horizontalLayout.addWidget(self.ImportFileSelectPushButton)
        self.verticalLayout.addWidget(self.ImportFileWidget)
        self.ProgressGroupBox = QtGui.QGroupBox(OpenSongImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ProgressGroupBox.sizePolicy().hasHeightForWidth())
        self.ProgressGroupBox.setSizePolicy(sizePolicy)
        self.ProgressGroupBox.setObjectName(u'ProgressGroupBox')
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.ProgressGroupBox)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setContentsMargins(6, 0, 8, 8)
        self.verticalLayout_4.setObjectName(u'verticalLayout_4')
        self.ProgressLabel = QtGui.QLabel(self.ProgressGroupBox)
        self.ProgressLabel.setObjectName(u'ProgressLabel')
        self.verticalLayout_4.addWidget(self.ProgressLabel)
        self.ProgressBar = QtGui.QProgressBar(self.ProgressGroupBox)
        self.ProgressBar.setProperty(u'value', QtCore.QVariant(24))
        self.ProgressBar.setObjectName(u'ProgressBar')
        self.verticalLayout_4.addWidget(self.ProgressBar)
        self.verticalLayout.addWidget(self.ProgressGroupBox)
        self.ButtonBarWidget = QtGui.QWidget(OpenSongImportDialog)
        self.ButtonBarWidget.setObjectName(u'ButtonBarWidget')
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.ButtonBarWidget)
        self.horizontalLayout_7.setSpacing(8)
        self.horizontalLayout_7.setMargin(0)
        self.horizontalLayout_7.setObjectName(u'horizontalLayout_7')
        spacerItem = QtGui.QSpacerItem(288, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.ImportPushButton = QtGui.QPushButton(self.ButtonBarWidget)
        self.ImportPushButton.setObjectName(u'ImportPushButton')
        self.horizontalLayout_7.addWidget(self.ImportPushButton)
        self.ClosePushButton = QtGui.QPushButton(self.ButtonBarWidget)
        self.ClosePushButton.setObjectName(u'ClosePushButton')
        self.horizontalLayout_7.addWidget(self.ClosePushButton)
        self.verticalLayout.addWidget(self.ButtonBarWidget)

        self.retranslateUi(OpenSongImportDialog)
        QtCore.QObject.connect(self.ClosePushButton, QtCore.SIGNAL(u'clicked()'), OpenSongImportDialog.close)
        QtCore.QMetaObject.connectSlotsByName(OpenSongImportDialog)

    def retranslateUi(self, OpenSongImportDialog):
        OpenSongImportDialog.setWindowTitle(self.trUtf8('OpenSong Song Importer'))
        self.ImportFileLabel.setText(self.trUtf8('OpenSong Folder:'))
        self.ProgressGroupBox.setTitle(self.trUtf8('Progress:'))
        self.ProgressLabel.setText(self.trUtf8('Ready to import'))
        self.ImportPushButton.setText(self.trUtf8('Import'))
        self.ClosePushButton.setText(self.trUtf8('Close'))
