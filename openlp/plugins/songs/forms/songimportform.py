# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
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

import logging
import os

from PyQt4 import QtCore, QtGui

from songimportwizard import Ui_SongImportWizard
from openlp.core.lib import Receiver, SettingsManager, translate
from openlp.plugins.songs.lib.importer import SongFormat

log = logging.getLogger(__name__)

class SongImportForm(QtGui.QWizard, Ui_SongImportWizard):
    """
    This is the Song Import Wizard, which allows easy importing of Songs
    into OpenLP from other formats like OpenLyrics, OpenSong and CCLI.
    """
    log.info(u'SongImportForm loaded')

    def __init__(self, parent, plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        ``parent``
            The QWidget-derived parent of the wizard.

        ``plugin``
            The songs plugin.
        """
        QtGui.QWizard.__init__(self, parent)
        self.setupUi(self)
        self.registerFields()
        self.finishButton = self.button(QtGui.QWizard.FinishButton)
        self.cancelButton = self.button(QtGui.QWizard.CancelButton)
        if not SongFormat.get_availability(SongFormat.OpenLP1):
            self.openLP1DisabledWidget.setVisible(True)
            self.openLP1ImportWidget.setVisible(False)
        if not SongFormat.get_availability(SongFormat.SongsOfFellowship):
            self.songsOfFellowshipDisabledWidget.setVisible(True)
            self.songsOfFellowshipImportWidget.setVisible(False)
        if not SongFormat.get_availability(SongFormat.Generic):
            self.genericDisabledWidget.setVisible(True)
            self.genericImportWidget.setVisible(False)
        self.plugin = plugin
        QtCore.QObject.connect(self.openLP2BrowseButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenLP2BrowseButtonClicked)
        QtCore.QObject.connect(self.openLP1BrowseButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenLP1BrowseButtonClicked)
        QtCore.QObject.connect(self.openLyricsAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenLyricsAddButtonClicked)
        QtCore.QObject.connect(self.openLyricsRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenLyricsRemoveButtonClicked)
        QtCore.QObject.connect(self.openSongAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenSongAddButtonClicked)
        QtCore.QObject.connect(self.openSongRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onOpenSongRemoveButtonClicked)
        QtCore.QObject.connect(self.wordsOfWorshipAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onWordsOfWorshipAddButtonClicked)
        QtCore.QObject.connect(self.wordsOfWorshipRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onWordsOfWorshipRemoveButtonClicked)
        QtCore.QObject.connect(self.ccliAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onCCLIAddButtonClicked)
        QtCore.QObject.connect(self.ccliRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onCCLIRemoveButtonClicked)
        QtCore.QObject.connect(self.songsOfFellowshipAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onSongsOfFellowshipAddButtonClicked)
        QtCore.QObject.connect(self.songsOfFellowshipRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onSongsOfFellowshipRemoveButtonClicked)
        QtCore.QObject.connect(self.genericAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onGenericAddButtonClicked)
        QtCore.QObject.connect(self.genericRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onGenericRemoveButtonClicked)
        QtCore.QObject.connect(self.ewBrowseButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onEWBrowseButtonClicked)
        QtCore.QObject.connect(self.songBeamerAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onSongBeamerAddButtonClicked)
        QtCore.QObject.connect(self.songBeamerRemoveButton,
            QtCore.SIGNAL(u'clicked()'),
            self.onSongBeamerRemoveButtonClicked)
        QtCore.QObject.connect(self,
            QtCore.SIGNAL(u'currentIdChanged(int)'),
            self.onCurrentIdChanged)

    def exec_(self):
        """
        Run the wizard.
        """
        self.setDefaults()
        return QtGui.QWizard.exec_(self)

    def reject(self):
        """
        Stop the import on cancel button, close button or ESC key.
        """
        log.debug(u'Import canceled by user.')
        if self.currentPage() == self.importPage:
            Receiver.send_message(u'songs_stop_import')
        self.done(QtGui.QDialog.Rejected)

    def validateCurrentPage(self):
        """
        Validate the current page before moving on to the next page.
        """
        if self.currentPage() == self.welcomePage:
            return True
        elif self.currentPage() == self.sourcePage:
            source_format = self.formatComboBox.currentIndex()
            if source_format == SongFormat.OpenLP2:
                if self.openLP2FilenameEdit.text().isEmpty():
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No OpenLP 2.0 Song Database Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to select an OpenLP 2.0 song database '
                        'file to import from.'))
                    self.openLP2BrowseButton.setFocus()
                    return False
            elif source_format == SongFormat.OpenLP1:
                if self.openLP1FilenameEdit.text().isEmpty():
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No openlp.org 1.x Song Database Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to select an openlp.org 1.x song '
                        'database file to import from.'))
                    self.openLP1BrowseButton.setFocus()
                    return False
            elif source_format == SongFormat.OpenLyrics:
                if self.openLyricsFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No OpenLyrics Files Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one OpenLyrics '
                        'song file to import from.'))
                    self.openLyricsAddButton.setFocus()
                    return False
            elif source_format == SongFormat.OpenSong:
                if self.openSongFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No OpenSong Files Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one OpenSong '
                        'song file to import from.'))
                    self.openSongAddButton.setFocus()
                    return False
            elif source_format == SongFormat.WordsOfWorship:
                if self.wordsOfWorshipFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No Words of Worship Files Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one Words of Worship '
                        'file to import from.'))
                    self.wordsOfWorshipAddButton.setFocus()
                    return False
            elif source_format == SongFormat.CCLI:
                if self.ccliFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No CCLI Files Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one CCLI file '
                        'to import from.'))
                    self.ccliAddButton.setFocus()
                    return False
            elif source_format == SongFormat.SongsOfFellowship:
                if self.songsOfFellowshipFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No Songs of Fellowship File Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one Songs of Fellowship '
                        'file to import from.'))
                    self.songsOfFellowshipAddButton.setFocus()
                    return False
            elif source_format == SongFormat.Generic:
                if self.genericFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No Document/Presentation Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one document or '
                        'presentation file to import from.'))
                    self.genericAddButton.setFocus()
                    return False
            elif source_format == SongFormat.EasyWorship:
                if self.ewFilenameEdit.text().isEmpty():
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No EasyWorship Song Database Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to select an EasyWorship song database '
                        'file to import from.'))
                    self.ewBrowseButton.setFocus()
                    return False
            elif source_format == SongFormat.SongBeamer:
                if self.songBeamerFileListWidget.count() == 0:
                    QtGui.QMessageBox.critical(self,
                        translate('SongsPlugin.ImportWizardForm',
                        'No SongBeamer File Selected'),
                        translate('SongsPlugin.ImportWizardForm',
                        'You need to add at least one SongBeamer '
                        'file to import from.'))
                    self.songBeamerAddButton.setFocus()
                    return False
            return True
        elif self.currentPage() == self.importPage:
            return True

    def getFileName(self, title, editbox, filters=u''):
        """
        Opens a QFileDialog and writes the filename to the given editbox.

        ``title``
            The title of the dialog (unicode).

        ``editbox``
            A editbox (QLineEdit).

        ``filters``
            The file extension filters. It should contain the file descriptions
            as well as the file extensions. For example::

                u'OpenLP 2.0 Databases (*.sqlite)'
        """
        if filters:
            filters += u';;'
        filters += u'%s (*)' % translate('SongsPlugin.ImportWizardForm',
            'All Files')
        filename = QtGui.QFileDialog.getOpenFileName(self, title,
            SettingsManager.get_last_dir(self.plugin.settingsSection, 1),
            filters)
        if filename:
            editbox.setText(filename)
            SettingsManager.set_last_dir(self.plugin.settingsSection,
                os.path.split(unicode(filename))[0], 1)

    def getFiles(self, title, listbox, filters=u''):
        """
        Opens a QFileDialog and writes the filenames to the given listbox.

        ``title``
            The title of the dialog (unicode).

        ``listbox``
            A listbox (QListWidget).

        ``filters``
            The file extension filters. It should contain the file descriptions
            as well as the file extensions. For example::

                u'SongBeamer files (*.sng)'
        """
        if filters:
            filters += u';;'
        filters += u'%s (*)' % translate('SongsPlugin.ImportWizardForm',
            'All Files')
        filenames = QtGui.QFileDialog.getOpenFileNames(self, title,
            SettingsManager.get_last_dir(self.plugin.settingsSection, 1),
            filters)
        if filenames:
            listbox.addItems(filenames)
            SettingsManager.set_last_dir(
                self.plugin.settingsSection,
                os.path.split(unicode(filenames[0]))[0], 1)

    def getListOfFiles(self, listbox):
        files = []
        for row in range(0, listbox.count()):
            files.append(unicode(listbox.item(row).text()))
        return files

    def removeSelectedItems(self, listbox):
        for item in listbox.selectedItems():
            item = listbox.takeItem(listbox.row(item))
            del item

    def onOpenLP2BrowseButtonClicked(self):
        self.getFileName(
            translate('SongsPlugin.ImportWizardForm',
            'Select OpenLP 2.0 Database File'),
            self.openLP2FilenameEdit, u'%s (*.sqlite)'
            % (translate('SongsPlugin.ImportWizardForm',
            'OpenLP 2.0 Databases'))
        )

    def onOpenLP1BrowseButtonClicked(self):
        self.getFileName(
            translate('SongsPlugin.ImportWizardForm',
            'Select openlp.org 1.x Database File'),
            self.openLP1FilenameEdit, u'%s (*.olp)'
            % translate('SongsPlugin.ImportWizardForm',
            'openlp.org v1.x Databases')
        )

    def onOpenLyricsAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select OpenLyrics Files'),
            self.openLyricsFileListWidget
        )

    def onOpenLyricsRemoveButtonClicked(self):
        self.removeSelectedItems(self.openLyricsFileListWidget)

    def onOpenSongAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Open Song Files'),
            self.openSongFileListWidget
        )

    def onOpenSongRemoveButtonClicked(self):
        self.removeSelectedItems(self.openSongFileListWidget)

    def onWordsOfWorshipAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Words of Worship Files'),
            self.wordsOfWorshipFileListWidget, u'%s (*.wsg *.wow-song)'
            % translate('SongsPlugin.ImportWizardForm',
            'Words Of Worship Song Files')
        )

    def onWordsOfWorshipRemoveButtonClicked(self):
        self.removeSelectedItems(self.wordsOfWorshipFileListWidget)

    def onCCLIAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select CCLI Files'),
            self.ccliFileListWidget
        )

    def onCCLIRemoveButtonClicked(self):
        self.removeSelectedItems(self.ccliFileListWidget)

    def onSongsOfFellowshipAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Songs of Fellowship Files'),
            self.songsOfFellowshipFileListWidget, u'%s (*.rtf)'
            % translate('SongsPlugin.ImportWizardForm',
            'Songs Of Felloship Song Files')
        )

    def onSongsOfFellowshipRemoveButtonClicked(self):
        self.removeSelectedItems(self.songsOfFellowshipFileListWidget)

    def onGenericAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Document/Presentation Files'),
            self.genericFileListWidget
        )

    def onGenericRemoveButtonClicked(self):
        self.removeSelectedItems(self.genericFileListWidget)

    def onEWBrowseButtonClicked(self):
        self.getFileName(
            translate('SongsPlugin.ImportWizardForm',
            'Select EasyWorship Database File'),
            self.ewFilenameEdit
        )

    def onSongBeamerAddButtonClicked(self):
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select SongBeamer Files'),
            self.songBeamerFileListWidget, u'%s (*.sng)' %
            translate('SongsPlugin.ImportWizardForm', 'SongBeamer files')
        )

    def onSongBeamerRemoveButtonClicked(self):
        self.removeSelectedItems(self.songBeamerFileListWidget)

    def onCurrentIdChanged(self, id):
        if self.page(id) == self.importPage:
            self.preImport()
            self.performImport()
            self.postImport()

    def registerFields(self):
        pass

    def setDefaults(self):
        self.restart()
        self.finishButton.setVisible(False)
        self.cancelButton.setVisible(True)
        self.formatComboBox.setCurrentIndex(0)
        self.openLP2FilenameEdit.setText(u'')
        self.openLP1FilenameEdit.setText(u'')
        self.openLyricsFileListWidget.clear()
        self.openSongFileListWidget.clear()
        self.wordsOfWorshipFileListWidget.clear()
        self.ccliFileListWidget.clear()
        self.songsOfFellowshipFileListWidget.clear()
        self.genericFileListWidget.clear()
        self.ewFilenameEdit.setText(u'')
        self.songBeamerFileListWidget.clear()
        #self.csvFilenameEdit.setText(u'')

    def incrementProgressBar(self, status_text, increment=1):
        log.debug(u'IncrementBar %s', status_text)
        if status_text:
            self.importProgressLabel.setText(status_text)
        if increment > 0:
            self.importProgressBar.setValue(self.importProgressBar.value() +
                increment)
        Receiver.send_message(u'openlp_process_events')

    def preImport(self):
        self.finishButton.setVisible(False)
        self.importProgressBar.setMinimum(0)
        self.importProgressBar.setMaximum(1188)
        self.importProgressBar.setValue(0)
        self.importProgressLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Starting import...'))
        Receiver.send_message(u'openlp_process_events')

    def performImport(self):
        """
        Perform the actual import. This method pulls in the correct importer
        class, and then runs the ``do_import`` method of the importer to do
        the actual importing.
        """
        source_format = self.formatComboBox.currentIndex()
        importer = None
        if source_format == SongFormat.OpenLP2:
            # Import an OpenLP 2.0 database
            importer = self.plugin.importSongs(SongFormat.OpenLP2,
                filename=unicode(self.openLP2FilenameEdit.text())
            )
        elif source_format == SongFormat.OpenLP1:
            # Import an openlp.org database
            importer = self.plugin.importSongs(SongFormat.OpenLP1,
                filename=unicode(self.openLP1FilenameEdit.text())
            )
        elif source_format == SongFormat.OpenLyrics:
            # Import OpenLyrics songs
            importer = self.plugin.importSongs(SongFormat.OpenLyrics,
                filenames=self.getListOfFiles(self.openLyricsFileListWidget)
            )
        elif source_format == SongFormat.OpenSong:
            # Import OpenSong songs
            importer = self.plugin.importSongs(SongFormat.OpenSong,
                filenames=self.getListOfFiles(self.openSongFileListWidget)
            )
        elif source_format == SongFormat.WordsOfWorship:
            # Import Words Of Worship songs
            importer = self.plugin.importSongs(SongFormat.WordsOfWorship,
                filenames=self.getListOfFiles(
                    self.wordsOfWorshipFileListWidget)
            )
        elif source_format == SongFormat.CCLI:
            # Import Words Of Worship songs
            importer = self.plugin.importSongs(SongFormat.CCLI,
                filenames=self.getListOfFiles(self.ccliFileListWidget)
            )
        elif source_format == SongFormat.SongsOfFellowship:
            # Import a Songs of Fellowship RTF file
            importer = self.plugin.importSongs(SongFormat.SongsOfFellowship,
                filenames=self.getListOfFiles(
                    self.songsOfFellowshipFileListWidget)
            )
        elif source_format == SongFormat.Generic:
            # Import a generic document or presentatoin
            importer = self.plugin.importSongs(SongFormat.Generic,
                filenames=self.getListOfFiles(self.genericFileListWidget)
            )
        elif source_format == SongFormat.EasyWorship:
            # Import an OpenLP 2.0 database
            importer = self.plugin.importSongs(SongFormat.EasyWorship,
                filename=unicode(self.ewFilenameEdit.text())
            )
        elif source_format == SongFormat.SongBeamer:
            # Import SongBeamer songs
            importer = self.plugin.importSongs(SongFormat.SongBeamer,
                filenames=self.getListOfFiles(
                    self.songBeamerFileListWidget)
            )
        if importer.do_import():
            # reload songs
            self.importProgressLabel.setText(
                translate('SongsPlugin.SongImportForm', 'Finished import.'))
        else:
            self.importProgressLabel.setText(
                translate('SongsPlugin.SongImportForm',
                'Your song import failed.'))

    def postImport(self):
        self.importProgressBar.setValue(self.importProgressBar.maximum())
        self.finishButton.setVisible(True)
        self.cancelButton.setVisible(False)
        Receiver.send_message(u'openlp_process_events')
