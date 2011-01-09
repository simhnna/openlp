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
import time

from PyQt4 import QtCore, QtGui

from openlp.core.lib import MediaManagerItem, Receiver, BaseListWithDnD, \
    ItemCapabilities, translate
from openlp.plugins.bibles.forms import BibleImportForm
from openlp.plugins.bibles.lib import get_reference_match

log = logging.getLogger(__name__)

class BibleListView(BaseListWithDnD):
    """
    Custom list view descendant, required for drag and drop.
    """
    def __init__(self, parent=None):
        self.PluginName = u'Bibles'
        BaseListWithDnD.__init__(self, parent)

    def resizeEvent(self, event):
        self.parent().onListViewResize(event.size().width(),
            event.size().width())


class BibleMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Bibles.
    """
    log.info(u'Bible Media Item loaded')

    def __init__(self, parent, plugin, icon):
        self.IconPath = u'songs/song'
        self.ListViewWithDnD_class = BibleListView
        MediaManagerItem.__init__(self, parent, plugin, icon)
        # Place to store the search results for both bibles.
        self.search_results = {}
        self.second_search_results = {}
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'bibles_load_list'), self.reloadBibles)

    def requiredIcons(self):
        MediaManagerItem.requiredIcons(self)
        self.hasImportIcon = True
        self.hasNewIcon = False
        self.hasEditIcon = False
        self.hasDeleteIcon = False
        self.addToServiceItem = False

    def addEndHeaderBar(self):
        self.searchTabWidget = QtGui.QTabWidget(self)
        self.searchTabWidget.setSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.searchTabWidget.setObjectName(u'SearchTabWidget')
        # Add the Quick Search tab.
        self.quickTab = QtGui.QWidget()
        self.quickTab.setObjectName(u'quickTab')
        self.quickLayout = QtGui.QFormLayout(self.quickTab)
        self.quickLayout.setObjectName(u'quickLayout')
        self.quickVersionLabel = QtGui.QLabel(self.quickTab)
        self.quickVersionLabel.setObjectName(u'quickVersionLabel')
        self.quickVersionComboBox = QtGui.QComboBox(self.quickTab)
        self.quickVersionComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.quickVersionComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.quickVersionComboBox.setObjectName(u'quickVersionComboBox')
        self.quickVersionLabel.setBuddy(self.quickVersionComboBox)
        self.quickLayout.addRow(self.quickVersionLabel,
            self.quickVersionComboBox)
        self.quickSecondLabel = QtGui.QLabel(self.quickTab)
        self.quickSecondLabel.setObjectName(u'quickSecondLabel')
        self.quickSecondComboBox = QtGui.QComboBox(self.quickTab)
        self.quickSecondComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.quickSecondComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.quickSecondComboBox.setObjectName(u'quickSecondComboBox')
        self.quickSecondLabel.setBuddy(self.quickSecondComboBox)
        self.quickLayout.addRow(self.quickSecondLabel, self.quickSecondComboBox)
        self.quickSearchTypeLabel = QtGui.QLabel(self.quickTab)
        self.quickSearchTypeLabel.setObjectName(u'quickSearchTypeLabel')
        self.quickSearchComboBox = QtGui.QComboBox(self.quickTab)
        self.quickSearchComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.quickSearchComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.quickSearchComboBox.setObjectName(u'quickSearchComboBox')
        self.quickSearchTypeLabel.setBuddy(self.quickSearchComboBox)
        self.quickLayout.addRow(self.quickSearchTypeLabel,
            self.quickSearchComboBox)
        self.quickSearchLabel = QtGui.QLabel(self.quickTab)
        self.quickSearchLabel.setObjectName(u'quickSearchLabel')
        self.quickSearchEdit = QtGui.QLineEdit(self.quickTab)
        self.quickSearchEdit.setObjectName(u'quickSearchEdit')
        self.quickSearchLabel.setBuddy(self.quickSearchEdit)
        self.quickLayout.addRow(self.quickSearchLabel, self.quickSearchEdit)
        self.quickClearLabel = QtGui.QLabel(self.quickTab)
        self.quickClearLabel.setObjectName(u'quickClearLabel')
        self.quickClearComboBox = QtGui.QComboBox(self.quickTab)
        self.quickClearComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.quickClearComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.quickClearComboBox.setObjectName(u'quickClearComboBox')
        self.quickLayout.addRow(self.quickClearLabel, self.quickClearComboBox)
        self.quickSearchButtonLayout = QtGui.QHBoxLayout()
        self.quickSearchButtonLayout.setObjectName(u'quickSearchButtonLayout')
        self.quickSearchButtonLayout.addStretch()
        self.quickSearchButton = QtGui.QPushButton(self.quickTab)
        self.quickSearchButton.setObjectName(u'quickSearchButton')
        self.quickSearchButtonLayout.addWidget(self.quickSearchButton)
        self.quickLayout.addRow(self.quickSearchButtonLayout)
        self.quickMessage = QtGui.QLabel(self.quickTab)
        self.quickMessage.setObjectName(u'quickMessage')
        self.quickLayout.addRow(self.quickMessage)
        self.searchTabWidget.addTab(self.quickTab,
            translate('BiblesPlugin.MediaItem', 'Quick'))
        # Add the Advanced Search tab.
        self.advancedTab = QtGui.QWidget()
        self.advancedTab.setObjectName(u'advancedTab')
        self.advancedLayout = QtGui.QGridLayout(self.advancedTab)
        self.advancedLayout.setObjectName(u'advancedLayout')
        self.advancedVersionLabel = QtGui.QLabel(self.advancedTab)
        self.advancedVersionLabel.setObjectName(u'advancedVersionLabel')
        self.advancedLayout.addWidget(self.advancedVersionLabel, 0, 0,
            QtCore.Qt.AlignRight)
        self.advancedVersionComboBox = QtGui.QComboBox(self.advancedTab)
        self.advancedVersionComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.advancedVersionComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.advancedVersionComboBox.setObjectName(u'advancedVersionComboBox')
        self.advancedVersionLabel.setBuddy(self.advancedVersionComboBox)
        self.advancedLayout.addWidget(self.advancedVersionComboBox, 0, 1, 1, 2)
        self.advancedSecondLabel = QtGui.QLabel(self.advancedTab)
        self.advancedSecondLabel.setObjectName(u'advancedSecondLabel')
        self.advancedLayout.addWidget(self.advancedSecondLabel, 1, 0,
            QtCore.Qt.AlignRight)
        self.advancedSecondComboBox = QtGui.QComboBox(self.advancedTab)
        self.advancedSecondComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.advancedSecondComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.advancedSecondComboBox.setObjectName(u'advancedSecondComboBox')
        self.advancedSecondLabel.setBuddy(self.advancedSecondComboBox)
        self.advancedLayout.addWidget(self.advancedSecondComboBox, 1, 1, 1, 2)
        self.advancedBookLabel = QtGui.QLabel(self.advancedTab)
        self.advancedBookLabel.setObjectName(u'advancedBookLabel')
        self.advancedLayout.addWidget(self.advancedBookLabel, 2, 0,
            QtCore.Qt.AlignRight)
        self.advancedBookComboBox = QtGui.QComboBox(self.advancedTab)
        self.advancedBookComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.advancedBookComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.advancedBookComboBox.setObjectName(u'advancedBookComboBox')
        self.advancedBookLabel.setBuddy(self.advancedBookComboBox)
        self.advancedLayout.addWidget(self.advancedBookComboBox, 2, 1, 1, 2)
        self.advancedChapterLabel = QtGui.QLabel(self.advancedTab)
        self.advancedChapterLabel.setObjectName(u'advancedChapterLabel')
        self.advancedLayout.addWidget(self.advancedChapterLabel, 3, 1)
        self.advancedVerseLabel = QtGui.QLabel(self.advancedTab)
        self.advancedVerseLabel.setObjectName(u'advancedVerseLabel')
        self.advancedLayout.addWidget(self.advancedVerseLabel, 3, 2)
        self.advancedFromLabel = QtGui.QLabel(self.advancedTab)
        self.advancedFromLabel.setObjectName(u'advancedFromLabel')
        self.advancedLayout.addWidget(self.advancedFromLabel, 4, 0,
            QtCore.Qt.AlignRight)
        self.advancedFromChapter = QtGui.QComboBox(self.advancedTab)
        self.advancedFromChapter.setObjectName(u'advancedFromChapter')
        self.advancedLayout.addWidget(self.advancedFromChapter, 4, 1)
        self.advancedFromVerse = QtGui.QComboBox(self.advancedTab)
        self.advancedFromVerse.setObjectName(u'advancedFromVerse')
        self.advancedLayout.addWidget(self.advancedFromVerse, 4, 2)
        self.advancedToLabel = QtGui.QLabel(self.advancedTab)
        self.advancedToLabel.setObjectName(u'advancedToLabel')
        self.advancedLayout.addWidget(self.advancedToLabel, 5, 0,
            QtCore.Qt.AlignRight)
        self.advancedToChapter = QtGui.QComboBox(self.advancedTab)
        self.advancedToChapter.setObjectName(u'advancedToChapter')
        self.advancedLayout.addWidget(self.advancedToChapter, 5, 1)
        self.advancedToVerse = QtGui.QComboBox(self.advancedTab)
        self.advancedToVerse.setObjectName(u'advancedToVerse')
        self.advancedLayout.addWidget(self.advancedToVerse, 5, 2)

        self.advancedClearLabel = QtGui.QLabel(self.quickTab)
        self.advancedClearLabel.setObjectName(u'advancedClearLabel')
        self.advancedLayout.addWidget(self.advancedClearLabel, 6, 0,
            QtCore.Qt.AlignRight)
        self.advancedClearComboBox = QtGui.QComboBox(self.quickTab)
        self.advancedClearComboBox.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.advancedClearComboBox.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.advancedClearComboBox.setObjectName(u'advancedClearComboBox')
        self.advancedClearLabel.setBuddy(self.advancedClearComboBox)
        self.advancedLayout.addWidget(self.advancedClearComboBox, 6, 1, 1, 2)
        self.advancedSearchButtonLayout = QtGui.QHBoxLayout()
        self.advancedSearchButtonLayout.setObjectName(
            u'advancedSearchButtonLayout')
        self.advancedSearchButtonLayout.addStretch()
        self.advancedSearchButton = QtGui.QPushButton(self.advancedTab)
        self.advancedSearchButton.setObjectName(u'advancedSearchButton')
        self.advancedSearchButtonLayout.addWidget(self.advancedSearchButton)
        self.advancedLayout.addLayout(
            self.advancedSearchButtonLayout, 7, 0, 1, 3)
        self.advancedMessage = QtGui.QLabel(self.advancedTab)
        self.advancedMessage.setObjectName(u'advancedMessage')
        self.advancedLayout.addWidget(self.advancedMessage, 8, 0, 1, 3)
        self.searchTabWidget.addTab(self.advancedTab,
            translate('BiblesPlugin.MediaItem', 'Advanced'))
        # Add the search tab widget to the page layout.
        self.pageLayout.addWidget(self.searchTabWidget)
        # Combo Boxes
        QtCore.QObject.connect(self.advancedVersionComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedVersionComboBox)
        QtCore.QObject.connect(self.advancedBookComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedBookComboBox)
        QtCore.QObject.connect(self.advancedFromChapter,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedFromChapter)
        QtCore.QObject.connect(self.advancedFromVerse,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedFromVerse)
        QtCore.QObject.connect(self.advancedToChapter,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedToChapter)
        QtCore.QObject.connect(self.quickSearchComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.updateAutoCompleter)
        QtCore.QObject.connect(self.quickVersionComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.updateAutoCompleter)
        # Buttons
        QtCore.QObject.connect(self.advancedSearchButton,
            QtCore.SIGNAL(u'pressed()'), self.onAdvancedSearchButton)
        QtCore.QObject.connect(self.quickSearchButton,
            QtCore.SIGNAL(u'pressed()'), self.onQuickSearchButton)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'config_updated'), self.configUpdated)
        # Other stuff
        QtCore.QObject.connect(self.quickSearchEdit,
            QtCore.SIGNAL(u'returnPressed()'), self.onQuickSearchButton)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'bibles_showprogress'), self.onSearchProgressShow)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'bibles_hideprogress'), self.onSearchProgressHide)

    def addListViewToToolBar(self):
        MediaManagerItem.addListViewToToolBar(self)
        # Progress Bar
        self.SearchProgress = QtGui.QProgressBar(self)
        self.SearchProgress.setFormat('')
        self.SearchProgress.setMinimum(0)
        self.SearchProgress.setMaximum(0)
        self.SearchProgress.setGeometry(self.listView.geometry().left(),
            self.listView.geometry().top(), 81, 23)
        self.SearchProgress.setVisible(False)
        self.SearchProgress.setObjectName(u'SearchProgress')

    def configUpdated(self):
        log.debug(u'configUpdated')
        if QtCore.QSettings().value(self.settingsSection + u'/second bibles',
            QtCore.QVariant(True)).toBool():
            self.advancedSecondLabel.setVisible(True)
            self.advancedSecondComboBox.setVisible(True)
            self.quickSecondLabel.setVisible(True)
            self.quickSecondComboBox.setVisible(True)
        else:
            self.advancedSecondLabel.setVisible(False)
            self.advancedSecondComboBox.setVisible(False)
            self.quickSecondLabel.setVisible(False)
            self.quickSecondComboBox.setVisible(False)

    def retranslateUi(self):
        log.debug(u'retranslateUi')
        self.quickVersionLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Version:'))
        self.quickSecondLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Second:'))
        self.quickSearchTypeLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Search type:'))
        self.quickSearchLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Find:'))
        self.quickSearchButton.setText(
            translate('BiblesPlugin.MediaItem', 'Search'))
        self.quickClearLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Results:'))
        self.advancedVersionLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Version:'))
        self.advancedSecondLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Second:'))
        self.advancedBookLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Book:'))
        self.advancedChapterLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Chapter:'))
        self.advancedVerseLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Verse:'))
        self.advancedFromLabel.setText(
            translate('BiblesPlugin.MediaItem', 'From:'))
        self.advancedToLabel.setText(
            translate('BiblesPlugin.MediaItem', 'To:'))
        self.advancedClearLabel.setText(
            translate('BiblesPlugin.MediaItem', 'Results:'))
        self.advancedSearchButton.setText(
            translate('BiblesPlugin.MediaItem', 'Search'))
        self.quickSearchComboBox.addItem(
            translate('BiblesPlugin.MediaItem', 'Verse Search'))
        self.quickSearchComboBox.addItem(
            translate('BiblesPlugin.MediaItem', 'Text Search'))
        self.quickClearComboBox.addItem(
            translate('BiblesPlugin.MediaItem', 'Clear'))
        self.quickClearComboBox.addItem(
            translate('BiblesPlugin.MediaItem', 'Keep'))
        self.advancedClearComboBox.addItem(
            translate('BiblesPlugin.MediaItem', 'Clear'))
        self.advancedClearComboBox.addItem(
            translate('BiblesPlugin.MediaItem', 'Keep'))

    def initialise(self):
        log.debug(u'bible manager initialise')
        self.parent.manager.media = self
        self.loadBibles()
        self.updateAutoCompleter()
        self.configUpdated()
        log.debug(u'bible manager initialise complete')

    def setQuickMessage(self, text):
        self.quickMessage.setText(text)
        self.advancedMessage.setText(text)
        Receiver.send_message(u'openlp_process_events')
        # Minor delay to get the events processed.
        time.sleep(0.1)

    def onListViewResize(self, width, height):
        listViewGeometry = self.listView.geometry()
        self.SearchProgress.setGeometry(listViewGeometry.x(),
            (listViewGeometry.y() + listViewGeometry.height()) - 23, 81, 23)

    def onSearchProgressShow(self):
        self.SearchProgress.setVisible(True)
        Receiver.send_message(u'openlp_process_events')

    def onSearchProgressHide(self):
        self.SearchProgress.setVisible(False)

    def onImportClick(self):
        if not hasattr(self, u'import_wizard'):
            self.import_wizard = BibleImportForm(self, self.parent.manager,
                self.parent)
        # If the import was not canceled then reload.
        if self.import_wizard.exec_():
            self.reloadBibles()

    def loadBibles(self):
        log.debug(u'Loading Bibles')
        self.quickVersionComboBox.clear()
        self.quickSecondComboBox.clear()
        self.advancedVersionComboBox.clear()
        self.advancedSecondComboBox.clear()
        self.quickSecondComboBox.addItem(u'')
        self.advancedSecondComboBox.addItem(u'')
        # Get all bibles and sort the list.
        bibles = self.parent.manager.get_bibles().keys()
        bibles.sort()
        # Load the bibles into the combo boxes.
        first = True
        for bible in bibles:
            if bible:
                self.quickVersionComboBox.addItem(bible)
                self.quickSecondComboBox.addItem(bible)
                self.advancedVersionComboBox.addItem(bible)
                self.advancedSecondComboBox.addItem(bible)
                if first:
                    first = False
                    self.initialiseBible(bible)

    def reloadBibles(self):
        log.debug(u'Reloading Bibles')
        self.parent.manager.reload_bibles()
        self.loadBibles()

    def initialiseBible(self, bible):
        """
        This initialises the given bible, which means that its book names and
        their chapter numbers is added to the combo boxes on the
        'Advanced Search' Tab. This is not of any importance of the
        'Quick Search' Tab.

        ``bible``
            The bible to initialise (unicode).
        """
        log.debug(u'initialiseBible %s', bible)
        book_data = self.parent.manager.get_books(bible)
        self.advancedBookComboBox.clear()
        first = True
        for book in book_data:
            row = self.advancedBookComboBox.count()
            self.advancedBookComboBox.addItem(book[u'name'])
            self.advancedBookComboBox.setItemData(
                row, QtCore.QVariant(book[u'chapters']))
            if first:
                first = False
                self.initialiseChapterVerse(bible, book[u'name'],
                    book[u'chapters'])

    def initialiseChapterVerse(self, bible, book, chapter_count):
        log.debug(u'initialiseChapterVerse %s, %s', bible, book)
        self.chapter_count = chapter_count
        verse_count = self.parent.manager.get_verse_count(bible, book, 1)
        if verse_count == 0:
            self.advancedSearchButton.setEnabled(False)
            self.advancedMessage.setText(
                translate('BiblesPlugin.MediaItem', 'Bible not fully loaded.'))
        else:
            self.advancedSearchButton.setEnabled(True)
            self.advancedMessage.setText(u'')
            self.adjustComboBox(1, self.chapter_count, self.advancedFromChapter)
            self.adjustComboBox(1, self.chapter_count, self.advancedToChapter)
            self.adjustComboBox(1, verse_count, self.advancedFromVerse)
            self.adjustComboBox(1, verse_count, self.advancedToVerse)

    def updateAutoCompleter(self):
        """
        This updates the bible book completion list for the search field. The
        completion depends on the bible. It is only updated when we are doing a
        verse search, otherwise the auto completion list is removed.
        """
        books = []
        # We have to do a 'Verse Search'.
        if self.quickSearchComboBox.currentIndex() == 0:
            bibles = self.parent.manager.get_bibles()
            bible = unicode(self.quickVersionComboBox.currentText())
            if bible:
                book_data = bibles[bible].get_books()
                books = [book.name for book in book_data]
                books.sort()
        completer = QtGui.QCompleter(books)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.quickSearchEdit.setCompleter(completer)

    def onAdvancedVersionComboBox(self):
        self.initialiseBible(
            unicode(self.advancedVersionComboBox.currentText()))

    def onAdvancedBookComboBox(self):
        item = int(self.advancedBookComboBox.currentIndex())
        self.initialiseChapterVerse(
            unicode(self.advancedVersionComboBox.currentText()),
            unicode(self.advancedBookComboBox.currentText()),
            self.advancedBookComboBox.itemData(item).toInt()[0])

    def onAdvancedFromVerse(self):
        chapter_from = int(self.advancedFromChapter.currentText())
        chapter_to = int(self.advancedToChapter.currentText())
        if chapter_from == chapter_to:
            bible = unicode(self.advancedVersionComboBox.currentText())
            book = unicode(self.advancedBookComboBox.currentText())
            verse_from = int(self.advancedFromVerse.currentText())
            verse_count = self.parent.manager.get_verse_count(bible, book,
                chapter_to)
            self.adjustComboBox(verse_from, verse_count,
                self.advancedToVerse, True)

    def onAdvancedToChapter(self):
        bible = unicode(self.advancedVersionComboBox.currentText())
        book = unicode(self.advancedBookComboBox.currentText())
        chapter_from = int(self.advancedFromChapter.currentText())
        chapter_to = int(self.advancedToChapter.currentText())
        verse_from = int(self.advancedFromVerse.currentText())
        verse_to = int(self.advancedToVerse.currentText())
        verse_count = self.parent.manager.get_verse_count(bible, book,
            chapter_to)
        if chapter_from == chapter_to and verse_from > verse_to:
            self.adjustComboBox(verse_from, verse_count, self.advancedToVerse)
        else:
            self.adjustComboBox(1, verse_count, self.advancedToVerse)

    def onAdvancedFromChapter(self):
        bible = unicode(self.advancedVersionComboBox.currentText())
        book = unicode(self.advancedBookComboBox.currentText())
        chapter_from = int(self.advancedFromChapter.currentText())
        chapter_to = int(self.advancedToChapter.currentText())
        verse_count = self.parent.manager.get_verse_count(bible, book,
            chapter_from)
        self.adjustComboBox(1, verse_count, self.advancedFromVerse)
        if chapter_from > chapter_to:
            self.adjustComboBox(1, verse_count, self.advancedToVerse)
            self.adjustComboBox(chapter_from, self.chapter_count,
                self.advancedToChapter)
        elif chapter_from == chapter_to:
            self.adjustComboBox(chapter_from, self.chapter_count,
                self.advancedToChapter)
            self.adjustComboBox(1, verse_count, self.advancedToVerse, True)
        else:
            self.adjustComboBox(chapter_from, self.chapter_count,
                self.advancedToChapter, True)

    def adjustComboBox(self, range_from, range_to, combo, restore=False):
        """
        Adjusts the given como box to the given values.

        ``range_from``
            The first number of the range (int).

        ``range_to``
            The last number of the range (int).

        ``combo``
            The combo box itself (QComboBox).

        ``restore``
            If True, then the combo's currentText will be restored after
            adjusting (if possible).
        """
        log.debug(u'adjustComboBox %s, %s, %s', combo, range_from, range_to)
        if restore:
            old_text = unicode(combo.currentText())
        combo.clear()
        for i in range(range_from, range_to + 1):
            combo.addItem(unicode(i))
        if restore and combo.findText(old_text) != -1:
            combo.setCurrentIndex(combo.findText(old_text))

    def onAdvancedSearchButton(self):
        """
        Does an advanced search and saves the search results.
        """
        log.debug(u'Advanced Search Button pressed')
        self.advancedSearchButton.setEnabled(False)
        bible = unicode(self.advancedVersionComboBox.currentText())
        second_bible = unicode(self.advancedSecondComboBox.currentText())
        book = unicode(self.advancedBookComboBox.currentText())
        chapter_from = self.advancedFromChapter.currentText()
        chapter_to = self.advancedToChapter.currentText()
        verse_from = self.advancedFromVerse.currentText()
        verse_to = self.advancedToVerse.currentText()
        verse_separator = get_reference_match(u'sep_v_display')
        range_separator = get_reference_match(u'sep_r_display')
        verse_range = chapter_from + verse_separator + verse_from + \
            range_separator + chapter_to + verse_separator + verse_to
        versetext = u'%s %s' % (book, verse_range)
        self.search_results = self.parent.manager.get_verses(bible, versetext)
        if second_bible:
            self.second_search_results = self.parent.manager.get_verses(
                second_bible, versetext)
        if self.advancedClearComboBox.currentIndex() == 0:
            self.listView.clear()
        if self.listView.count() != 0:
            # Check if the first item is a second bible item or not.
            bitem = self.listView.item(0)
            item_second_bible = self._decodeQtObject(bitem, 'second_bible')
            if item_second_bible and second_bible or not item_second_bible and \
                not second_bible:
                self.displayResults(bible, second_bible)
            elif QtGui.QMessageBox.critical(self,
                translate('BiblePlugin.MediaItem', 'Error'),
                translate('BiblePlugin.MediaItem', 'You cannot combine single '
                'and second bible verses. Do you want to delete your search '
                'results and start a new search?'),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.No |
                QtGui.QMessageBox.Yes)) == QtGui.QMessageBox.Yes:
                self.listView.clear()
                self.displayResults(bible, second_bible)
        else:
            self.displayResults(bible, second_bible)
        self.advancedSearchButton.setEnabled(True)

    def onQuickSearchButton(self):
        """
        Does a quick search and saves the search results. Quick search can
        either be "Verse Search" or "Text Search".
        """
        log.debug(u'Quick Search Button pressed')
        self.quickSearchButton.setEnabled(False)
        bible = unicode(self.quickVersionComboBox.currentText())
        second_bible = unicode(self.quickSecondComboBox.currentText())
        text = unicode(self.quickSearchEdit.text())
        if self.quickSearchComboBox.currentIndex() == 0:
            # We are doing a 'Verse Search'.
            self.search_results = self.parent.manager.get_verses(bible, text)
            if second_bible and self.search_results:
                self.second_search_results = self.parent.manager.get_verses(
                    second_bible, text)
        else:
            # We are doing a 'Text Search'.
            bibles = self.parent.manager.get_bibles()
            self.search_results = self.parent.manager.verse_search(bible,
                second_bible, text)
            if second_bible and self.search_results:
                text = []
                for verse in self.search_results:
                    text.append((verse.book.name, verse.chapter, verse.verse,
                        verse.verse))
                self.second_search_results = \
                    bibles[second_bible].get_verses(text)
        if self.quickClearComboBox.currentIndex() == 0:
            self.listView.clear()
        if self.listView.count() != 0 and self.search_results:
            bitem = self.listView.item(0)
            item_second_bible = self._decodeQtObject(bitem, 'second_bible')
            if item_second_bible and second_bible or not item_second_bible and \
                not second_bible:
                self.displayResults(bible, second_bible)
            elif QtGui.QMessageBox.critical(self,
                translate('BiblePlugin.MediaItem', 'Error'),
                translate('BiblePlugin.MediaItem', 'You cannot combine single '
                'and second bible verses. Do you want to delete your search '
                'results and start a new search?'),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.No |
                QtGui.QMessageBox.Yes)) == QtGui.QMessageBox.Yes:
                self.listView.clear()
                self.displayResults(bible, second_bible)
        elif self.search_results:
            self.displayResults(bible, second_bible)
        self.quickSearchButton.setEnabled(True)

    def displayResults(self, bible, second_bible=u''):
        """
        Displays the search results in the media manager. All data needed for
        further action is saved for/in each row.
        """
        verse_separator = get_reference_match(u'sep_v_display')
        version = self.parent.manager.get_meta_data(bible, u'Version')
        copyright = self.parent.manager.get_meta_data(bible, u'Copyright')
        permissions = self.parent.manager.get_meta_data(bible, u'Permissions')
        if second_bible:
            second_version = self.parent.manager.get_meta_data(second_bible,
                u'Version')
            second_copyright = self.parent.manager.get_meta_data(second_bible,
                u'Copyright')
            second_permissions = self.parent.manager.get_meta_data(second_bible,
                u'Permissions')
            if not second_permissions:
                second_permissions = u''
        for count, verse in enumerate(self.search_results):
            if second_bible:
                try:
                    vdict = {
                        'book': QtCore.QVariant(verse.book.name),
                        'chapter': QtCore.QVariant(verse.chapter),
                        'verse': QtCore.QVariant(verse.verse),
                        'bible': QtCore.QVariant(bible),
                        'version': QtCore.QVariant(version.value),
                        'copyright': QtCore.QVariant(copyright.value),
                        'permissions': QtCore.QVariant(permissions.value),
                        'text': QtCore.QVariant(verse.text),
                        'second_bible': QtCore.QVariant(second_bible),
                        'second_version': QtCore.QVariant(second_version.value),
                        'second_copyright': QtCore.QVariant(
                            second_copyright.value),
                        'second_permissions': QtCore.QVariant(
                            second_permissions.value),
                        'second_text': QtCore.QVariant(
                            self.second_search_results[count].text)
                    }
                except IndexError:
                    break
                bible_text = u' %s %d%s%d (%s, %s)' % (verse.book.name,
                    verse.chapter, verse_separator, verse.verse, version.value,
                    second_version.value)
            else:
                vdict = {
                    'book': QtCore.QVariant(verse.book.name),
                    'chapter': QtCore.QVariant(verse.chapter),
                    'verse': QtCore.QVariant(verse.verse),
                    'bible': QtCore.QVariant(bible),
                    'version': QtCore.QVariant(version.value),
                    'copyright': QtCore.QVariant(copyright.value),
                    'permissions': QtCore.QVariant(permissions.value),
                    'text': QtCore.QVariant(verse.text),
                    'second_bible': QtCore.QVariant(u''),
                    'second_version': QtCore.QVariant(u''),
                    'second_copyright': QtCore.QVariant(u''),
                    'second_permissions': QtCore.QVariant(u''),
                    'second_text': QtCore.QVariant(u'')
                }
                bible_text = u'%s %d%s%d (%s)' % (verse.book.name,
                    verse.chapter, verse_separator, verse.verse, version.value)
            bible_verse = QtGui.QListWidgetItem(bible_text)
            bible_verse.setData(QtCore.Qt.UserRole, QtCore.QVariant(vdict))
            self.listView.addItem(bible_verse)
        self.listView.selectAll()
        self.search_results = {}
        self.second_search_results = {}

    def _decodeQtObject(self, bitem, key):
        reference = bitem.data(QtCore.Qt.UserRole)
        if isinstance(reference, QtCore.QVariant):
            reference = reference.toPyObject()
        obj = reference[QtCore.QString(key)]
        if isinstance(obj, QtCore.QVariant):
            obj = obj.toPyObject()
        return unicode(obj).strip()

    def generateSlideData(self, service_item, item=None, xmlVersion=False):
        """
        Generates and formats the slides for the service item as well as the
        service item's title.
        """
        log.debug(u'generating slide data')
        items = self.listView.selectedIndexes()
        if len(items) == 0:
            return False
        bible_text = u''
        old_chapter = -1
        raw_footer = []
        raw_slides = []
        raw_title = []
        first_item = True
        for item in items:
            bitem = self.listView.item(item.row())
            book = self._decodeQtObject(bitem, 'book')
            chapter = int(self._decodeQtObject(bitem, 'chapter'))
            verse = int(self._decodeQtObject(bitem, 'verse'))
            bible = self._decodeQtObject(bitem, 'bible')
            version = self._decodeQtObject(bitem, 'version')
            copyright = self._decodeQtObject(bitem, 'copyright')
            permissions = self._decodeQtObject(bitem, 'permissions')
            text = self._decodeQtObject(bitem, 'text')
            second_bible = self._decodeQtObject(bitem, 'second_bible')
            second_version = self._decodeQtObject(bitem, 'second_version')
            second_copyright = self._decodeQtObject(bitem, 'second_copyright')
            second_permissions = \
                self._decodeQtObject(bitem, 'second_permissions')
            second_text = self._decodeQtObject(bitem, 'second_text')
            verse_text = self.formatVerse(old_chapter, chapter, verse)
            footer = u'%s (%s %s %s)' % (book, version, copyright, permissions)
            if footer not in raw_footer:
                raw_footer.append(footer)
            if second_bible:
                footer = u'%s (%s %s %s)' % (book, second_version,
                    second_copyright, second_permissions)
                if footer not in raw_footer:
                    raw_footer.append(footer)
                bible_text = u'%s\u00a0%s\n\n%s\u00a0%s' % (verse_text, text,
                    verse_text, second_text)
                raw_slides.append(bible_text)
                bible_text = u''
            # If we are 'Verse Per Slide' then create a new slide.
            elif self.parent.settings_tab.layout_style == 0:
                bible_text = u'%s\u00a0%s' % (verse_text, text)
                raw_slides.append(bible_text)
                bible_text = u''
            # If we are 'Verse Per Line' then force a new line.
            elif self.parent.settings_tab.layout_style == 1:
                bible_text = u'%s %s\u00a0%s\n' % (bible_text, verse_text, text)
            # We have to be 'Continuous'.
            else:
                bible_text = u'%s %s\u00a0%s\n' % (bible_text, verse_text, text)
            if first_item:
                start_item = item
                first_item = False
            elif self.checkTitle(item, old_item):
                raw_title.append(self.formatTitle(start_item, old_item))
                start_item = item
            old_item = item
            old_chapter = chapter
        raw_title.append(self.formatTitle(start_item, item))
        # If there are no more items we check whether we have to add bible_text.
        if bible_text:
            raw_slides.append(bible_text)
            bible_text = u''
        # Service Item: Capabilities
        if self.parent.settings_tab.layout_style == 2 and not second_bible:
            # Split the line but do not replace line breaks in renderer.
            service_item.add_capability(ItemCapabilities.NoLineBreaks)
        service_item.add_capability(ItemCapabilities.AllowsPreview)
        service_item.add_capability(ItemCapabilities.AllowsLoop)
        # Service Item: Title
        for title in raw_title:
            if not service_item.title:
                service_item.title = title
            else:
                service_item.title += u', ' + title
        # Service Item: Theme
        if len(self.parent.settings_tab.bible_theme) == 0:
            service_item.theme = None
        else:
            service_item.theme = self.parent.settings_tab.bible_theme
        for slide in raw_slides:
            service_item.add_from_text(slide[:30], slide)
        if service_item.raw_footer:
            for footer in raw_footer:
                service_item.raw_footer.append(footer)
        else:
            service_item.raw_footer = raw_footer
        return True

    def formatTitle(self, start_item, old_item):
        """
        This methode is called, when we have to change the title, because
        we are at the end of a verse range. E. g. if we want to add
        Genesis 1:1-6 as well as Daniel 2:14.

        ``start_item``
            The first item of a range.

        ``old_item``
            The last item of a range.
        """
        verse_separator = get_reference_match(u'sep_v_display')
        range_separator = get_reference_match(u'sep_r_display')
        old_bitem = self.listView.item(old_item.row())
        old_chapter = self._decodeQtObject(old_bitem, 'chapter')
        old_verse = self._decodeQtObject(old_bitem, 'verse')
        start_bitem = self.listView.item(start_item.row())
        start_book = self._decodeQtObject(start_bitem, 'book')
        start_chapter = self._decodeQtObject(start_bitem, 'chapter')
        start_verse = self._decodeQtObject(start_bitem, 'verse')
        start_bible = self._decodeQtObject(start_bitem, 'bible')
        start_second_bible = self._decodeQtObject(start_bitem, 'second_bible')
        if start_second_bible:
            bibles = u'%s, %s' % (start_bible, start_second_bible)
        else:
            bibles = start_bible
        if start_chapter == old_chapter:
            if start_verse == old_verse:
                verse_range = start_chapter + verse_separator + start_verse
            else:
                verse_range = start_chapter + verse_separator + start_verse + \
                range_separator + old_verse
        else:
            verse_range = start_chapter + verse_separator + start_verse + \
                range_separator + old_chapter + verse_separator + old_verse
        title = u'%s %s (%s)' % (start_book, verse_range, bibles)
        return title

    def checkTitle(self, item, old_item):
        """
        This methode checks if we are at the end of an verse range. If that is
        the case, we return True, otherwise False. E. g. if we added
        Genesis 1:1-6, but the next verse is Daniel 2:14, we return True.

        ``item``
            The item we are dealing with at the moment.

        ``old_item``
            The item we were previously dealing with.
        """
        # Get all the necessary meta data.
        bitem = self.listView.item(item.row())
        book = self._decodeQtObject(bitem, 'book')
        chapter = int(self._decodeQtObject(bitem, 'chapter'))
        verse = int(self._decodeQtObject(bitem, 'verse'))
        bible = self._decodeQtObject(bitem, 'bible')
        second_bible = self._decodeQtObject(bitem, 'second_bible')
        old_bitem = self.listView.item(old_item.row())
        old_book = self._decodeQtObject(old_bitem, 'book')
        old_chapter = int(self._decodeQtObject(old_bitem, 'chapter'))
        old_verse = int(self._decodeQtObject(old_bitem, 'verse'))
        old_bible = self._decodeQtObject(old_bitem, 'bible')
        old_second_bible = self._decodeQtObject(old_bitem, 'second_bible')
        if old_bible != bible or old_second_bible != second_bible or \
            old_book != book:
            # The bible, second bible or book has changed.
            return True
        elif old_verse + 1 != verse and old_chapter == chapter:
            # We are still in the same chapter, but a verse has been skipped.
            return True
        elif old_chapter + 1 == chapter and (verse != 1 or
            old_verse != self.parent.manager.get_verse_count(
            old_bible, old_book, old_chapter)):
            # We are in the following chapter, but the last verse was not the
            # last verse of the chapter or the current verse is not the
            # first one of the chapter.
            return True
        else:
            return False

    def formatVerse(self, old_chapter, chapter, verse):
        """
        Formats and returns the text, each verse starts with, for the given
        chapter and verse. The text is either surrounded by round, square,
        curly brackets or no brackets at all. For example::

            u'{su}1:1{/su}'

        ``old_chapter``
            The previous verse's chapter number (int).

        ``chapter``
            The chapter number (int).

        ``verse``
            The verse number (int).
        """
        verse_separator = get_reference_match(u'sep_v_display')
        if not self.parent.settings_tab.show_new_chapters or \
            old_chapter != chapter:
            verse_text = unicode(chapter) + verse_separator + unicode(verse)
        else:
            verse_text = unicode(verse)
        if self.parent.settings_tab.display_style == 1:
            verse_text = u'{su}(' + verse_text + u'){/su}'
        elif self.parent.settings_tab.display_style == 2:
            verse_text = u'{su}{' + verse_text + u'}{/su}'
        elif self.parent.settings_tab.display_style == 3:
            verse_text = u'{su}[' + verse_text + u']{/su}'
        else:
            verse_text = u'{su}' + verse_text + u'{/su}'
        return verse_text
