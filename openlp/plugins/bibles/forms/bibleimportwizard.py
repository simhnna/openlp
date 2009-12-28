# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2009 Raoul Snyman                                        #
# Portions copyright (c) 2008-2009 Tim Bentley, Jonathan Corwin, Michael      #
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

class Ui_BibleImportWizard(object):
    def setupUi(self, BibleImportWizard):
        BibleImportWizard.setObjectName(u'BibleImportWizard')
        BibleImportWizard.resize(550, 386)
        BibleImportWizard.setModal(True)
        BibleImportWizard.setWizardStyle(QtGui.QWizard.ModernStyle)
        BibleImportWizard.setOptions(
            QtGui.QWizard.IndependentPages | \
            QtGui.QWizard.NoBackButtonOnStartPage | \
            QtGui.QWizard.NoBackButtonOnLastPage)
        self.WelcomePage = QtGui.QWizardPage()
        self.WelcomePage.setPixmap(QtGui.QWizard.WatermarkPixmap,
            QtGui.QPixmap(u':/wizards/wizard_importbible.bmp'))
        self.WelcomePage.setObjectName(u'WelcomePage')
        self.WelcomeLayout = QtGui.QVBoxLayout(self.WelcomePage)
        self.WelcomeLayout.setSpacing(8)
        self.WelcomeLayout.setMargin(0)
        self.WelcomeLayout.setObjectName(u'WelcomeLayout')
        self.TitleLabel = QtGui.QLabel(self.WelcomePage)
        self.TitleLabel.setObjectName(u'TitleLabel')
        self.WelcomeLayout.addWidget(self.TitleLabel)
        spacerItem = QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.WelcomeLayout.addItem(spacerItem)
        self.InformationLabel = QtGui.QLabel(self.WelcomePage)
        self.InformationLabel.setWordWrap(True)
        self.InformationLabel.setMargin(10)
        self.InformationLabel.setObjectName(u'InformationLabel')
        self.WelcomeLayout.addWidget(self.InformationLabel)
        spacerItem1 = QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.WelcomeLayout.addItem(spacerItem1)
        BibleImportWizard.addPage(self.WelcomePage)
        self.SelectPage = QtGui.QWizardPage()
        self.SelectPage.setObjectName(u'SelectPage')
        self.SelectPageLayout = QtGui.QVBoxLayout(self.SelectPage)
        self.SelectPageLayout.setSpacing(8)
        self.SelectPageLayout.setMargin(20)
        self.SelectPageLayout.setObjectName(u'SelectPageLayout')
        self.FormatSelectLayout = QtGui.QHBoxLayout()
        self.FormatSelectLayout.setSpacing(8)
        self.FormatSelectLayout.setObjectName(u'FormatSelectLayout')
        self.FormatLabel = QtGui.QLabel(self.SelectPage)
        self.FormatLabel.setObjectName(u'FormatLabel')
        self.FormatSelectLayout.addWidget(self.FormatLabel)
        self.FormatComboBox = QtGui.QComboBox(self.SelectPage)
        self.FormatComboBox.setObjectName(u'FormatComboBox')
        self.FormatComboBox.addItem(u'')
        self.FormatComboBox.addItem(u'')
        self.FormatComboBox.addItem(u'')
        self.FormatComboBox.addItem(u'')
        self.FormatSelectLayout.addWidget(self.FormatComboBox)
        spacerItem2 = QtGui.QSpacerItem(40, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.FormatSelectLayout.addItem(spacerItem2)
        self.SelectPageLayout.addLayout(self.FormatSelectLayout)
        self.FormatWidget = QtGui.QStackedWidget(self.SelectPage)
        self.FormatWidget.setObjectName(u'FormatWidget')
        self.OsisPage = QtGui.QWidget()
        self.OsisPage.setObjectName(u'OsisPage')
        self.OsisLayout = QtGui.QFormLayout(self.OsisPage)
        self.OsisLayout.setFieldGrowthPolicy(
            QtGui.QFormLayout.ExpandingFieldsGrow)
        self.OsisLayout.setMargin(0)
        self.OsisLayout.setSpacing(8)
        self.OsisLayout.setObjectName(u'OsisLayout')
        self.OsisBibleNameLabel = QtGui.QLabel(self.OsisPage)
        self.OsisBibleNameLabel.setIndent(0)
        self.OsisBibleNameLabel.setObjectName(u'OsisBibleNameLabel')
        self.OsisLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.OsisBibleNameLabel)
        self.OsisBibleNameEdit = QtGui.QLineEdit(self.OsisPage)
        self.OsisBibleNameEdit.setObjectName(u'OsisBibleNameEdit')
        self.OsisLayout.setWidget(0, QtGui.QFormLayout.FieldRole,
            self.OsisBibleNameEdit)
        self.OsisLocationLabel = QtGui.QLabel(self.OsisPage)
        self.OsisLocationLabel.setObjectName(u'OsisLocationLabel')
        self.OsisLayout.setWidget(1, QtGui.QFormLayout.LabelRole,
            self.OsisLocationLabel)
        self.OsisLocationLayout = QtGui.QHBoxLayout()
        self.OsisLocationLayout.setSpacing(8)
        self.OsisLocationLayout.setObjectName(u'OsisLocationLayout')
        self.OSISLocationEdit = QtGui.QLineEdit(self.OsisPage)
        self.OSISLocationEdit.setObjectName(u'OSISLocationEdit')
        self.OsisLocationLayout.addWidget(self.OSISLocationEdit)
        self.OsisFileButton = QtGui.QToolButton(self.OsisPage)
        self.OsisFileButton.setMaximumSize(QtCore.QSize(32, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(u':/imports/import_load.png'),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.OsisFileButton.setIcon(icon)
        self.OsisFileButton.setObjectName(u'OsisFileButton')
        self.OsisLocationLayout.addWidget(self.OsisFileButton)
        self.OsisLayout.setLayout(1, QtGui.QFormLayout.FieldRole,
            self.OsisLocationLayout)
        self.FormatWidget.addWidget(self.OsisPage)
        self.CsvPage = QtGui.QWidget()
        self.CsvPage.setObjectName(u'CsvPage')
        self.CsvSourceLayout = QtGui.QFormLayout(self.CsvPage)
        self.CsvSourceLayout.setFieldGrowthPolicy(
            QtGui.QFormLayout.ExpandingFieldsGrow)
        self.CsvSourceLayout.setLabelAlignment(QtCore.Qt.AlignBottom |
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing)
        self.CsvSourceLayout.setFormAlignment(QtCore.Qt.AlignLeading |
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.CsvSourceLayout.setMargin(0)
        self.CsvSourceLayout.setSpacing(8)
        self.CsvSourceLayout.setObjectName(u'CsvSourceLayout')
        self.BooksLocationLabel = QtGui.QLabel(self.CsvPage)
        self.BooksLocationLabel.setObjectName(u'BooksLocationLabel')
        self.CsvSourceLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.BooksLocationLabel)
        self.CsvBooksLayout = QtGui.QHBoxLayout()
        self.CsvBooksLayout.setSpacing(8)
        self.CsvBooksLayout.setObjectName(u'CsvBooksLayout')
        self.BooksLocationEdit = QtGui.QLineEdit(self.CsvPage)
        self.BooksLocationEdit.setObjectName(u'BooksLocationEdit')
        self.CsvBooksLayout.addWidget(self.BooksLocationEdit)
        self.BooksFileButton = QtGui.QToolButton(self.CsvPage)
        self.BooksFileButton.setMaximumSize(QtCore.QSize(32, 16777215))
        self.BooksFileButton.setIcon(icon)
        self.BooksFileButton.setObjectName(u'BooksFileButton')
        self.CsvBooksLayout.addWidget(self.BooksFileButton)
        self.CsvSourceLayout.setLayout(0, QtGui.QFormLayout.FieldRole,
            self.CsvBooksLayout)
        self.VerseLocationLabel = QtGui.QLabel(self.CsvPage)
        self.VerseLocationLabel.setObjectName(u'VerseLocationLabel')
        self.CsvSourceLayout.setWidget(1, QtGui.QFormLayout.LabelRole,
            self.VerseLocationLabel)
        self.CsvVerseLayout = QtGui.QHBoxLayout()
        self.CsvVerseLayout.setSpacing(8)
        self.CsvVerseLayout.setObjectName(u'CsvVerseLayout')
        self.CsvVerseLocationEdit = QtGui.QLineEdit(self.CsvPage)
        self.CsvVerseLocationEdit.setObjectName(u'CsvVerseLocationEdit')
        self.CsvVerseLayout.addWidget(self.CsvVerseLocationEdit)
        self.CsvVersesFileButton = QtGui.QToolButton(self.CsvPage)
        self.CsvVersesFileButton.setMaximumSize(QtCore.QSize(32, 16777215))
        self.CsvVersesFileButton.setIcon(icon)
        self.CsvVersesFileButton.setObjectName(u'CsvVersesFileButton')
        self.CsvVerseLayout.addWidget(self.CsvVersesFileButton)
        self.CsvSourceLayout.setLayout(1, QtGui.QFormLayout.FieldRole,
            self.CsvVerseLayout)
        self.FormatWidget.addWidget(self.CsvPage)
        self.OpenSongPage = QtGui.QWidget()
        self.OpenSongPage.setObjectName(u'OpenSongPage')
        self.OpenSongLayout = QtGui.QFormLayout(self.OpenSongPage)
        self.OpenSongLayout.setMargin(0)
        self.OpenSongLayout.setSpacing(8)
        self.OpenSongLayout.setObjectName(u'OpenSongLayout')
        self.OpenSongFileLabel = QtGui.QLabel(self.OpenSongPage)
        self.OpenSongFileLabel.setObjectName(u'OpenSongFileLabel')
        self.OpenSongLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.OpenSongFileLabel)
        self.OpenSongFileLayout = QtGui.QHBoxLayout()
        self.OpenSongFileLayout.setSpacing(8)
        self.OpenSongFileLayout.setObjectName(u'OpenSongFileLayout')
        self.OpenSongFileEdit = QtGui.QLineEdit(self.OpenSongPage)
        self.OpenSongFileEdit.setObjectName(u'OpenSongFileEdit')
        self.OpenSongFileLayout.addWidget(self.OpenSongFileEdit)
        self.OpenSongBrowseButton = QtGui.QToolButton(self.OpenSongPage)
        self.OpenSongBrowseButton.setIcon(icon)
        self.OpenSongBrowseButton.setObjectName(u'OpenSongBrowseButton')
        self.OpenSongFileLayout.addWidget(self.OpenSongBrowseButton)
        self.OpenSongLayout.setLayout(0, QtGui.QFormLayout.FieldRole,
            self.OpenSongFileLayout)
        self.FormatWidget.addWidget(self.OpenSongPage)
        self.WebDownloadPage = QtGui.QWidget()
        self.WebDownloadPage.setObjectName(u'WebDownloadPage')
        self.WebDownloadLayout = QtGui.QVBoxLayout(self.WebDownloadPage)
        self.WebDownloadLayout.setSpacing(8)
        self.WebDownloadLayout.setMargin(0)
        self.WebDownloadLayout.setObjectName(u'WebDownloadLayout')
        self.WebDownloadTabWidget = QtGui.QTabWidget(self.WebDownloadPage)
        self.WebDownloadTabWidget.setObjectName(u'WebDownloadTabWidget')
        self.DownloadOptionsTab = QtGui.QWidget()
        self.DownloadOptionsTab.setObjectName(u'DownloadOptionsTab')
        self.DownloadOptionsLayout = QtGui.QFormLayout(self.DownloadOptionsTab)
        self.DownloadOptionsLayout.setMargin(8)
        self.DownloadOptionsLayout.setSpacing(8)
        self.DownloadOptionsLayout.setObjectName(u'DownloadOptionsLayout')
        self.LocationLabel = QtGui.QLabel(self.DownloadOptionsTab)
        self.LocationLabel.setObjectName(u'LocationLabel')
        self.DownloadOptionsLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.LocationLabel)
        self.LocationComboBox = QtGui.QComboBox(self.DownloadOptionsTab)
        self.LocationComboBox.setObjectName(u'LocationComboBox')
        self.LocationComboBox.addItem(u'')
        self.LocationComboBox.addItem(u'')
        self.DownloadOptionsLayout.setWidget(0, QtGui.QFormLayout.FieldRole,
            self.LocationComboBox)
        self.BibleLabel = QtGui.QLabel(self.DownloadOptionsTab)
        self.BibleLabel.setObjectName(u'BibleLabel')
        self.DownloadOptionsLayout.setWidget(1, QtGui.QFormLayout.LabelRole,
            self.BibleLabel)
        self.BibleComboBox = QtGui.QComboBox(self.DownloadOptionsTab)
        self.BibleComboBox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.BibleComboBox.setObjectName(u'BibleComboBox')
        self.BibleComboBox.addItem(u'')
        self.BibleComboBox.addItem(u'')
        self.BibleComboBox.addItem(u'')
        self.DownloadOptionsLayout.setWidget(1, QtGui.QFormLayout.FieldRole,
            self.BibleComboBox)
        self.WebDownloadTabWidget.addTab(self.DownloadOptionsTab, u'')
        self.ProxyServerTab = QtGui.QWidget()
        self.ProxyServerTab.setObjectName(u'ProxyServerTab')
        self.ProxyServerLayout = QtGui.QFormLayout(self.ProxyServerTab)
        self.ProxyServerLayout.setObjectName(u'ProxyServerLayout')
        self.AddressLabel = QtGui.QLabel(self.ProxyServerTab)
        self.AddressLabel.setObjectName(u'AddressLabel')
        self.ProxyServerLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.AddressLabel)
        self.AddressEdit = QtGui.QLineEdit(self.ProxyServerTab)
        self.AddressEdit.setObjectName(u'AddressEdit')
        self.ProxyServerLayout.setWidget(0, QtGui.QFormLayout.FieldRole,
            self.AddressEdit)
        self.UsernameLabel = QtGui.QLabel(self.ProxyServerTab)
        self.UsernameLabel.setObjectName(u'UsernameLabel')
        self.ProxyServerLayout.setWidget(1, QtGui.QFormLayout.LabelRole,
            self.UsernameLabel)
        self.UsernameEdit = QtGui.QLineEdit(self.ProxyServerTab)
        self.UsernameEdit.setObjectName(u'UsernameEdit')
        self.ProxyServerLayout.setWidget(1, QtGui.QFormLayout.FieldRole,
            self.UsernameEdit)
        self.PasswordLabel = QtGui.QLabel(self.ProxyServerTab)
        self.PasswordLabel.setObjectName(u'PasswordLabel')
        self.ProxyServerLayout.setWidget(2, QtGui.QFormLayout.LabelRole,
            self.PasswordLabel)
        self.PasswordEdit = QtGui.QLineEdit(self.ProxyServerTab)
        self.PasswordEdit.setObjectName(u'PasswordEdit')
        self.ProxyServerLayout.setWidget(2, QtGui.QFormLayout.FieldRole,
            self.PasswordEdit)
        self.WebDownloadTabWidget.addTab(self.ProxyServerTab, u'')
        self.WebDownloadLayout.addWidget(self.WebDownloadTabWidget)
        self.FormatWidget.addWidget(self.WebDownloadPage)
        self.SelectPageLayout.addWidget(self.FormatWidget)
        BibleImportWizard.addPage(self.SelectPage)
        self.LicenseDetailsPage = QtGui.QWizardPage()
        self.LicenseDetailsPage.setObjectName(u'LicenseDetailsPage')
        self.LicenseDetailsLayout = QtGui.QFormLayout(self.LicenseDetailsPage)
        self.LicenseDetailsLayout.setMargin(20)
        self.LicenseDetailsLayout.setSpacing(8)
        self.LicenseDetailsLayout.setObjectName(u'LicenseDetailsLayout')
        self.VersionNameLabel = QtGui.QLabel(self.LicenseDetailsPage)
        self.VersionNameLabel.setObjectName(u'VersionNameLabel')
        self.LicenseDetailsLayout.setWidget(0, QtGui.QFormLayout.LabelRole,
            self.VersionNameLabel)
        self.VersionNameEdit = QtGui.QLineEdit(self.LicenseDetailsPage)
        self.VersionNameEdit.setObjectName(u'VersionNameEdit')
        self.LicenseDetailsLayout.setWidget(0, QtGui.QFormLayout.FieldRole,
            self.VersionNameEdit)
        self.CopyrightLabel = QtGui.QLabel(self.LicenseDetailsPage)
        self.CopyrightLabel.setObjectName(u'CopyrightLabel')
        self.LicenseDetailsLayout.setWidget(1, QtGui.QFormLayout.LabelRole,
            self.CopyrightLabel)
        self.CopyrightEdit = QtGui.QLineEdit(self.LicenseDetailsPage)
        self.CopyrightEdit.setObjectName(u'CopyrightEdit')
        self.LicenseDetailsLayout.setWidget(1, QtGui.QFormLayout.FieldRole,
            self.CopyrightEdit)
        self.PermissionLabel = QtGui.QLabel(self.LicenseDetailsPage)
        self.PermissionLabel.setObjectName(u'PermissionLabel')
        self.LicenseDetailsLayout.setWidget(2, QtGui.QFormLayout.LabelRole,\
            self.PermissionLabel)
        self.PermissionEdit = QtGui.QLineEdit(self.LicenseDetailsPage)
        self.PermissionEdit.setObjectName(u'PermissionEdit')
        self.LicenseDetailsLayout.setWidget(2, QtGui.QFormLayout.FieldRole,
            self.PermissionEdit)
        BibleImportWizard.addPage(self.LicenseDetailsPage)
        self.ImportPage = QtGui.QWizardPage()
        self.ImportPage.setObjectName(u'ImportPage')
        self.ImportLayout = QtGui.QVBoxLayout(self.ImportPage)
        self.ImportLayout.setSpacing(8)
        self.ImportLayout.setMargin(50)
        self.ImportLayout.setObjectName(u'ImportLayout')
        self.ImportProgressLabel = QtGui.QLabel(self.ImportPage)
        self.ImportProgressLabel.setObjectName(u'ImportProgressLabel')
        self.ImportLayout.addWidget(self.ImportProgressLabel)
        self.ImportProgressBar = QtGui.QProgressBar(self.ImportPage)
        self.ImportProgressBar.setProperty(u'value', 0)
        self.ImportProgressBar.setInvertedAppearance(False)
        self.ImportProgressBar.setObjectName(u'ImportProgressBar')
        self.ImportLayout.addWidget(self.ImportProgressBar)
        BibleImportWizard.addPage(self.ImportPage)


        self.retranslateUi(BibleImportWizard)
        self.FormatWidget.setCurrentIndex(0)
        self.WebDownloadTabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.FormatComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'),
            self.FormatWidget.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(BibleImportWizard)

    def retranslateUi(self, BibleImportWizard):
        BibleImportWizard.setWindowTitle(self.trUtf8('Bible Import Wizard'))
        self.TitleLabel.setText(
            u'<span style=\" font-size:14pt; font-weight:600;\">' + \
            self.trUtf8('Welcome to the Bible Import Wizard') + u'</span>')
        self.InformationLabel.setText(
            self.trUtf8('This wizard will help you to import Bibles from a '
                'variety of formats. Click the next button below to start the '
                'process by selecting a format to import from.'))
        self.SelectPage.setTitle(self.trUtf8('Select Import Source'))
        self.SelectPage.setSubTitle(
            self.trUtf8('Select the import format, and where to import from.'))
        self.FormatLabel.setText(self.trUtf8('Format:'))
        self.FormatComboBox.setItemText(0, self.trUtf8('OSIS'))
        self.FormatComboBox.setItemText(1, self.trUtf8('CSV'))
        self.FormatComboBox.setItemText(2, self.trUtf8('OpenSong'))
        self.FormatComboBox.setItemText(3, self.trUtf8('Web Download'))
        self.OsisBibleNameLabel.setText(self.trUtf8('Bible Name:'))
        self.OsisLocationLabel.setText(self.trUtf8('File Location:'))
        self.BooksLocationLabel.setText(self.trUtf8('Books Location:'))
        self.VerseLocationLabel.setText(self.trUtf8('Verse Location:'))
        self.OpenSongFileLabel.setText(self.trUtf8('Bible Filename:'))
        self.LocationLabel.setText(self.trUtf8('Location:'))
        self.LocationComboBox.setItemText(0, self.trUtf8('Crosswalk'))
        self.LocationComboBox.setItemText(1, self.trUtf8('BibleGateway'))
        self.BibleLabel.setText(self.trUtf8('Bible:'))
        self.WebDownloadTabWidget.setTabText(
            self.WebDownloadTabWidget.indexOf(self.DownloadOptionsTab),
            self.trUtf8('Download Options'))
        self.AddressLabel.setText(self.trUtf8('Server:'))
        self.UsernameLabel.setText(self.trUtf8('Username:'))
        self.PasswordLabel.setText(self.trUtf8('Password:'))
        self.WebDownloadTabWidget.setTabText(
            self.WebDownloadTabWidget.indexOf(self.ProxyServerTab),
            self.trUtf8('Proxy Server (Optional)'))
        self.LicenseDetailsPage.setTitle(self.trUtf8('License Details'))
        self.LicenseDetailsPage.setSubTitle(
            self.trUtf8('Set up the Bible\'s license details.'))
        self.VersionNameLabel.setText(self.trUtf8('Version Name:'))
        self.CopyrightLabel.setText(self.trUtf8('Copyright:'))
        self.PermissionLabel.setText(self.trUtf8('Permission:'))
        self.ImportPage.setTitle(self.trUtf8('Importing'))
        self.ImportPage.setSubTitle(
            self.trUtf8('Please wait while your Bible is imported.'))
        self.ImportProgressLabel.setText(self.trUtf8('Ready.'))
        #self.ImportProgressBar.setFormat(u'%p')
