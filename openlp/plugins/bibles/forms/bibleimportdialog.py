# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2009 Raoul Snyman                                        #
# Portions copyright (c) 2008-2009 Martin Thompson, Tim Bentley, Carsten      #
# Tinggaard, Jon Tibble, Jonathan Corwin, Maikel Stuivenberg, Scott Guerrieri #
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

from openlp.core.lib import buildIcon

class Ui_BibleImportDialog(object):
    def setupUi(self, BibleImportDialog):
        BibleImportDialog.setObjectName(u'BibleImportDialog')
        BibleImportDialog.resize(500, 686)
        icon = buildIcon(u':/icon/openlp.org-icon-32.bmp')
        BibleImportDialog.setWindowIcon(icon)
        self.LicenceDetailsGroupBox = QtGui.QGroupBox(BibleImportDialog)
        self.LicenceDetailsGroupBox.setGeometry(QtCore.QRect(10, 400, 480, 151))
        self.LicenceDetailsGroupBox.setMinimumSize(QtCore.QSize(0, 123))
        self.LicenceDetailsGroupBox.setObjectName(u'LicenceDetailsGroupBox')
        self.formLayout = QtGui.QFormLayout(self.LicenceDetailsGroupBox)
        self.formLayout.setMargin(8)
        self.formLayout.setHorizontalSpacing(8)
        self.formLayout.setObjectName(u'formLayout')
        self.VersionNameLabel = QtGui.QLabel(self.LicenceDetailsGroupBox)
        self.VersionNameLabel.setObjectName(u'VersionNameLabel')
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.VersionNameLabel)
        self.VersionNameEdit = QtGui.QLineEdit(self.LicenceDetailsGroupBox)
        self.VersionNameEdit.setObjectName(u'VersionNameEdit')
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.VersionNameEdit)
        self.CopyrightLabel = QtGui.QLabel(self.LicenceDetailsGroupBox)
        self.CopyrightLabel.setObjectName(u'CopyrightLabel')
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.CopyrightLabel)
        self.CopyrightEdit = QtGui.QLineEdit(self.LicenceDetailsGroupBox)
        self.CopyrightEdit.setObjectName(u'CopyrightEdit')
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.CopyrightEdit)
        self.PermisionLabel = QtGui.QLabel(self.LicenceDetailsGroupBox)
        self.PermisionLabel.setObjectName(u'PermisionLabel')
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.PermisionLabel)
        self.PermisionEdit = QtGui.QLineEdit(self.LicenceDetailsGroupBox)
        self.PermisionEdit.setObjectName(u'PermisionEdit')
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.PermisionEdit)
        self.MessageLabel = QtGui.QLabel(BibleImportDialog)
        self.MessageLabel.setGeometry(QtCore.QRect(20, 670, 271, 17))
        self.MessageLabel.setObjectName(u'MessageLabel')
        self.ProgressGroupBox = QtGui.QGroupBox(BibleImportDialog)
        self.ProgressGroupBox.setGeometry(QtCore.QRect(10, 550, 480, 70))
        self.ProgressGroupBox.setObjectName(u'ProgressGroupBox')
        self.gridLayout_3 = QtGui.QGridLayout(self.ProgressGroupBox)
        self.gridLayout_3.setObjectName(u'gridLayout_3')
        self.ProgressBar = QtGui.QProgressBar(self.ProgressGroupBox)
        self.ProgressBar.setProperty(u'value', QtCore.QVariant(0))
        self.ProgressBar.setInvertedAppearance(False)
        self.ProgressBar.setObjectName(u'ProgressBar')
        self.gridLayout_3.addWidget(self.ProgressBar, 0, 0, 1, 1)
        self.layoutWidget = QtGui.QWidget(BibleImportDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(310, 630, 180, 38))
        self.layoutWidget.setObjectName(u'layoutWidget')
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(6)
        self.horizontalLayout.setObjectName(u'horizontalLayout')
        self.ImportButton = QtGui.QPushButton(self.layoutWidget)
        self.ImportButton.setObjectName(u'ImportButton')
        self.horizontalLayout.addWidget(self.ImportButton)
        self.CancelButton = QtGui.QPushButton(self.layoutWidget)
        self.CancelButton.setObjectName(u'CancelButton')
        self.horizontalLayout.addWidget(self.CancelButton)
        self.tabWidget = QtGui.QTabWidget(BibleImportDialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 30, 480, 361))
        self.tabWidget.setObjectName(u'tabWidget')
        self.OsisTab = QtGui.QWidget()
        self.OsisTab.setObjectName(u'OsisTab')
        self.OSISGroupBox = QtGui.QGroupBox(self.OsisTab)
        self.OSISGroupBox.setGeometry(QtCore.QRect(10, 10, 460, 141))
        self.OSISGroupBox.setObjectName(u'OSISGroupBox')
        self.gridLayout_2 = QtGui.QGridLayout(self.OSISGroupBox)
        self.gridLayout_2.setObjectName(u'gridLayout_2')
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u'horizontalLayout_2')
        self.BibleNameLabel = QtGui.QLabel(self.OSISGroupBox)
        self.BibleNameLabel.setObjectName(u'BibleNameLabel')
        self.horizontalLayout_2.addWidget(self.BibleNameLabel)
        self.BibleNameEdit = QtGui.QLineEdit(self.OSISGroupBox)
        self.BibleNameEdit.setObjectName(u'BibleNameEdit')
        self.horizontalLayout_2.addWidget(self.BibleNameEdit)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u'horizontalLayout_3')
        self.LocatioLabel = QtGui.QLabel(self.OSISGroupBox)
        self.LocatioLabel.setObjectName(u'LocatioLabel')
        self.horizontalLayout_3.addWidget(self.LocatioLabel)
        self.OSISLocationEdit = QtGui.QLineEdit(self.OSISGroupBox)
        self.OSISLocationEdit.setObjectName(u'OSISLocationEdit')
        self.horizontalLayout_3.addWidget(self.OSISLocationEdit)
        self.OsisFileButton = QtGui.QPushButton(self.OSISGroupBox)
        icon1 = buildIcon(u':/imports/import_load.png')
        self.OsisFileButton.setIcon(icon1)
        self.OsisFileButton.setObjectName(u'OsisFileButton')
        self.horizontalLayout_3.addWidget(self.OsisFileButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.tabWidget.addTab(self.OsisTab, u'')
        self.CsvTab = QtGui.QWidget()
        self.CsvTab.setObjectName(u'CsvTab')
        self.CVSGroupBox = QtGui.QGroupBox(self.CsvTab)
        self.CVSGroupBox.setGeometry(QtCore.QRect(10, 10, 460, 191))
        self.CVSGroupBox.setObjectName(u'CVSGroupBox')
        self.gridLayout = QtGui.QGridLayout(self.CVSGroupBox)
        self.gridLayout.setMargin(8)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u'gridLayout')
        self.BooksLocationLabel = QtGui.QLabel(self.CVSGroupBox)
        self.BooksLocationLabel.setObjectName(u'BooksLocationLabel')
        self.gridLayout.addWidget(self.BooksLocationLabel, 0, 0, 1, 1)
        self.VerseLocationLabel = QtGui.QLabel(self.CVSGroupBox)
        self.VerseLocationLabel.setObjectName(u'VerseLocationLabel')
        self.gridLayout.addWidget(self.VerseLocationLabel, 4, 0, 1, 1)
        self.VerseLocationEdit = QtGui.QLineEdit(self.CVSGroupBox)
        self.VerseLocationEdit.setObjectName(u'VerseLocationEdit')
        self.gridLayout.addWidget(self.VerseLocationEdit, 4, 1, 1, 1)
        self.BooksLocationEdit = QtGui.QLineEdit(self.CVSGroupBox)
        self.BooksLocationEdit.setObjectName(u'BooksLocationEdit')
        self.gridLayout.addWidget(self.BooksLocationEdit, 0, 1, 1, 1)
        self.BooksFileButton = QtGui.QPushButton(self.CVSGroupBox)
        self.BooksFileButton.setIcon(icon1)
        self.BooksFileButton.setObjectName(u'BooksFileButton')
        self.gridLayout.addWidget(self.BooksFileButton, 0, 2, 1, 1)
        self.VersesFileButton = QtGui.QPushButton(self.CVSGroupBox)
        self.VersesFileButton.setIcon(icon1)
        self.VersesFileButton.setObjectName(u'VersesFileButton')
        self.gridLayout.addWidget(self.VersesFileButton, 4, 2, 1, 1)
        self.tabWidget.addTab(self.CsvTab, u'')
        self.HttpTab = QtGui.QWidget()
        self.HttpTab.setObjectName(u'HttpTab')
        self.OptionsGroupBox = QtGui.QGroupBox(self.HttpTab)
        self.OptionsGroupBox.setGeometry(QtCore.QRect(10, 10, 460, 141))
        self.OptionsGroupBox.setObjectName(u'OptionsGroupBox')
        self.verticalLayout = QtGui.QVBoxLayout(self.OptionsGroupBox)
        self.verticalLayout.setObjectName(u'verticalLayout')
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u'horizontalLayout_4')
        self.LocationLabel = QtGui.QLabel(self.OptionsGroupBox)
        self.LocationLabel.setObjectName(u'LocationLabel')
        self.horizontalLayout_4.addWidget(self.LocationLabel)
        self.LocationComboBox = QtGui.QComboBox(self.OptionsGroupBox)
        self.LocationComboBox.setObjectName(u'LocationComboBox')
        self.LocationComboBox.addItem(QtCore.QString())
        self.LocationComboBox.addItem(QtCore.QString())
        self.horizontalLayout_4.addWidget(self.LocationComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u'horizontalLayout_5')
        self.BibleLabel = QtGui.QLabel(self.OptionsGroupBox)
        self.BibleLabel.setObjectName(u'BibleLabel')
        self.horizontalLayout_5.addWidget(self.BibleLabel)
        self.BibleComboBox = QtGui.QComboBox(self.OptionsGroupBox)
        self.BibleComboBox.setObjectName(u'BibleComboBox')
        self.BibleComboBox.addItem(QtCore.QString())
        self.BibleComboBox.setItemText(0, u'')
        self.BibleComboBox.setItemText(1, u'')
        self.BibleComboBox.addItem(QtCore.QString())
        self.BibleComboBox.addItem(QtCore.QString())
        self.horizontalLayout_5.addWidget(self.BibleComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.ProxyGroupBox = QtGui.QGroupBox(self.HttpTab)
        self.ProxyGroupBox.setGeometry(QtCore.QRect(10, 160, 460, 161))
        self.ProxyGroupBox.setObjectName(u'ProxyGroupBox')
        self.ProxySettingsLayout = QtGui.QFormLayout(self.ProxyGroupBox)
        self.ProxySettingsLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.ProxySettingsLayout.setMargin(8)
        self.ProxySettingsLayout.setSpacing(8)
        self.ProxySettingsLayout.setObjectName(u'ProxySettingsLayout')
        self.AddressLabel = QtGui.QLabel(self.ProxyGroupBox)
        self.AddressLabel.setObjectName(u'AddressLabel')
        self.ProxySettingsLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.AddressLabel)
        self.AddressEdit = QtGui.QLineEdit(self.ProxyGroupBox)
        self.AddressEdit.setObjectName(u'AddressEdit')
        self.ProxySettingsLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.AddressEdit)
        self.UsernameLabel = QtGui.QLabel(self.ProxyGroupBox)
        self.UsernameLabel.setObjectName(u'UsernameLabel')
        self.ProxySettingsLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.UsernameLabel)
        self.UsernameEdit = QtGui.QLineEdit(self.ProxyGroupBox)
        self.UsernameEdit.setObjectName(u'UsernameEdit')
        self.ProxySettingsLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.UsernameEdit)
        self.PasswordLabel = QtGui.QLabel(self.ProxyGroupBox)
        self.PasswordLabel.setObjectName(u'PasswordLabel')
        self.ProxySettingsLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.PasswordLabel)
        self.PasswordEdit = QtGui.QLineEdit(self.ProxyGroupBox)
        self.PasswordEdit.setObjectName(u'PasswordEdit')
        self.ProxySettingsLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.PasswordEdit)
        self.tabWidget.addTab(self.HttpTab, u'')

        self.retranslateUi(BibleImportDialog)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(BibleImportDialog)
        BibleImportDialog.setTabOrder(self.BibleNameEdit, self.OSISLocationEdit)
        BibleImportDialog.setTabOrder(self.OSISLocationEdit, self.OsisFileButton)
        BibleImportDialog.setTabOrder(self.OsisFileButton, self.BooksLocationEdit)
        BibleImportDialog.setTabOrder(self.BooksLocationEdit, self.BooksFileButton)
        BibleImportDialog.setTabOrder(self.BooksFileButton, self.VerseLocationEdit)
        BibleImportDialog.setTabOrder(self.VerseLocationEdit, self.VersesFileButton)
        BibleImportDialog.setTabOrder(self.VersesFileButton, self.LocationComboBox)
        BibleImportDialog.setTabOrder(self.LocationComboBox, self.BibleComboBox)
        BibleImportDialog.setTabOrder(self.BibleComboBox, self.AddressEdit)
        BibleImportDialog.setTabOrder(self.AddressEdit, self.UsernameEdit)
        BibleImportDialog.setTabOrder(self.UsernameEdit, self.PasswordEdit)
        BibleImportDialog.setTabOrder(self.PasswordEdit, self.VersionNameEdit)
        BibleImportDialog.setTabOrder(self.VersionNameEdit, self.CopyrightEdit)
        BibleImportDialog.setTabOrder(self.CopyrightEdit, self.PermisionEdit)

    def retranslateUi(self, BibleImportDialog):
        BibleImportDialog.setWindowTitle(self.trUtf8(u'Bible Registration'))
        self.LicenceDetailsGroupBox.setTitle(self.trUtf8(u'Licence Details'))
        self.VersionNameLabel.setText(self.trUtf8(u'Version Name:'))
        self.CopyrightLabel.setText(self.trUtf8(u'Copyright:'))
        self.PermisionLabel.setText(self.trUtf8(u'Permission:'))
        self.ProgressGroupBox.setTitle(self.trUtf8(u'Import Progress'))
        self.ProgressBar.setFormat(self.trUtf8(u'%p'))
        self.ImportButton.setText(self.trUtf8(u'Import'))
        self.CancelButton.setText(self.trUtf8(u'Cancel'))
        self.OSISGroupBox.setTitle(self.trUtf8(u'OSIS Bible'))
        self.BibleNameLabel.setText(self.trUtf8(u'Bible Name:'))
        self.LocatioLabel.setText(self.trUtf8(u'File Location:'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.OsisTab),
            self.trUtf8(u'Osis (Sword) Imports'))
        self.CVSGroupBox.setTitle(self.trUtf8(u'CVS Bible'))
        self.BooksLocationLabel.setText(self.trUtf8(u'Books Location:'))
        self.VerseLocationLabel.setText(self.trUtf8(u'Verse Location:'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CsvTab),
            self.trUtf8(u'CSV File Imports'))
        self.OptionsGroupBox.setTitle(self.trUtf8(u'Download Options'))
        self.LocationLabel.setText(self.trUtf8(u'Location:'))
        self.LocationComboBox.setItemText(0, self.trUtf8(u'Crosswalk'))
        self.LocationComboBox.setItemText(1, self.trUtf8(u'BibleGateway'))
        self.BibleLabel.setText(self.trUtf8(u'Bible:'))
        self.ProxyGroupBox.setTitle(self.trUtf8(u'Proxy Settings (Optional)'))
        self.AddressLabel.setText(self.trUtf8(u'Proxy Address:'))
        self.UsernameLabel.setText(self.trUtf8(u'Username:'))
        self.PasswordLabel.setText(self.trUtf8(u'Password:'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.HttpTab),
            self.trUtf8(u'Web Downloads'))
