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

import csv
import logging
import os
import os.path

from PyQt4 import QtCore, QtGui

from bibleimportwizard import Ui_BibleImportWizard
from openlp.core.lib import Receiver
from openlp.core.utils import AppLocation
from openlp.plugins.bibles.lib.manager import BibleFormat

log = logging.getLogger(__name__)

class DownloadLocation(object):
    Unknown = -1
    Crosswalk = 0
    BibleGateway = 1

    Names = {
        0: u'Crosswalk',
        1: u'BibleGateway'
    }

    @classmethod
    def get_name(cls, id):
        return cls.Names[id]


class ImportWizardForm(QtGui.QWizard, Ui_BibleImportWizard):
    """
    This is the Bible Import Wizard, which allows easy importing of Bibles
    into OpenLP from other formats like OSIS, CSV and OpenSong.
    """
    log.info(u'BibleImportForm loaded')

    def __init__(self, parent, config, manager, bibleplugin):
        '''
        Constructor
        '''
        QtGui.QWizard.__init__(self, parent)
        self.setupUi(self)
        self.registerFields()
        self.finishButton = self.button(QtGui.QWizard.FinishButton)
        self.cancelButton = self.button(QtGui.QWizard.CancelButton)
        self.manager = manager
        self.config = config
        self.bibleplugin = bibleplugin
        self.manager.set_process_dialog(self)
        self.web_bible_list = {}
        self.loadWebBibles()
        QtCore.QObject.connect(self.LocationComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'),
            self.onLocationComboBoxChanged)
        QtCore.QObject.connect(self.OsisFileButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOsisFileButtonClicked)
        QtCore.QObject.connect(self.BooksFileButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onBooksFileButtonClicked)
        QtCore.QObject.connect(self.CsvVersesFileButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onCsvVersesFileButtonClicked)
        QtCore.QObject.connect(self.OpenSongBrowseButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenSongBrowseButtonClicked)
        QtCore.QObject.connect(self.cancelButton,
            QtCore.SIGNAL(u'clicked(bool)'),
            self.onCancelButtonClicked)
        QtCore.QObject.connect(self,
            QtCore.SIGNAL(u'currentIdChanged(int)'),
            self.onCurrentIdChanged)

    def exec_(self):
        self.setDefaults()
        return QtGui.QWizard.exec_(self)

    def validateCurrentPage(self):
        if self.currentId() == 0:
            # Welcome page
            return True
        elif self.currentId() == 1:
            # Select page
            if self.field(u'source_format').toInt()[0] == BibleFormat.OSIS:
                if self.field(u'osis_location').toString() == u'':
                    QtGui.QMessageBox.critical(self,
                        self.trUtf8('Invalid Bible Location'),
                        self.trUtf8('You need to specify a file to import your '
                            'Bible from.'),
                        QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                    self.OSISLocationEdit.setFocus()
                    return False
            elif self.field(u'source_format').toInt()[0] == BibleFormat.CSV:
                if self.field(u'csv_booksfile').toString() == u'':
                    QtGui.QMessageBox.critical(self,
                        self.trUtf8('Invalid Books File'),
                        self.trUtf8('You need to specify a file with books of '
                            'the Bible to use in the import.'),
                        QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                    self.BooksLocationEdit.setFocus()
                    return False
                elif self.field(u'csv_versefile').toString() == u'':
                    QtGui.QMessageBox.critical(self,
                        self.trUtf8('Invalid Verse File'),
                        self.trUtf8('You need to specify a file of Bible '
                            'verses to import.'),
                        QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                    self.CsvVerseLocationEdit.setFocus()
                    return False
            elif self.field(u'source_format').toInt()[0] == BibleFormat.OpenSong:
                if self.field(u'opensong_file').toString() == u'':
                    QtGui.QMessageBox.critical(self,
                        self.trUtf8('Invalid OpenSong Bible'),
                        self.trUtf8('You need to specify an OpenSong Bible '
                            'file to import.'),
                        QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                    self.OpenSongFileEdit.setFocus()
                    return False
            return True
        elif self.currentId() == 2:
            # License details
            if self.field(u'license_version').toString() == u'':
                QtGui.QMessageBox.critical(self,
                    self.trUtf8('Empty Version Name'),
                    self.trUtf8('You need to specify a version name for your '
                        'Bible.'),
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                self.VersionNameEdit.setFocus()
                return False
            elif self.field(u'license_copyright').toString() == u'':
                QtGui.QMessageBox.critical(self,
                    self.trUtf8('Empty Copyright'),
                    self.trUtf8('You need to set a copyright for your Bible! '
                        'Bibles in the Public Domain need to be marked as '
                        'such.'),
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                self.CopyrightEdit.setFocus()
                return False
            elif self.manager.exists(
                     self.field(u'license_version').toString()):
                QtGui.QMessageBox.critical(self,
                    self.trUtf8('Bible Exists'),
                    self.trUtf8('This Bible already exists! Please import '
                        'a different Bible or first delete the existing one.'),
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                self.VersionNameEdit.setFocus()
                return False
            return True
        if self.currentId() == 3:
            # Progress page
            return True

    def onLocationComboBoxChanged(self, index):
        self.BibleComboBox.clear()
        for bible, abbreviation in self.web_bible_list[index].iteritems():
            self.BibleComboBox.addItem(unicode(self.trUtf8(bible)))

    def onOsisFileButtonClicked(self):
        self.getFileName(self.trUtf8('Open OSIS file'),
            self.OSISLocationEdit)

    def onBooksFileButtonClicked(self):
        self.getFileName(self.trUtf8('Open Books CSV file'),
            self.BooksLocationEdit)

    def onCsvVersesFileButtonClicked(self):
        self.getFileName(self.trUtf8('Open Verses CSV file'),
            self.CsvVerseLocationEdit)

    def onOpenSongBrowseButtonClicked(self):
        self.getFileName(self.trUtf8('Open OpenSong Bible'),
            self.OpenSongFileEdit)

    def onCancelButtonClicked(self, checked):
        log.debug('Cancel button pressed!')
        if self.currentId() == 3:
            Receiver.send_message(u'openlpstopimport')

    def onCurrentIdChanged(self, id):
        if id == 3:
            self.preImport()
            self.performImport()
            self.postImport()

    def registerFields(self):
        self.SelectPage.registerField(
            u'source_format', self.FormatComboBox)
        self.SelectPage.registerField(
            u'osis_location', self.OSISLocationEdit)
        self.SelectPage.registerField(
            u'csv_booksfile', self.BooksLocationEdit)
        self.SelectPage.registerField(
            u'csv_versefile', self.CsvVerseLocationEdit)
        self.SelectPage.registerField(
            u'opensong_file', self.OpenSongFileEdit)
        self.SelectPage.registerField(
            u'web_location', self.LocationComboBox)
        self.SelectPage.registerField(
            u'web_biblename', self.BibleComboBox)
        self.SelectPage.registerField(
            u'proxy_server', self.AddressEdit)
        self.SelectPage.registerField(
            u'proxy_username', self.UsernameEdit)
        self.SelectPage.registerField(
            u'proxy_password', self.PasswordEdit)
        self.LicenseDetailsPage.registerField(
            u'license_version', self.VersionNameEdit)
        self.LicenseDetailsPage.registerField(
            u'license_copyright', self.CopyrightEdit)
        self.LicenseDetailsPage.registerField(
            u'license_permission', self.PermissionEdit)

    def setDefaults(self):
        self.setField(u'source_format', QtCore.QVariant(0))
        self.setField(u'osis_location', QtCore.QVariant(''))
        self.setField(u'csv_booksfile', QtCore.QVariant(''))
        self.setField(u'csv_versefile', QtCore.QVariant(''))
        self.setField(u'opensong_file', QtCore.QVariant(''))
        self.setField(u'web_location', QtCore.QVariant(DownloadLocation.Crosswalk))
        self.setField(u'web_biblename', QtCore.QVariant(self.BibleComboBox))
        self.setField(u'proxy_server',
            QtCore.QVariant(self.config.get_config(u'proxy address', '')))
        self.setField(u'proxy_username',
            QtCore.QVariant(self.config.get_config(u'proxy username','')))
        self.setField(u'proxy_password',
            QtCore.QVariant(self.config.get_config(u'proxy password','')))
        self.setField(u'license_version', QtCore.QVariant(self.VersionNameEdit))
        self.setField(u'license_copyright', QtCore.QVariant(self.CopyrightEdit))
        self.setField(u'license_permission', QtCore.QVariant(self.PermissionEdit))
        self.onLocationComboBoxChanged(DownloadLocation.Crosswalk)

    def loadWebBibles(self):
        """
        Load the list of Crosswalk and BibleGateway bibles.
        """
        #Load and store Crosswalk Bibles
        filepath = AppLocation.get_directory(AppLocation.PluginsDir)
        filepath = os.path.join(filepath, u'bibles', u'resources')
        fbibles = None
        try:
            self.web_bible_list[DownloadLocation.Crosswalk] = {}
            books_file = open(os.path.join(filepath, u'crosswalkbooks.csv'), 'r')
            dialect = csv.Sniffer().sniff(books_file.read(1024))
            books_file.seek(0)
            books_reader = csv.reader(books_file, dialect)
            for line in books_reader:
                self.web_bible_list[DownloadLocation.Crosswalk][line[0]] = \
                    unicode(line[1], u'utf-8').strip()
        except:
            log.exception(u'Crosswalk resources missing')
        finally:
            if books_file:
                books_file.close()
        #Load and store BibleGateway Bibles
        try:
            self.web_bible_list[DownloadLocation.BibleGateway] = {}
            books_file = open(os.path.join(filepath, u'biblegateway.csv'), 'r')
            dialect = csv.Sniffer().sniff(books_file.read(1024))
            books_file.seek(0)
            books_reader = csv.reader(books_file, dialect)
            for line in books_reader:
                self.web_bible_list[DownloadLocation.BibleGateway][line[0]] = \
                    unicode(line[1], u'utf-8').strip()
        except:
            log.exception(u'Biblegateway resources missing')
        finally:
            if books_file:
                books_file.close()

    def getFileName(self, title, editbox):
        filename = QtGui.QFileDialog.getOpenFileName(self, title,
            self.config.get_last_dir(1))
        if filename:
            editbox.setText(filename)
            self.config.set_last_dir(filename, 1)

    def incrementProgressBar(self, status_text):
        log.debug(u'IncrementBar %s', status_text)
        self.ImportProgressLabel.setText(status_text)
        self.ImportProgressBar.setValue(self.ImportProgressBar.value() + 1)
        Receiver.send_message(u'process_events')

    def preImport(self):
        self.finishButton.setVisible(False)
        self.ImportProgressBar.setMinimum(0)
        self.ImportProgressBar.setMaximum(1188)
        self.ImportProgressBar.setValue(0)
        self.ImportProgressLabel.setText(self.trUtf8('Starting import...'))
        Receiver.send_message(u'process_events')

    def performImport(self):
        bible_type = self.field(u'source_format').toInt()[0]
        importer = None
        if bible_type == BibleFormat.OSIS:
            # Import an OSIS bible
            importer = self.manager.import_bible(BibleFormat.OSIS,
                name=unicode(self.field(u'license_version').toString()),
                filename=unicode(self.field(u'osis_location').toString())
            )
        elif bible_type == BibleFormat.CSV:
            # Import a CSV bible
            importer = self.manager.import_bible(BibleFormat.CSV,
                name=unicode(self.field(u'license_version').toString()),
                booksfile=self.field(u'csv_booksfile').toString(),
                versefile=self.field(u'csv_versefile').toString()
            )
        elif bible_type == BibleFormat.OpenSong:
            # Import an OpenSong bible
            importer = self.manager.import_bible(BibleFormat.OpenSong,
                name=unicode(self.field(u'license_version').toString()),
                filename=self.field(u'opensong_file').toString()
            )
        elif bible_type == BibleFormat.WebDownload:
            # Import a bible from the web
            self.ImportProgressBar.setMaximum(1)
            download_location = self.field(u'web_location').toInt()[0]
            if download_location == DownloadLocation.Crosswalk:
                bible = self.web_bible_list[DownloadLocation.Crosswalk][
                    unicode(self.BibleComboBox.currentText(), u'utf8')]
            elif download_location == DownloadLocation.BibleGateway:
                bible = self.web_bible_list[DownloadLocation.BibleGateway][
                    self.BibleComboBox.currentText()]
            importer = self.manager.import_bible(BibleFormat.WebDownload,
                name=unicode(self.field(u'license_version').toString(), u'utf8'),
                download_source=DownloadLocation.get_name(download_location),
                download_name=bible,
                proxy_server=unicode(self.field(u'proxy_server').toString(), u'utf8'),
                proxy_username=unicode(self.field(u'proxy_username').toString(), u'utf8'),
                proxy_password=unicode(self.field(u'proxy_password').toString(), u'utf8')
            )
        success = importer.do_import()
        if success:
            self.manager.save_meta_data(
                unicode(self.field(u'license_version').toString()),
                unicode(self.field(u'license_version').toString()),
                unicode(self.field(u'license_copyright').toString()),
                unicode(self.field(u'license_permission').toString())
            )
            self.manager.reload_bibles()
            self.ImportProgressLabel.setText(self.trUtf8('Finished import.'))
        else:
            self.ImportProgressLabel.setText(
                self.trUtf8('Your Bible import failed.'))
            importer.delete()

    def postImport(self):
        self.ImportProgressBar.setValue(self.ImportProgressBar.maximum())
        self.finishButton.setVisible(True)
        self.cancelButton.setVisible(False)
        Receiver.send_message(u'process_events')
