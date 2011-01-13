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
"""
The song import functions for OpenLP.
"""
import logging
import os

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Receiver, SettingsManager, translate
from openlp.core.ui.wizard import OpenLPWizard
from openlp.plugins.songs.lib.importer import SongFormat

log = logging.getLogger(__name__)

class SongImportForm(OpenLPWizard):
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
        OpenLPWizard.__init__(self, parent, plugin, u'songImportWizard',
            u':/wizards/wizard_importsong.bmp')

    def setupUi(self, image):
        """
        Set up the song wizard UI.
        """
        OpenLPWizard.setupUi(self, image)
        self.formatStack.setCurrentIndex(0)
        QtCore.QObject.connect(self.formatComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'),
            self.formatStack.setCurrentIndex)

    def customInit(self):
        """
        Song wizard specific initialisation.
        """
        if not SongFormat.get_availability(SongFormat.OpenLP1):
            self.openLP1DisabledWidget.setVisible(True)
            self.openLP1ImportWidget.setVisible(False)
        if not SongFormat.get_availability(SongFormat.SongsOfFellowship):
            self.songsOfFellowshipDisabledWidget.setVisible(True)
            self.songsOfFellowshipImportWidget.setVisible(False)
        if not SongFormat.get_availability(SongFormat.Generic):
            self.genericDisabledWidget.setVisible(True)
            self.genericImportWidget.setVisible(False)

    def customSignals(self):
        """
        Song wizard specific signals.
        """
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

    def addCustomPages(self):
        """
        Add song wizard specific pages.
        """
        # Source Page
        self.sourcePage = QtGui.QWizardPage()
        self.sourcePage.setObjectName(u'SourcePage')
        self.sourceLayout = QtGui.QVBoxLayout(self.sourcePage)
        self.sourceLayout.setObjectName(u'SourceLayout')
        self.formatLayout = QtGui.QFormLayout()
        self.formatLayout.setObjectName(u'FormatLayout')
        self.formatLabel = QtGui.QLabel(self.sourcePage)
        self.formatLabel.setObjectName(u'FormatLabel')
        self.formatComboBox = QtGui.QComboBox(self.sourcePage)
        self.formatComboBox.setObjectName(u'FormatComboBox')
        self.formatLayout.addRow(self.formatLabel, self.formatComboBox)
        self.formatSpacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Minimum)
        self.formatLayout.setItem(1, QtGui.QFormLayout.LabelRole,
            self.formatSpacer)
        self.sourceLayout.addLayout(self.formatLayout)
        self.formatStack = QtGui.QStackedLayout()
        self.formatStack.setObjectName(u'FormatStack')
        # OpenLP 2.0
        self.addSingleFileSelectItem(u'openLP2')
        # openlp.org 1.x
        self.addSingleFileSelectItem(u'openLP1', None, True)
        # OpenLyrics
        self.addMultiFileSelectItem(u'openLyrics', u'OpenLyrics', True)
        # Open Song
        self.addMultiFileSelectItem(u'openSong', u'OpenSong')
        # Words of Worship
        self.addMultiFileSelectItem(u'wordsOfWorship')
        # CCLI File import
        self.addMultiFileSelectItem(u'ccli')
        # Songs of Fellowship
        self.addMultiFileSelectItem(u'songsOfFellowship', None, True)
        # Generic Document/Presentation import
        self.addMultiFileSelectItem(u'generic', None, True)
        # EasyWorship
        self.addSingleFileSelectItem(u'ew')
        # Words of Worship
        self.addMultiFileSelectItem(u'songBeamer')
#        Commented out for future use.
#        self.addSingleFileSelectItem(u'csv', u'CSV')
        self.sourceLayout.addLayout(self.formatStack)
        self.addPage(self.sourcePage)

    def retranslateUi(self):
        """
        Song wizard localisation.
        """
        self.setWindowTitle(
            translate('SongsPlugin.ImportWizardForm', 'Song Import Wizard'))
        self.titleLabel.setText(
            u'<span style="font-size:14pt; font-weight:600;">%s</span>' % \
            translate('SongsPlugin.ImportWizardForm',
                'Welcome to the Song Import Wizard'))
        self.informationLabel.setText(
            translate('SongsPlugin.ImportWizardForm',
                'This wizard will help you to import songs from a variety of '
                'formats. Click the next button below to start the process by '
                'selecting a format to import from.'))
        self.sourcePage.setTitle(
            translate('SongsPlugin.ImportWizardForm', 'Select Import Source'))
        self.sourcePage.setSubTitle(
            translate('SongsPlugin.ImportWizardForm',
            'Select the import format, and where to import from.'))
        self.formatLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Format:'))
        self.formatComboBox.setItemText(0,
            translate('SongsPlugin.ImportWizardForm', 'OpenLP 2.0'))
        self.formatComboBox.setItemText(1,
            translate('SongsPlugin.ImportWizardForm', 'openlp.org 1.x'))
        self.formatComboBox.setItemText(2,
            translate('SongsPlugin.ImportWizardForm', 'OpenLyrics'))
        self.formatComboBox.setItemText(3,
            translate('SongsPlugin.ImportWizardForm', 'OpenSong'))
        self.formatComboBox.setItemText(4,
            translate('SongsPlugin.ImportWizardForm', 'Words of Worship'))
        self.formatComboBox.setItemText(5,
            translate('SongsPlugin.ImportWizardForm', 'CCLI/SongSelect'))
        self.formatComboBox.setItemText(6,
            translate('SongsPlugin.ImportWizardForm', 'Songs of Fellowship'))
        self.formatComboBox.setItemText(7,
            translate('SongsPlugin.ImportWizardForm',
            'Generic Document/Presentation'))
        self.formatComboBox.setItemText(8,
            translate('SongsPlugin.ImportWizardForm', 'EasyWorship'))
        self.formatComboBox.setItemText(9,
            translate('SongsPlugin.ImportWizardForm', 'SongBeamer'))
#        self.formatComboBox.setItemText(9,
#            translate('SongsPlugin.ImportWizardForm', 'CSV'))
        self.openLP2FilenameLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Filename:'))
        self.openLP2BrowseButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Browse...'))
        self.openLP1FilenameLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Filename:'))
        self.openLP1BrowseButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Browse...'))
        self.openLP1DisabledLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'The openlp.org 1.x '
            'importer has been disabled due to a missing Python module. If '
            'you want to use this importer, you will need to install the '
            '"python-sqlite" module.'))
        self.openLyricsAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.openLyricsRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
        self.openLyricsDisabledLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'The OpenLyrics '
            'importer has not yet been developed, but as you can see, we are '
            'still intending to do so. Hopefully it will be in the next '
            'release.'))
        self.openSongAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.openSongRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
        self.wordsOfWorshipAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.wordsOfWorshipRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
        self.ccliAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.ccliRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
        self.songsOfFellowshipAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.songsOfFellowshipRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
        self.songsOfFellowshipDisabledLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'The Songs of '
            'Fellowship importer has been disabled because OpenLP cannot '
            'find OpenOffice.org on your computer.'))
        self.genericAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.genericRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
        self.genericDisabledLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'The generic document/'
            'presentation importer has been disabled because OpenLP cannot '
            'find OpenOffice.org on your computer.'))
        self.ewFilenameLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Filename:'))
        self.ewBrowseButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Browse...'))
        self.songBeamerAddButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
        self.songBeamerRemoveButton.setText(
            translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
#        self.csvFilenameLabel.setText(
#            translate('SongsPlugin.ImportWizardForm', 'Filename:'))
#        self.csvBrowseButton.setText(
#            translate('SongsPlugin.ImportWizardForm', 'Browse...'))
        self.progressPage.setTitle(
            translate('SongsPlugin.ImportWizardForm', 'Importing'))
        self.progressPage.setSubTitle(
            translate('SongsPlugin.ImportWizardForm',
                'Please wait while your songs are imported.'))
        self.progressLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Ready.'))
        self.progressBar.setFormat(
            translate('SongsPlugin.ImportWizardForm', '%p%'))
        # Align all QFormLayouts towards each other.
        width = max(self.formatLabel.minimumSizeHint().width(),
            self.openLP2FilenameLabel.minimumSizeHint().width())
        self.formatSpacer.changeSize(width, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Fixed)
        self.openLP2FormLabelSpacer.changeSize(width, 0,
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.openLP1FormLabelSpacer.changeSize(width, 0,
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ewFormLabelSpacer.changeSize(width, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Fixed)
#        self.csvFormLabelSpacer.changeSize(width, 0, QtGui.QSizePolicy.Fixed,
#            QtGui.QSizePolicy.Fixed)

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
        elif self.currentPage() == self.progressPage:
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
        """
        Return a list of file from the listbox
        """
        files = []
        for row in range(0, listbox.count()):
            files.append(unicode(listbox.item(row).text()))
        return files

    def removeSelectedItems(self, listbox):
        """
        Remove selected listbox items
        """
        for item in listbox.selectedItems():
            item = listbox.takeItem(listbox.row(item))
            del item

    def onOpenLP2BrowseButtonClicked(self):
        """
        Get OpenLP v2 song database file
        """
        self.getFileName(
            translate('SongsPlugin.ImportWizardForm',
            'Select OpenLP 2.0 Database File'),
            self.openLP2FilenameEdit, u'%s (*.sqlite)'
            % (translate('SongsPlugin.ImportWizardForm',
            'OpenLP 2.0 Databases'))
        )

    def onOpenLP1BrowseButtonClicked(self):
        """
        Get OpenLP v1 song database file
        """
        self.getFileName(
            translate('SongsPlugin.ImportWizardForm',
            'Select openlp.org 1.x Database File'),
            self.openLP1FilenameEdit, u'%s (*.olp)'
            % translate('SongsPlugin.ImportWizardForm',
            'openlp.org v1.x Databases')
        )

    def onOpenLyricsAddButtonClicked(self):
        """
        Get OpenLyrics song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select OpenLyrics Files'),
            self.openLyricsFileListWidget
        )

    def onOpenLyricsRemoveButtonClicked(self):
        """
        Remove selected OpenLyrics files from the import list
        """
        self.removeSelectedItems(self.openLyricsFileListWidget)

    def onOpenSongAddButtonClicked(self):
        """
        Get OpenSong song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm', 'Select Open Song Files'),
            self.openSongFileListWidget
        )

    def onOpenSongRemoveButtonClicked(self):
        """
        Remove selected OpenSong files from the import list
        """
        self.removeSelectedItems(self.openSongFileListWidget)

    def onWordsOfWorshipAddButtonClicked(self):
        """
        Get Words of Worship song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Words of Worship Files'),
            self.wordsOfWorshipFileListWidget, u'%s (*.wsg *.wow-song)'
            % translate('SongsPlugin.ImportWizardForm',
            'Words Of Worship Song Files')
        )

    def onWordsOfWorshipRemoveButtonClicked(self):
        """
        Remove selected Words of Worship files from the import list
        """
        self.removeSelectedItems(self.wordsOfWorshipFileListWidget)

    def onCCLIAddButtonClicked(self):
        """
        Get CCLI song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select CCLI Files'),
            self.ccliFileListWidget
        )

    def onCCLIRemoveButtonClicked(self):
        """
        Remove selected CCLI files from the import list
        """
        self.removeSelectedItems(self.ccliFileListWidget)

    def onSongsOfFellowshipAddButtonClicked(self):
        """
        Get Songs of Fellowship song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Songs of Fellowship Files'),
            self.songsOfFellowshipFileListWidget, u'%s (*.rtf)'
            % translate('SongsPlugin.ImportWizardForm',
            'Songs Of Felloship Song Files')
        )

    def onSongsOfFellowshipRemoveButtonClicked(self):
        """
        Remove selected Songs of Fellowship files from the import list
        """
        self.removeSelectedItems(self.songsOfFellowshipFileListWidget)

    def onGenericAddButtonClicked(self):
        """
        Get song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select Document/Presentation Files'),
            self.genericFileListWidget
        )

    def onGenericRemoveButtonClicked(self):
        """
        Remove selected files from the import list
        """
        self.removeSelectedItems(self.genericFileListWidget)

    def onEWBrowseButtonClicked(self):
        """
        Get EasyWorship song database files
        """
        self.getFileName(
            translate('SongsPlugin.ImportWizardForm',
            'Select EasyWorship Database File'),
            self.ewFilenameEdit
        )

    def onSongBeamerAddButtonClicked(self):
        """
        Get SongBeamer song database files
        """
        self.getFiles(
            translate('SongsPlugin.ImportWizardForm',
            'Select SongBeamer Files'),
            self.songBeamerFileListWidget, u'%s (*.sng)' %
            translate('SongsPlugin.ImportWizardForm', 'SongBeamer files')
        )

    def onSongBeamerRemoveButtonClicked(self):
        """
        Remove selected SongBeamer files from the import list
        """
        self.removeSelectedItems(self.songBeamerFileListWidget)

    def registerFields(self):
        """
        Register song import wizard fields.
        """
        pass

    def setDefaults(self):
        """
        Set default form values for the song import wizard.
        """
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

    def preWizard(self):
        """
        Perform pre import tasks
        """
        OpenLPWizard.preWizard(self)
        self.progressLabel.setText(
            translate('SongsPlugin.ImportWizardForm', 'Starting import...'))
        Receiver.send_message(u'openlp_process_events')

    def performWizard(self):
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
                filenames=self.getListOfFiles(self.songBeamerFileListWidget)
            )
        if importer.do_import():
            # reload songs
            self.progressLabel.setText(
                translate('SongsPlugin.SongImportForm', 'Finished import.'))
        else:
            self.progressLabel.setText(
                translate('SongsPlugin.SongImportForm',
                'Your song import failed.'))

    def addSingleFileSelectItem(self, prefix, obj_prefix=None,
        can_disable=False):
        if not obj_prefix:
            obj_prefix = prefix
        page = QtGui.QWidget()
        page.setObjectName(obj_prefix + u'Page')
        if can_disable:
            importWidget = self.disablableWidget(page, prefix, obj_prefix)
        else:
            importWidget = page
        importLayout = QtGui.QFormLayout(importWidget)
        importLayout.setMargin(0)
        if can_disable:
            importLayout.setObjectName(obj_prefix + u'ImportLayout')
        else:
            importLayout.setObjectName(obj_prefix + u'Layout')
        filenameLabel = QtGui.QLabel(importWidget)
        filenameLabel.setObjectName(obj_prefix + u'FilenameLabel')
        fileLayout = QtGui.QHBoxLayout()
        fileLayout.setObjectName(obj_prefix + u'FileLayout')
        filenameEdit = QtGui.QLineEdit(importWidget)
        filenameEdit.setObjectName(obj_prefix + u'FilenameEdit')
        fileLayout.addWidget(filenameEdit)
        browseButton = QtGui.QToolButton(importWidget)
        browseButton.setIcon(self.openIcon)
        browseButton.setObjectName(obj_prefix + u'BrowseButton')
        fileLayout.addWidget(browseButton)
        importLayout.addRow(filenameLabel, fileLayout)
        formSpacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Minimum)
        importLayout.setItem(1, QtGui.QFormLayout.LabelRole, formSpacer)
        self.formatStack.addWidget(page)
        setattr(self, prefix + u'Page', page)
        setattr(self, prefix + u'FilenameLabel', filenameLabel)
        setattr(self, prefix + u'FormLabelSpacer', formSpacer)
        setattr(self, prefix + u'FileLayout', fileLayout)
        setattr(self, prefix + u'FilenameEdit', filenameEdit)
        setattr(self, prefix + u'BrowseButton', browseButton)
        if can_disable:
            setattr(self, prefix + u'ImportLayout', importLayout)
        else:
            setattr(self, prefix + u'Layout', importLayout)
        self.formatComboBox.addItem(u'')

    def addMultiFileSelectItem(self, prefix, obj_prefix=None,
        can_disable=False):
        if not obj_prefix:
            obj_prefix = prefix
        page = QtGui.QWidget()
        page.setObjectName(obj_prefix + u'Page')
        if can_disable:
            importWidget = self.disablableWidget(page, prefix, obj_prefix)
        else:
            importWidget = page
        importLayout = QtGui.QVBoxLayout(importWidget)
        importLayout.setMargin(0)
        if can_disable:
            importLayout.setObjectName(obj_prefix + u'ImportLayout')
        else:
            importLayout.setObjectName(obj_prefix + u'Layout')
        fileListWidget = QtGui.QListWidget(importWidget)
        fileListWidget.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        fileListWidget.setObjectName(obj_prefix + u'FileListWidget')
        importLayout.addWidget(fileListWidget)
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.setObjectName(obj_prefix + u'ButtonLayout')
        addButton = QtGui.QPushButton(importWidget)
        addButton.setIcon(self.openIcon)
        addButton.setObjectName(obj_prefix + u'AddButton')
        buttonLayout.addWidget(addButton)
        buttonLayout.addStretch()
        removeButton = QtGui.QPushButton(importWidget)
        removeButton.setIcon(self.deleteIcon)
        removeButton.setObjectName(obj_prefix + u'RemoveButton')
        buttonLayout.addWidget(removeButton)
        importLayout.addLayout(buttonLayout)
        self.formatStack.addWidget(page)
        setattr(self, prefix + u'Page', page)
        setattr(self, prefix + u'FileListWidget', fileListWidget)
        setattr(self, prefix + u'ButtonLayout', buttonLayout)
        setattr(self, prefix + u'AddButton', addButton)
        setattr(self, prefix + u'RemoveButton', removeButton)
        if can_disable:
            setattr(self, prefix + u'ImportLayout', importLayout)
        else:
            setattr(self, prefix + u'Layout', importLayout)
        self.formatComboBox.addItem(u'')

    def disablableWidget(self, page, prefix, obj_prefix):
        layout = QtGui.QVBoxLayout(page)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.setObjectName(obj_prefix + u'Layout')
        disabledWidget = QtGui.QWidget(page)
        disabledWidget.setVisible(False)
        disabledWidget.setObjectName(obj_prefix + u'DisabledWidget')
        disabledLayout = QtGui.QVBoxLayout(disabledWidget)
        disabledLayout.setMargin(0)
        disabledLayout.setObjectName(obj_prefix + u'DisabledLayout')
        disabledLabel = QtGui.QLabel(disabledWidget)
        disabledLabel.setWordWrap(True)
        disabledLabel.setObjectName(obj_prefix + u'DisabledLabel')
        disabledLayout.addWidget(disabledLabel)
        layout.addWidget(disabledWidget)
        importWidget = QtGui.QWidget(page)
        importWidget.setObjectName(obj_prefix + u'ImportWidget')
        layout.addWidget(importWidget)
        setattr(self, prefix + u'Layout', layout)
        setattr(self, prefix + u'DisabledWidget', disabledWidget)
        setattr(self, prefix + u'DisabledLayout', disabledLayout)
        setattr(self, prefix + u'DisabledLabel', disabledLabel)
        setattr(self, prefix + u'ImportWidget', importWidget)
        return importWidget
