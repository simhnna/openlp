# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
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

from PyQt4 import QtCore, QtGui
from openlp.core.lib import translate

class Ui_PluginViewDialog(object):
    def setupUi(self, pluginViewDialog):
        pluginViewDialog.setObjectName(u'pluginViewDialog')
        pluginViewDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        pluginViewDialog.resize(554, 344)
        self.pluginLayout = QtGui.QVBoxLayout(pluginViewDialog)
        self.pluginLayout.setSpacing(8)
        self.pluginLayout.setMargin(8)
        self.pluginLayout.setObjectName(u'pluginLayout')
        self.listLayout = QtGui.QHBoxLayout()
        self.listLayout.setSpacing(8)
        self.listLayout.setObjectName(u'listLayout')
        self.pluginListWidget = QtGui.QListWidget(pluginViewDialog)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pluginListWidget.sizePolicy().hasHeightForWidth())
        self.pluginListWidget.setSizePolicy(sizePolicy)
        self.pluginListWidget.setMaximumSize(QtCore.QSize(192, 16777215))
        self.pluginListWidget.setObjectName(u'pluginListWidget')
        self.listLayout.addWidget(self.pluginListWidget)
        self.pluginInfoGroupBox = QtGui.QGroupBox(pluginViewDialog)
        self.pluginInfoGroupBox.setAlignment(
            QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pluginInfoGroupBox.setFlat(False)
        self.pluginInfoGroupBox.setObjectName(u'pluginInfoGroupBox')
        self.pluginInfoLayout = QtGui.QFormLayout(self.pluginInfoGroupBox)
        self.pluginInfoLayout.setMargin(8)
        self.pluginInfoLayout.setSpacing(8)
        self.pluginInfoLayout.setObjectName(u'pluginInfoLayout')
        self.versionLabel = QtGui.QLabel(self.pluginInfoGroupBox)
        self.versionLabel.setObjectName(u'versionLabel')
        self.pluginInfoLayout.setWidget(
            1, QtGui.QFormLayout.LabelRole, self.versionLabel)
        self.versionNumberLabel = QtGui.QLabel(self.pluginInfoGroupBox)
        self.versionNumberLabel.setObjectName(u'versionNumberLabel')
        self.pluginInfoLayout.setWidget(
            1, QtGui.QFormLayout.FieldRole, self.versionNumberLabel)
        self.aboutLabel = QtGui.QLabel(self.pluginInfoGroupBox)
        self.aboutLabel.setObjectName(u'aboutLabel')
        self.pluginInfoLayout.setWidget(
            2, QtGui.QFormLayout.LabelRole, self.aboutLabel)
        self.statusLabel = QtGui.QLabel(self.pluginInfoGroupBox)
        self.statusLabel.setObjectName(u'statusLabel')
        self.pluginInfoLayout.setWidget(
            0, QtGui.QFormLayout.LabelRole, self.statusLabel)
        self.statusComboBox = QtGui.QComboBox(self.pluginInfoGroupBox)
        self.statusComboBox.setObjectName(u'statusComboBox')
        self.statusComboBox.addItem(QtCore.QString())
        self.statusComboBox.addItem(QtCore.QString())
        self.pluginInfoLayout.setWidget(
            0, QtGui.QFormLayout.FieldRole, self.statusComboBox)
        self.aboutTextBrowser = QtGui.QTextBrowser(self.pluginInfoGroupBox)
        self.aboutTextBrowser.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse)
        self.aboutTextBrowser.setObjectName(u'aboutTextBrowser')
        self.pluginInfoLayout.setWidget(
            2, QtGui.QFormLayout.FieldRole, self.aboutTextBrowser)
        self.listLayout.addWidget(self.pluginInfoGroupBox)
        self.pluginLayout.addLayout(self.listLayout)
        self.pluginListButtonBox = QtGui.QDialogButtonBox(pluginViewDialog)
        self.pluginListButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.pluginListButtonBox.setObjectName(u'pluginListButtonBox')
        self.pluginLayout.addWidget(self.pluginListButtonBox)
        self.retranslateUi(pluginViewDialog)
        QtCore.QObject.connect(self.pluginListButtonBox,
            QtCore.SIGNAL(u'accepted()'), pluginViewDialog.close)
        QtCore.QMetaObject.connectSlotsByName(pluginViewDialog)

    def retranslateUi(self, pluginViewDialog):
        pluginViewDialog.setWindowTitle(
            translate('OpenLP.PluginForm', 'Plugin List'))
        self.pluginInfoGroupBox.setTitle(
            translate('OpenLP.PluginForm', 'Plugin Details'))
        self.versionLabel.setText(
            translate('OpenLP.PluginForm', 'Version:'))
        self.versionNumberLabel.setText(
            translate('OpenLP.PluginForm', 'TextLabel'))
        self.aboutLabel.setText(
            translate('OpenLP.PluginForm', 'About:'))
        self.statusLabel.setText(
            translate('OpenLP.PluginForm', 'Status:'))
        self.statusComboBox.setItemText(0,
            translate('OpenLP.PluginForm', 'Active'))
        self.statusComboBox.setItemText(1,
            translate('OpenLP.PluginForm', 'Inactive'))
