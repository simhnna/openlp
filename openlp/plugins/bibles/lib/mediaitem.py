# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4
"""
OpenLP - Open Source Lyrics Projection
Copyright (c) 2008 Raoul Snyman
Portions copyright (c) 2008-2009 Martin Thompson, Tim Bentley

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.lib import translate, ServiceItem, MediaManagerItem, \
    Receiver, contextMenuAction, contextMenuSeparator
from openlp.plugins.bibles.forms import BibleImportForm
from openlp.plugins.bibles.lib.manager import BibleMode

class BibleList(QtGui.QListWidget):

    def __init__(self,parent=None,name=None):
        QtGui.QListView.__init__(self,parent)

    def mouseMoveEvent(self, event):
        """
        Drag and drop event does not care what data is selected
        as the recepient will use events to request the data move
        just tell it what plugin to call
        """
        if event.buttons() != QtCore.Qt.LeftButton:
            return
        drag = QtGui.QDrag(self)
        mimeData = QtCore.QMimeData()
        drag.setMimeData(mimeData)
        mimeData.setText(u'Bibles')
        dropAction = drag.start(QtCore.Qt.CopyAction)
        if dropAction == QtCore.Qt.CopyAction:
            self.close()

class BibleMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for Bibles.
    """
    global log
    log = logging.getLogger(u'BibleMediaItem')
    log.info(u'Bible Media Item loaded')

    def __init__(self, parent, icon, title):
        self.TranslationContext = u'BiblePlugin'
        self.PluginTextShort = u'Bible'
        self.ConfigSection = u'bibles'
        MediaManagerItem.__init__(self, parent, icon, title)
        self.search_results = {} # place to store the search results
        QtCore.QObject.connect(Receiver().get_receiver(),
            QtCore.SIGNAL(u'openlpreloadbibles'), self.reloadBibles)

    def setupUi(self):
        # Add a toolbar
        self.addToolbar()
        # Create buttons for the toolbar
        ## New Bible Button ##
        self.addToolbarButton(
            translate(u'BibleMediaItem',u'New Bible'),
            translate(u'BibleMediaItem',u'Register a new Bible'),
            u':/themes/theme_import.png', self.onBibleNewClick, u'BibleNewItem')
        ## Separator Line ##
        self.addToolbarSeparator()
        ## Preview Bible Button ##
        self.addToolbarButton(
            translate(u'BibleMediaItem',u'Preview Bible'),
            translate(u'BibleMediaItem',u'Preview the selected Bible Verse'),
            u':/system/system_preview.png', self.onPreviewClick, u'BiblePreviewItem')
        ## Live Bible Button ##
        self.addToolbarButton(
            translate(u'BibleMediaItem',u'Go Live'),
            translate(u'BibleMediaItem',u'Send the selected Bible Verse(s) live'),
            u':/system/system_live.png', self.onLiveClick, u'BibleLiveItem')
        ## Add Bible Button ##
        self.addToolbarButton(
            translate(u'BibleMediaItem',u'Add Bible Verse(s) To Service'),
            translate(u'BibleMediaItem',u'Add the selected Bible(s) to the service'),
            u':/system/system_add.png',
            self.onAddClick, u'BibleAddItem')
        # Create the tab widget
        self.SearchTabWidget = QtGui.QTabWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SearchTabWidget.sizePolicy().hasHeightForWidth())
        self.SearchTabWidget.setSizePolicy(sizePolicy)
        self.SearchTabWidget.setObjectName(u'SearchTabWidget')
        # Add the Quick Search tab
        self.QuickTab = QtGui.QWidget()
        self.QuickTab.setObjectName(u'QuickTab')
        self.QuickLayout = QtGui.QGridLayout(self.QuickTab)
        self.QuickLayout.setMargin(8)
        self.QuickLayout.setSpacing(8)
        self.QuickLayout.setObjectName(u'QuickLayout')
        self.QuickVersionLabel = QtGui.QLabel(self.QuickTab)
        self.QuickVersionLabel.setObjectName(u'QuickVersionLabel')
        self.QuickLayout.addWidget(self.QuickVersionLabel, 0, 0, 1, 1)
        self.QuickVersionComboBox = QtGui.QComboBox(self.QuickTab)
        self.QuickVersionComboBox.setObjectName(u'VersionComboBox')
        self.QuickLayout.addWidget(self.QuickVersionComboBox, 0, 1, 1, 2)
        self.QuickSearchLabel = QtGui.QLabel(self.QuickTab)
        self.QuickSearchLabel.setObjectName(u'QuickSearchLabel')
        self.QuickLayout.addWidget(self.QuickSearchLabel, 1, 0, 1, 1)
        self.QuickSearchComboBox = QtGui.QComboBox(self.QuickTab)
        self.QuickSearchComboBox.setObjectName(u'SearchComboBox')
        self.QuickLayout.addWidget(self.QuickSearchComboBox, 1, 1, 1, 2)
        self.QuickSearchLabel = QtGui.QLabel(self.QuickTab)
        self.QuickSearchLabel.setObjectName(u'QuickSearchLabel')
        self.QuickLayout.addWidget(self.QuickSearchLabel, 2, 0, 1, 1)
        self.QuickSearchEdit = QtGui.QLineEdit(self.QuickTab)
        self.QuickSearchEdit.setObjectName(u'QuickSearchEdit')
        self.QuickLayout.addWidget(self.QuickSearchEdit, 2, 1, 1, 2)
        self.QuickSearchButton = QtGui.QPushButton(self.QuickTab)
        self.QuickSearchButton.setObjectName(u'QuickSearchButton')
        self.QuickLayout.addWidget(self.QuickSearchButton, 3, 2, 1, 1)
        self.QuickClearLabel = QtGui.QLabel(self.QuickTab)
        self.QuickClearLabel.setObjectName(u'QuickSearchLabel')
        self.QuickLayout.addWidget(self.QuickClearLabel, 3, 0, 1, 1)
        self.ClearQuickSearchComboBox = QtGui.QComboBox(self.QuickTab)
        self.ClearQuickSearchComboBox.setObjectName(u'ClearQuickSearchComboBox')
        self.QuickLayout.addWidget(self.ClearQuickSearchComboBox, 3, 1, 1, 1)
        self.SearchTabWidget.addTab(self.QuickTab, 'Quick')
        QuickSpacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Expanding)
        self.QuickLayout.addItem(QuickSpacerItem, 4, 2, 1, 1)
        # Add the Advanced Search tab
        self.AdvancedTab = QtGui.QWidget()
        self.AdvancedTab.setObjectName(u'AdvancedTab')
        self.AdvancedLayout = QtGui.QGridLayout(self.AdvancedTab)
        self.AdvancedLayout.setMargin(8)
        self.AdvancedLayout.setSpacing(8)
        self.AdvancedLayout.setObjectName(u'AdvancedLayout')
        self.AdvancedVersionLabel = QtGui.QLabel(self.AdvancedTab)
        self.AdvancedVersionLabel.setObjectName(u'AdvancedVersionLabel')
        self.AdvancedLayout.addWidget(self.AdvancedVersionLabel, 0, 0, 1, 1)
        self.AdvancedVersionComboBox = QtGui.QComboBox(self.AdvancedTab)
        self.AdvancedVersionComboBox.setObjectName(u'AdvancedVersionComboBox')
        self.AdvancedLayout.addWidget(self.AdvancedVersionComboBox, 0, 2, 1, 2)
        self.AdvancedBookLabel = QtGui.QLabel(self.AdvancedTab)
        self.AdvancedBookLabel.setObjectName(u'AdvancedBookLabel')
        self.AdvancedLayout.addWidget(self.AdvancedBookLabel, 1, 0, 1, 1)
        self.AdvancedBookComboBox = QtGui.QComboBox(self.AdvancedTab)
        self.AdvancedBookComboBox.setObjectName(u'AdvancedBookComboBox')
        self.AdvancedLayout.addWidget(self.AdvancedBookComboBox, 1, 2, 1, 2)
        self.AdvancedChapterLabel = QtGui.QLabel(self.AdvancedTab)
        self.AdvancedChapterLabel.setObjectName(u'AdvancedChapterLabel')
        self.AdvancedLayout.addWidget(self.AdvancedChapterLabel, 2, 2, 1, 1)
        self.AdvancedVerseLabel = QtGui.QLabel(self.AdvancedTab)
        self.AdvancedVerseLabel.setObjectName(u'AdvancedVerseLabel')
        self.AdvancedLayout.addWidget(self.AdvancedVerseLabel, 2, 3, 1, 1)
        self.AdvancedFromLabel = QtGui.QLabel(self.AdvancedTab)
        self.AdvancedFromLabel.setObjectName(u'AdvancedFromLabel')
        self.AdvancedLayout.addWidget(self.AdvancedFromLabel, 3, 0, 1, 1)
        self.AdvancedToLabel = QtGui.QLabel(self.AdvancedTab)
        self.AdvancedToLabel.setObjectName(u'AdvancedToLabel')
        self.AdvancedLayout.addWidget(self.AdvancedToLabel, 4, 0, 1, 1)
        self.AdvancedFromChapter = QtGui.QComboBox(self.AdvancedTab)
        self.AdvancedFromChapter.setObjectName(u'AdvancedFromChapter')
        self.AdvancedLayout.addWidget(self.AdvancedFromChapter, 3, 2, 1, 1)
        self.AdvancedFromVerse = QtGui.QComboBox(self.AdvancedTab)
        self.AdvancedFromVerse.setObjectName(u'AdvancedFromVerse')
        self.AdvancedLayout.addWidget(self.AdvancedFromVerse, 3, 3, 1, 1)
        self.AdvancedToChapter = QtGui.QComboBox(self.AdvancedTab)
        self.AdvancedToChapter.setObjectName(u'AdvancedToChapter')
        self.AdvancedLayout.addWidget(self.AdvancedToChapter, 4, 2, 1, 1)
        self.AdvancedToVerse = QtGui.QComboBox(self.AdvancedTab)
        self.AdvancedToVerse.setObjectName(u'AdvancedToVerse')
        self.AdvancedLayout.addWidget(self.AdvancedToVerse, 4, 3, 1, 1)
        self.AdvancedClearLabel = QtGui.QLabel(self.QuickTab)
        self.AdvancedClearLabel.setObjectName(u'QuickSearchLabel')
        self.AdvancedLayout.addWidget(self.AdvancedClearLabel, 5, 0, 1, 1)
        self.ClearAdvancedSearchComboBox = QtGui.QComboBox(self.QuickTab)
        self.ClearAdvancedSearchComboBox.setObjectName(u'ClearAdvancedSearchComboBox')
        self.AdvancedLayout.addWidget(self.ClearAdvancedSearchComboBox, 5, 2, 1, 1)
        self.AdvancedSearchButton = QtGui.QPushButton(self.AdvancedTab)
        self.AdvancedSearchButton.setObjectName(u'AdvancedSearchButton')
        self.AdvancedLayout.addWidget(self.AdvancedSearchButton, 5, 3, 1, 1)
        self.SearchTabWidget.addTab(self.AdvancedTab, u'Advanced')
        # Add the search tab widget to the page layout
        self.PageLayout.addWidget(self.SearchTabWidget)
        self.ListView = BibleList()
        self.ListView.setAlternatingRowColors(True)
        self.ListView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ListView.setDragEnabled(True)
        self.PageLayout.addWidget(self.ListView)
        # Combo Boxes
        QtCore.QObject.connect(self.AdvancedVersionComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedVersionComboBox)
        QtCore.QObject.connect(self.AdvancedBookComboBox,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedBookComboBox)
        QtCore.QObject.connect(self.AdvancedFromChapter,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedFromChapter)
        QtCore.QObject.connect(self.AdvancedFromVerse,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedFromVerse)
        QtCore.QObject.connect(self.AdvancedToChapter,
            QtCore.SIGNAL(u'activated(int)'), self.onAdvancedToChapter)
        # Buttons
        QtCore.QObject.connect(self.AdvancedSearchButton,
            QtCore.SIGNAL(u'pressed()'), self.onAdvancedSearchButton)
        QtCore.QObject.connect(self.QuickSearchButton,
            QtCore.SIGNAL(u'pressed()'), self.onQuickSearchButton)
        QtCore.QObject.connect(self.ListView,
            QtCore.SIGNAL(u'doubleClicked(QModelIndex)'), self.onPreviewClick)
        # Context Menus
        self.ListView.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.ListView.addAction(contextMenuAction(
            self.ListView, u':/system/system_preview.png',
            translate(u'BibleMediaItem',u'&Preview Verse'), self.onPreviewClick))
        self.ListView.addAction(contextMenuAction(
            self.ListView, u':/system/system_live.png',
            translate(u'BibleMediaItem',u'&Show Live'), self.onLiveClick))
        self.ListView.addAction(contextMenuAction(
            self.ListView, u':/system/system_add.png',
            translate(u'BibleMediaItem',u'&Add to Service'), self.onAddClick))

    def retranslateUi(self):
        log.debug(u'retranslateUi')
        self.QuickVersionLabel.setText(translate(u'BibleMediaItem', u'Version:'))
        self.QuickSearchLabel.setText(translate(u'BibleMediaItem', u'Search Type:'))
        self.QuickSearchLabel.setText(translate(u'BibleMediaItem', u'Find:'))
        self.QuickSearchButton.setText(translate(u'BibleMediaItem', u'Search'))
        self.QuickClearLabel.setText(translate(u'BibleMediaItem', u'Results:'))
        self.AdvancedVersionLabel.setText(translate(u'BibleMediaItem', u'Version:'))
        self.AdvancedBookLabel.setText(translate(u'BibleMediaItem', u'Book:'))
        self.AdvancedChapterLabel.setText(translate(u'BibleMediaItem', u'Chapter:'))
        self.AdvancedVerseLabel.setText(translate(u'BibleMediaItem', u'Verse:'))
        self.AdvancedFromLabel.setText(translate(u'BibleMediaItem', u'From:'))
        self.AdvancedToLabel.setText(translate(u'BibleMediaItem', u'To:'))
        self.AdvancedClearLabel.setText(translate(u'BibleMediaItem', u'Results:'))
        self.AdvancedSearchButton.setText(translate(u'BibleMediaItem', u'Search'))
        self.QuickSearchComboBox.addItem(translate(u'BibleMediaItem', u'Verse Search'))
        self.QuickSearchComboBox.addItem(translate(u'BibleMediaItem', u'Text Search'))
        self.ClearQuickSearchComboBox.addItem(translate(u'BibleMediaItem', u'Clear'))
        self.ClearQuickSearchComboBox.addItem(translate(u'BibleMediaItem', u'Keep'))
        self.ClearAdvancedSearchComboBox.addItem(translate(u'BibleMediaItem', u'Clear'))
        self.ClearAdvancedSearchComboBox.addItem(translate(u'BibleMediaItem', u'Keep'))

    def initialise(self):
        log.debug(u'initialise')
        self.loadBibles()

    def loadBibles(self):
        log.debug(u'Loading Bibles')
        self.QuickVersionComboBox.clear()
        self.AdvancedVersionComboBox.clear()
        bibles = self.parent.biblemanager.get_bibles(BibleMode.Full)
        # load bibles into the combo boxes
        for bible in bibles:
            self.QuickVersionComboBox.addItem(bible)
        # Without HTTP
        bibles = self.parent.biblemanager.get_bibles(BibleMode.Partial)
        first = True
        # load bibles into the combo boxes
        for bible in bibles:
            self.AdvancedVersionComboBox.addItem(bible)
            if first:
                first = False
                # use the first bible as the trigger
                self.initialiseBible(bible)

    def onAdvancedVersionComboBox(self):
        self.initialiseBible(unicode(self.AdvancedVersionComboBox.currentText()))

    def onAdvancedBookComboBox(self):
        self.initialiseChapterVerse(unicode(self.AdvancedVersionComboBox.currentText()),
            unicode(self.AdvancedBookComboBox.currentText()))

    def onBibleNewClick(self):
        self.bibleimportform = BibleImportForm(self.parent.config, self.parent.biblemanager, self)
        self.bibleimportform.exec_()
        self.reloadBibles()

    def onAdvancedFromVerse(self):
        frm = self.AdvancedFromVerse.currentText()
        self.adjustComboBox(frm, self.verses, self.AdvancedToVerse)

    def onAdvancedToChapter(self):
        t1 = self.AdvancedFromChapter.currentText()
        t2 = self.AdvancedToChapter.currentText()
        if t1 != t2:
            bible = unicode(self.AdvancedVersionComboBox.currentText())
            book = unicode(self.AdvancedBookComboBox.currentText())
            # get the verse count for new chapter
            vse = self.parent.biblemanager.get_book_verse_count(bible, book, int(t2))[0]
            self.adjustComboBox(1, vse, self.AdvancedToVerse)

    def onAdvancedSearchButton(self):
        log.debug(u'Advanced Search Button pressed')
        bible = unicode(self.AdvancedVersionComboBox.currentText())
        book = unicode(self.AdvancedBookComboBox.currentText())
        chapter_from =  int(self.AdvancedFromChapter.currentText())
        chapter_to =  int(self.AdvancedToChapter.currentText())
        verse_from =  int(self.AdvancedFromVerse.currentText())
        verse_to =  int(self.AdvancedToVerse.currentText())
        self.search_results = self.parent.biblemanager.get_verse_text(bible, book,
            chapter_from, chapter_to, verse_from, verse_to)
        if self.ClearAdvancedSearchComboBox.currentIndex() == 0:
            self.ListView.clear()
        self.displayResults(bible)

    def onAdvancedFromChapter(self):
        bible = unicode(self.AdvancedVersionComboBox.currentText())
        book = unicode(self.AdvancedBookComboBox.currentText())
        cf = self.AdvancedFromChapter.currentText()
        self.adjustComboBox(cf, self.chapters_from, self.AdvancedToChapter)
        # get the verse count for new chapter
        vse = self.parent.biblemanager.get_book_verse_count(bible, book, int(cf))[0]
        self.adjustComboBox(1, vse, self.AdvancedFromVerse)
        self.adjustComboBox(1, vse, self.AdvancedToVerse)

    def onQuickSearchButton(self):
        log.debug(u'Quick Search Button pressed')
        bible = unicode(self.QuickVersionComboBox.currentText())
        text = unicode(self.QuickSearchEdit.displayText())
        if self.ClearQuickSearchComboBox.currentIndex() == 0:
            self.ListView.clear()
        if self.QuickSearchComboBox.currentIndex() == 1:
            self.search_results = self.parent.biblemanager.get_verse_from_text(bible, text)
        else:
            self.searchByReference(bible, text)
        if self.search_results is not None:
            self.displayResults(bible)

    def generateSlideData(self, service_item):
        log.debug(u'generating slide data')
        items = self.ListView.selectedIndexes()
        old_chapter = u''
        raw_slides=[]
        raw_footer = []
        bible_text = u''
        for item in items:
            bitem =  self.ListView.item(item.row())
            text = unicode((bitem.data(QtCore.Qt.UserRole)).toString())
            verse = text[:text.find(u'(')]
            bible = text[text.find(u'(') + 1:-1]
            self.searchByReference(bible, verse)
            book = self.search_results[0].book.name
            chapter = unicode(self.search_results[0].chapter)
            verse = unicode(self.search_results[0].verse)
            text = self.search_results[0].text
            # Paragraph
            if self.parent.bibles_tab.paragraph_style:
                text = text + u'\n\n'
            if self.parent.bibles_tab.display_style == 1:
                loc = self.formatVerse(old_chapter, chapter, verse, u'(u', u')')
            elif  self.parent.bibles_tab.display_style == 2:
                loc = self.formatVerse(old_chapter, chapter, verse, u'{', u'}')
            elif  self.parent.bibles_tab.display_style == 3:
                loc = self.formatVerse(old_chapter, chapter, verse, u'[', u']')
            else:
                loc = self.formatVerse(old_chapter, chapter, verse, u'', u'')
            old_chapter = chapter
            bible_text = bible_text + u' '+ loc + u' '+ text
            service_item.title = book + u' ' + loc
            if len(raw_footer) <= 1:
                raw_footer.append(book)
        if  len(self.parent.bibles_tab.bible_theme)  == 0:
            service_item.theme = None
        else:
            service_item.theme = self.parent.bibles_tab.bible_theme
        raw_slides.append(bible_text)
        for slide in raw_slides:
            service_item.add_from_text(slide[:30], slide)
        service_item.raw_footer = raw_footer

    def formatVerse(self, old_chapter, chapter, verse, opening, closing):
        loc = opening
        if old_chapter != chapter:
            loc += chapter + u':'
        elif not self.parent.bibles_tab.show_new_chapters:
            loc += chapter + u':'
        loc += verse
        loc += closing
        return loc

    def reloadBibles(self):
        log.debug(u'Reloading Bibles')
        self.parent.biblemanager.reload_bibles()
        self.loadBibles()

    def initialiseBible(self, bible):
        log.debug(u'initialiseBible %s', bible)
        books = self.parent.biblemanager.get_bible_books(unicode(bible))
        self.AdvancedBookComboBox.clear()
        first = True
        for book in books:
            self.AdvancedBookComboBox.addItem(book.name)
            if first:
                first = False
                self.initialiseChapterVerse(bible, book.name)

    def initialiseChapterVerse(self, bible, book):
        log.debug(u'initialiseChapterVerse %s , %s', bible, book)
        self.chapters_from = self.parent.biblemanager.get_book_chapter_count(bible, book)
        self.verses = self.parent.biblemanager.get_book_verse_count(bible, book, 1)
        self.adjustComboBox(1, self.chapters_from, self.AdvancedFromChapter)
        self.adjustComboBox(1, self.chapters_from, self.AdvancedToChapter)
        self.adjustComboBox(1, self.verses, self.AdvancedFromVerse)
        self.adjustComboBox(1, self.verses, self.AdvancedToVerse)

    def adjustComboBox(self, frm, to , combo):
        log.debug(u'adjustComboBox %s , %s , %s', combo, frm,  to)
        combo.clear()
        for i in range(int(frm), int(to) + 1):
            combo.addItem(unicode(i))

    def displayResults(self, bible):
        for verse in self.search_results:
            #bible_text = unicode(u' %s %d:%d (%s)'%(book , chap,vse, bible))
            #bible_verse = QtGui.QListWidgetItem(bible_text)
            #bible_verse.setData(QtCore.Qt.UserRole, QtCore.QVariant(bible_text))
            #self.ListView.addItem(bible_verse)
            bible_text = u' %s %d:%d (%s)' % (verse.book.name,
                verse.chapter, verse.verse, bible)
            bible_verse = QtGui.QListWidgetItem(bible_text)
            bible_verse.setData(QtCore.Qt.UserRole,
                QtCore.QVariant(bible_text))
            self.ListView.addItem(bible_verse)

    def searchByReference(self, bible,  search):
        log.debug(u'searchByReference %s ,%s', bible, search)
        book = ''
        start_chapter = ''
        end_chapter = ''
        start_verse = ''
        end_verse = ''
        search = search.replace(u'  ', u' ').strip()
        original = search
        message = None
        # Remove book beware 0 index arrays
        for i in range (len(search)-1, 0, - 1):
            if search[i] == ' ':
                book = search[:i]
                # remove book from string
                search = search[i:]
                break
        # allow V or v for verse instead of :
        search = search.replace(u'v', ':')
        search = search.replace(u'V', ':')
        search = search.strip()
        colon = search.find(u':')
        if colon == -1:
            # number : found
            i = search.rfind(u' ')
            if i == -1:
                chapter = ''
            else:
                chapter = search[i:len(search)]
            hyphen = chapter.find(u'-')
            if hyphen != -1:
                start_chapter= chapter[:hyphen]
                end_chapter= chapter[hyphen + 1:len(chapter)]
            else:
                start_chapter = chapter
        else:
            # more complex
            #print search
            sp = search.split(u'-') #find first
            #print sp, len(sp)
            sp1 = sp[0].split(u':')
            #print sp1, len(sp1)
            if len(sp1) == 1:
                start_chapter = sp1[0]
                start_verse = 1
            else:
                start_chapter = sp1[0]
                start_verse = sp1[1]
            if len(sp)== 1:
                end_chapter = start_chapter
                end_verse = start_verse
            else:
                sp1 = sp[1].split(u':')
                #print "2nd details", sp1, len(sp1)
                if len(sp1) == 1:
                    end_chapter = start_chapter
                    end_verse =  sp1[0]
                else:
                    end_chapter = sp1[0]
                    end_verse = sp1[1]
        #print 'search = ' + unicode(original)
        #print 'results = ' + unicode(book) + ' @ '+ unicode(start_chapter)+' @ '+ unicode(end_chapter)+' @ '+ unicode(start_verse)+ ' @ '+ unicode(end_verse)
        if end_chapter == '':
            end_chapter = start_chapter.rstrip()
        if start_verse == '':
            if end_verse == '':
                start_verse = 1
            else:
                start_verse = end_verse
        if end_verse == '':
            end_verse = 99
        if start_chapter == '':
            message = u'No chapter found for search criteria'
        #print 'message = ' + unicode(message)
        #print 'search = ' + unicode(original)
        #print 'results = ' + unicode(book) + ' @ '+ unicode(start_chapter)+' @ '+ unicode(end_chapter)+' @ '+ unicode(start_verse)+ ' @ '+ unicode(end_verse)
        if message == None:
            self.search_results = None
            self.search_results = self.parent.biblemanager.get_verse_text(bible, book,
                int(start_chapter), int(end_chapter), int(start_verse),
                int(end_verse))
        else:
            reply = QtGui.QMessageBox.information(self,
                translate(u'BibleMediaItem', u'Information'),
                translate(u'BibleMediaItem', message))
