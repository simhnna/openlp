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
import re

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Receiver, translate
from openlp.core.ui import criticalErrorMessageBox
from openlp.plugins.songs.forms import EditVerseForm
from openlp.plugins.songs.lib import SongXML, VerseType
from openlp.plugins.songs.lib.db import Book, Song, Author, Topic
from editsongdialog import Ui_EditSongDialog

log = logging.getLogger(__name__)

class EditSongForm(QtGui.QDialog, Ui_EditSongDialog):
    """
    Class to manage the editing of a song
    """
    log.info(u'%s EditSongForm loaded', __name__)

    def __init__(self, parent, manager):
        """
        Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.song = None
        # can this be automated?
        self.width = 400
        self.setupUi(self)
        # Connecting signals and slots
        QtCore.QObject.connect(self.authorAddButton,
            QtCore.SIGNAL(u'clicked()'), self.onAuthorAddButtonClicked)
        QtCore.QObject.connect(self.authorRemoveButton,
            QtCore.SIGNAL(u'clicked()'), self.onAuthorRemoveButtonClicked)
        QtCore.QObject.connect(self.authorsListView,
            QtCore.SIGNAL(u'itemClicked(QListWidgetItem*)'),
            self.onAuthorsListViewPressed)
        QtCore.QObject.connect(self.topicAddButton,
            QtCore.SIGNAL(u'clicked()'), self.onTopicAddButtonClicked)
        QtCore.QObject.connect(self.topicRemoveButton,
            QtCore.SIGNAL(u'clicked()'), self.onTopicRemoveButtonClicked)
        QtCore.QObject.connect(self.topicsListView,
            QtCore.SIGNAL(u'itemClicked(QListWidgetItem*)'),
            self.onTopicListViewPressed)
        QtCore.QObject.connect(self.copyrightInsertButton,
            QtCore.SIGNAL(u'clicked()'), self.onCopyrightInsertButtonTriggered)
        QtCore.QObject.connect(self.verseAddButton,
            QtCore.SIGNAL(u'clicked()'), self.onVerseAddButtonClicked)
        QtCore.QObject.connect(self.verseListWidget,
            QtCore.SIGNAL(u'doubleClicked(QModelIndex)'),
            self.onVerseEditButtonClicked)
        QtCore.QObject.connect(self.verseEditButton,
            QtCore.SIGNAL(u'clicked()'), self.onVerseEditButtonClicked)
        QtCore.QObject.connect(self.verseEditAllButton,
            QtCore.SIGNAL(u'clicked()'), self.onVerseEditAllButtonClicked)
        QtCore.QObject.connect(self.verseDeleteButton,
            QtCore.SIGNAL(u'clicked()'), self.onVerseDeleteButtonClicked)
        QtCore.QObject.connect(self.verseListWidget,
            QtCore.SIGNAL(u'itemClicked(QTableWidgetItem*)'),
            self.onVerseListViewPressed)
        QtCore.QObject.connect(self.themeAddButton,
            QtCore.SIGNAL(u'clicked()'),
            self.parent.parent.renderManager.theme_manager.onAddTheme)
        QtCore.QObject.connect(self.maintenanceButton,
            QtCore.SIGNAL(u'clicked()'), self.onMaintenanceButtonClicked)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'theme_update_list'), self.loadThemes)
        self.previewButton = QtGui.QPushButton()
        self.previewButton.setObjectName(u'previewButton')
        self.previewButton.setText(
            translate('SongsPlugin.EditSongForm', 'Save && Preview'))
        self.buttonBox.addButton(
            self.previewButton, QtGui.QDialogButtonBox.ActionRole)
        QtCore.QObject.connect(self.buttonBox,
            QtCore.SIGNAL(u'clicked(QAbstractButton*)'), self.onPreview)
        # Create other objects and forms
        self.manager = manager
        self.verse_form = EditVerseForm(self)
        self.initialise()
        self.authorsListView.setSortingEnabled(False)
        self.authorsListView.setAlternatingRowColors(True)
        self.topicsListView.setSortingEnabled(False)
        self.topicsListView.setAlternatingRowColors(True)
        self.findVerseSplit = re.compile(u'---\[\]---\n', re.UNICODE)
        self.whitespace = re.compile(r'\W+', re.UNICODE)

    def initialise(self):
        self.verseEditButton.setEnabled(False)
        self.verseDeleteButton.setEnabled(False)
        self.authorRemoveButton.setEnabled(False)
        self.topicRemoveButton.setEnabled(False)

    def loadAuthors(self):
        authors = self.manager.get_all_objects(Author,
            order_by_ref=Author.display_name)
        self.authorsComboBox.clear()
        self.authorsComboBox.addItem(u'')
        self.authors = []
        for author in authors:
            row = self.authorsComboBox.count()
            self.authorsComboBox.addItem(author.display_name)
            self.authorsComboBox.setItemData(
                row, QtCore.QVariant(author.id))
            self.authors.append(author.display_name)
        completer = QtGui.QCompleter(self.authors)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.authorsComboBox.setCompleter(completer)

    def loadTopics(self):
        topics = self.manager.get_all_objects(Topic, order_by_ref=Topic.name)
        self.topicsComboBox.clear()
        self.topicsComboBox.addItem(u'')
        self.topics = []
        for topic in topics:
            row = self.topicsComboBox.count()
            self.topicsComboBox.addItem(topic.name)
            self.topics.append(topic.name)
            self.topicsComboBox.setItemData(row, QtCore.QVariant(topic.id))
        completer = QtGui.QCompleter(self.topics)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.topicsComboBox.setCompleter(completer)

    def loadBooks(self):
        books = self.manager.get_all_objects(Book, order_by_ref=Book.name)
        self.songBookComboBox.clear()
        self.songBookComboBox.addItem(u'')
        self.books = []
        for book in books:
            row = self.songBookComboBox.count()
            self.songBookComboBox.addItem(book.name)
            self.books.append(book.name)
            self.songBookComboBox.setItemData(row, QtCore.QVariant(book.id))
        completer = QtGui.QCompleter(self.books)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.songBookComboBox.setCompleter(completer)

    def loadThemes(self, theme_list):
        self.themeComboBox.clear()
        self.themeComboBox.addItem(u'')
        self.themes = []
        for theme in theme_list:
            self.themeComboBox.addItem(theme)
            self.themes.append(theme)
        completer = QtGui.QCompleter(self.themes)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.themeComboBox.setCompleter(completer)

    def newSong(self):
        log.debug(u'New Song')
        self.initialise()
        self.songTabWidget.setCurrentIndex(0)
        self.titleEdit.setText(u'')
        self.alternativeEdit.setText(u'')
        self.copyrightEdit.setText(u'')
        self.verseOrderEdit.setText(u'')
        self.commentsEdit.setText(u'')
        self.CCLNumberEdit.setText(u'')
        self.verseListWidget.clear()
        self.verseListWidget.setRowCount(0)
        self.authorsListView.clear()
        self.topicsListView.clear()
        self.titleEdit.setFocus(QtCore.Qt.OtherFocusReason)
        self.songBookNumberEdit.setText(u'')
        self.loadAuthors()
        self.loadTopics()
        self.loadBooks()
        self.themeComboBox.setCurrentIndex(0)
        # it's a new song to preview is not possible
        self.previewButton.setVisible(False)

    def loadSong(self, id, preview=False):
        """
        Loads a song.

        ``id``
            The song id (int).

        ``preview``
            Should be ``True`` if the song is also previewed (boolean).
        """
        log.debug(u'Load Song')
        self.initialise()
        self.songTabWidget.setCurrentIndex(0)
        self.loadAuthors()
        self.loadTopics()
        self.loadBooks()
        self.song = self.manager.get_object(Song, id)
        self.titleEdit.setText(self.song.title)
        if self.song.alternate_title:
            self.alternativeEdit.setText(self.song.alternate_title)
        else:
            self.alternativeEdit.setText(u'')
        if self.song.song_book_id != 0:
            book_name = self.manager.get_object(Book, self.song.song_book_id)
            id = self.songBookComboBox.findText(
                unicode(book_name.name), QtCore.Qt.MatchExactly)
            if id == -1:
                # Not Found
                id = 0
            self.songBookComboBox.setCurrentIndex(id)
        if self.song.theme_name:
            id = self.themeComboBox.findText(
                unicode(self.song.theme_name), QtCore.Qt.MatchExactly)
            if id == -1:
                # Not Found
                id = 0
                self.song.theme_name = None
            self.themeComboBox.setCurrentIndex(id)
        if self.song.copyright:
            self.copyrightEdit.setText(self.song.copyright)
        else:
            self.copyrightEdit.setText(u'')
        self.verseListWidget.clear()
        self.verseListWidget.setRowCount(0)
        if self.song.verse_order:
            self.verseOrderEdit.setText(self.song.verse_order)
        else:
            self.verseOrderEdit.setText(u'')
        if self.song.comments:
            self.commentsEdit.setPlainText(self.song.comments)
        else:
            self.commentsEdit.setPlainText(u'')
        if self.song.ccli_number:
            self.CCLNumberEdit.setText(self.song.ccli_number)
        else:
            self.CCLNumberEdit.setText(u'')
        if self.song.song_number:
            self.songBookNumberEdit.setText(self.song.song_number)
        else:
            self.songBookNumberEdit.setText(u'')

        # lazy xml migration for now
        self.verseListWidget.clear()
        self.verseListWidget.setRowCount(0)
        self.verseListWidget.setColumnWidth(0, self.width)
        # This is just because occasionally the lyrics come back as a "buffer"
        if isinstance(self.song.lyrics, buffer):
            self.song.lyrics = unicode(self.song.lyrics)
        if self.song.lyrics.startswith(u'<?xml version='):
            songXML = SongXML()
            verseList = songXML.get_verses(self.song.lyrics)
            for count, verse in enumerate(verseList):
                self.verseListWidget.setRowCount(
                    self.verseListWidget.rowCount() + 1)
                variant = u'%s:%s' % (verse[0][u'type'], verse[0][u'label'])
                item = QtGui.QTableWidgetItem(verse[1])
                item.setData(QtCore.Qt.UserRole, QtCore.QVariant(variant))
                self.verseListWidget.setItem(count, 0, item)
        else:
            verses = self.song.lyrics.split(u'\n\n')
            for count, verse in enumerate(verses):
                self.verseListWidget.setRowCount(
                    self.verseListWidget.rowCount() + 1)
                item = QtGui.QTableWidgetItem(verse)
                variant = u'%s:%s' % \
                    (VerseType.to_string(VerseType.Verse), unicode(count + 1))
                item.setData(QtCore.Qt.UserRole, QtCore.QVariant(variant))
                self.verseListWidget.setItem(count, 0, item)
        self.verseListWidget.resizeRowsToContents()
        self.tagRows()
        # clear the results
        self.authorsListView.clear()
        for author in self.song.authors:
            author_name = QtGui.QListWidgetItem(unicode(author.display_name))
            author_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(author.id))
            self.authorsListView.addItem(author_name)
        # clear the results
        self.topicsListView.clear()
        for topic in self.song.topics:
            topic_name = QtGui.QListWidgetItem(unicode(topic.name))
            topic_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(topic.id))
            self.topicsListView.addItem(topic_name)
        self.titleEdit.setFocus(QtCore.Qt.OtherFocusReason)
        # if not preview hide the preview button
        self.previewButton.setVisible(False)
        if preview:
            self.previewButton.setVisible(True)

    def tagRows(self):
        """
        Tag the Song List rows based on the verse list
        """
        rowLabel = []
        for row in range(0, self.verseListWidget.rowCount()):
            item = self.verseListWidget.item(row, 0)
            data = unicode(item.data(QtCore.Qt.UserRole).toString())
            bit = data.split(u':')
            rowTag = u'%s%s' % (bit[0][0:1], bit[1])
            rowLabel.append(rowTag)
        self.verseListWidget.setVerticalHeaderLabels(rowLabel)

    def onAuthorAddButtonClicked(self):
        item = int(self.authorsComboBox.currentIndex())
        text = unicode(self.authorsComboBox.currentText())
        if item == 0 and text:
            if QtGui.QMessageBox.question(self,
                translate('SongsPlugin.EditSongForm', 'Add Author'),
                translate('SongsPlugin.EditSongForm', 'This author does not '
                'exist, do you want to add them?'),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                if text.find(u' ') == -1:
                    author = Author.populate(first_name=u'', last_name=u'',
                        display_name=text)
                else:
                    author = Author.populate(first_name=text.rsplit(u' ', 1)[0],
                        last_name=text.rsplit(u' ', 1)[1], display_name=text)
                self.manager.save_object(author, False)
                author_item = QtGui.QListWidgetItem(
                    unicode(author.display_name))
                author_item.setData(QtCore.Qt.UserRole,
                    QtCore.QVariant(author.id))
                self.authorsListView.addItem(author_item)
                self.loadAuthors()
                self.authorsComboBox.setCurrentIndex(0)
            else:
                return
        elif item > 0:
            item_id = (self.authorsComboBox.itemData(item)).toInt()[0]
            author = self.manager.get_object(Author, item_id)
            if self.authorsListView.findItems(unicode(author.display_name),
                QtCore.Qt.MatchExactly):
                criticalErrorMessageBox(
                    message=translate('SongsPlugin.EditSongForm',
                    'This author is already in the list.'))
            else:
                author_item = QtGui.QListWidgetItem(unicode(
                    author.display_name))
                author_item.setData(QtCore.Qt.UserRole,
                    QtCore.QVariant(author.id))
                self.authorsListView.addItem(author_item)
            self.authorsComboBox.setCurrentIndex(0)
        else:
            QtGui.QMessageBox.warning(self,
                translate('SongsPlugin.EditSongForm', 'No Author Selected'),
                translate('SongsPlugin.EditSongForm', 'You have not selected '
                'a valid author. Either select an author from the list, '
                'or type in a new author and click the "Add Author to '
                'Song" button to add the new author.'))

    def onAuthorsListViewPressed(self):
        if self.authorsListView.count() > 1:
            self.authorRemoveButton.setEnabled(True)

    def onAuthorRemoveButtonClicked(self):
        self.authorRemoveButton.setEnabled(False)
        item = self.authorsListView.currentItem()
        row = self.authorsListView.row(item)
        self.authorsListView.takeItem(row)

    def onTopicAddButtonClicked(self):
        item = int(self.topicsComboBox.currentIndex())
        text = unicode(self.topicsComboBox.currentText())
        if item == 0 and text:
            if QtGui.QMessageBox.question(self,
                translate('SongsPlugin.EditSongForm', 'Add Topic'),
                translate('SongsPlugin.EditSongForm', 'This topic does not '
                'exist, do you want to add it?'),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                topic = Topic.populate(name=text)
                self.manager.save_object(topic, False)
                topic_item = QtGui.QListWidgetItem(unicode(topic.name))
                topic_item.setData(QtCore.Qt.UserRole,
                    QtCore.QVariant(topic.id))
                self.topicsListView.addItem(topic_item)
                self.loadTopics()
                self.topicsComboBox.setCurrentIndex(0)
            else:
                return
        elif item > 0:
            item_id = (self.topicsComboBox.itemData(item)).toInt()[0]
            topic = self.manager.get_object(Topic, item_id)
            if self.topicsListView.findItems(unicode(topic.name),
                QtCore.Qt.MatchExactly):
                criticalErrorMessageBox(
                    message=translate('SongsPlugin.EditSongForm',
                    'This topic is already in the list.'))
            else:
                topic_item = QtGui.QListWidgetItem(unicode(topic.name))
                topic_item.setData(QtCore.Qt.UserRole,
                    QtCore.QVariant(topic.id))
                self.topicsListView.addItem(topic_item)
            self.topicsComboBox.setCurrentIndex(0)
        else:
            QtGui.QMessageBox.warning(self,
                translate('SongsPlugin.EditSongForm', 'No Topic Selected'),
                translate('SongsPlugin.EditSongForm', 'You have not selected '
                'a valid topic. Either select a topic from the list, or '
                'type in a new topic and click the "Add Topic to Song" '
                'button to add the new topic.'))

    def onTopicListViewPressed(self):
        self.topicRemoveButton.setEnabled(True)

    def onTopicRemoveButtonClicked(self):
        self.topicRemoveButton.setEnabled(False)
        item = self.topicsListView.currentItem()
        row = self.topicsListView.row(item)
        self.topicsListView.takeItem(row)

    def onVerseListViewPressed(self):
        self.verseEditButton.setEnabled(True)
        self.verseDeleteButton.setEnabled(True)

    def onVerseAddButtonClicked(self):
        self.verse_form.setVerse(u'', True)
        if self.verse_form.exec_():
            afterText, verse, subVerse = self.verse_form.getVerse()
            data = u'%s:%s' % (verse, subVerse)
            item = QtGui.QTableWidgetItem(afterText)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(data))
            item.setText(afterText)
            self.verseListWidget.setRowCount(
                self.verseListWidget.rowCount() + 1)
            self.verseListWidget.setItem(
                int(self.verseListWidget.rowCount() - 1), 0, item)
        self.verseListWidget.setColumnWidth(0, self.width)
        self.verseListWidget.resizeRowsToContents()
        self.tagRows()

    def onVerseEditButtonClicked(self):
        item = self.verseListWidget.currentItem()
        if item:
            tempText = item.text()
            verseId = unicode(item.data(QtCore.Qt.UserRole).toString())
            self.verse_form.setVerse(tempText, True, verseId)
            if self.verse_form.exec_():
                afterText, verse, subVerse = self.verse_form.getVerse()
                data = u'%s:%s' % (verse, subVerse)
                item.setData(QtCore.Qt.UserRole, QtCore.QVariant(data))
                item.setText(afterText)
                # number of lines has change so repaint the list moving the data
                if len(tempText.split(u'\n')) != len(afterText.split(u'\n')):
                    tempList = {}
                    tempId = {}
                    for row in range(0, self.verseListWidget.rowCount()):
                        tempList[row] = self.verseListWidget.item(row, 0).text()
                        tempId[row] = self.verseListWidget.item(row, 0).\
                            data(QtCore.Qt.UserRole)
                    self.verseListWidget.clear()
                    for row in range (0, len(tempList)):
                        item = QtGui.QTableWidgetItem(tempList[row], 0)
                        item.setData(QtCore.Qt.UserRole, tempId[row])
                        self.verseListWidget.setItem(row, 0, item)
                    self.verseListWidget.resizeRowsToContents()
                    self.verseListWidget.repaint()
        self.tagRows()

    def onVerseEditAllButtonClicked(self):
        verse_list = u''
        if self.verseListWidget.rowCount() > 0:
            for row in range(0, self.verseListWidget.rowCount()):
                item = self.verseListWidget.item(row, 0)
                field = unicode(item.data(QtCore.Qt.UserRole).toString())
                verse_list += u'---[%s]---\n' % field
                verse_list += item.text()
                verse_list += u'\n'
            self.verse_form.setVerse(verse_list)
        else:
            self.verse_form.setVerse(u'')
        if self.verse_form.exec_():
            verse_list = self.verse_form.getVerseAll()
            verse_list = unicode(verse_list.replace(u'\r\n', u'\n'))
            self.verseListWidget.clear()
            self.verseListWidget.setRowCount(0)
            for row in self.findVerseSplit.split(verse_list):
                for match in row.split(u'---['):
                    for count, parts in enumerate(match.split(u']---\n')):
                        if len(parts) > 1:
                            if count == 0:
                                # make sure the tag is correctly cased
                                variant = u'%s%s' % \
                                    (parts[0:1].upper(), parts[1:].lower())
                            else:
                                if parts.endswith(u'\n'):
                                    parts = parts.rstrip(u'\n')
                                item = QtGui.QTableWidgetItem(parts)
                                item.setData(QtCore.Qt.UserRole,
                                    QtCore.QVariant(variant))
                                self.verseListWidget.setRowCount(
                                    self.verseListWidget.rowCount() + 1)
                                self.verseListWidget.setItem(
                                    int(self.verseListWidget.rowCount() - 1),
                                    0, item)
            self.verseListWidget.setColumnWidth(0, self.width)
            self.verseListWidget.resizeRowsToContents()
            self.verseListWidget.repaint()
            self.tagRows()
            self.verseEditButton.setEnabled(False)
            self.verseDeleteButton.setEnabled(False)

    def onVerseDeleteButtonClicked(self):
        self.verseListWidget.removeRow(self.verseListWidget.currentRow())
        self.verseEditButton.setEnabled(False)
        self.verseDeleteButton.setEnabled(False)

    def _validate_song(self):
        """
        Check the validity of the form. Only display the 'save' if the data
        can be saved.
        """
        log.debug(u'Validate Song')
        # Lets be nice and assume the data is correct.
        if len(self.titleEdit.displayText()) == 0:
            self.songTabWidget.setCurrentIndex(0)
            self.titleEdit.setFocus()
            criticalErrorMessageBox(
                message=translate('SongsPlugin.EditSongForm',
                'You need to type in a song title.'))
            return False
        if self.verseListWidget.rowCount() == 0:
            self.songTabWidget.setCurrentIndex(0)
            self.verseListWidget.setFocus()
            criticalErrorMessageBox(
                message=translate('SongsPlugin.EditSongForm',
                'You need to type in at least one verse.'))
            return False
        if self.authorsListView.count() == 0:
            self.songTabWidget.setCurrentIndex(1)
            self.authorsListView.setFocus()
            criticalErrorMessageBox(
                message=translate('SongsPlugin.EditSongForm',
                'You need to have an author for this song.'))
            return False
        if self.song.verse_order:
            order = []
            order_names = self.song.verse_order.split()
            for item in order_names:
                if len(item) == 1:
                    order.append(item.lower() + u'1')
                else:
                    order.append(item.lower())
            verses = []
            verse_names = []
            for index in range (0, self.verseListWidget.rowCount()):
                verse = self.verseListWidget.item(index, 0)
                verse = unicode(verse.data(QtCore.Qt.UserRole).toString())
                if verse not in verse_names:
                    verses.append(
                        re.sub(r'(.)[^:]*:(.*)', r'\1\2', verse.lower()))
                    verse_names.append(verse)
            for count, item in enumerate(order):
                if item not in verses:
                    self.songTabWidget.setCurrentIndex(0)
                    self.verseOrderEdit.setFocus()
                    valid = verses.pop(0)
                    for verse in verses:
                        valid = valid + u', ' + verse
                    criticalErrorMessageBox(
                        message=unicode(translate('SongsPlugin.EditSongForm',
                        'The verse order is invalid. There is no verse '
                        'corresponding to %s. Valid entries are %s.')) % \
                        (order_names[count], valid))
                    return False
            for count, verse in enumerate(verses):
                if verse not in order:
                    self.songTabWidget.setCurrentIndex(0)
                    self.verseOrderEdit.setFocus()
                    answer = QtGui.QMessageBox.warning(self,
                        translate('SongsPlugin.EditSongForm', 'Warning'),
                        unicode(translate('SongsPlugin.EditSongForm',
                        'You have not used %s anywhere in the verse '
                        'order. Are you sure you want to save the song '
                        'like this?')) % verse_names[count].replace(u':', u' '),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if answer == QtGui.QMessageBox.No:
                        return False
        return True

    def onCopyrightInsertButtonTriggered(self):
        text = self.copyrightEdit.text()
        pos = self.copyrightEdit.cursorPosition()
        sign = translate('SongsPlugin.EditSongForm', '\xa9')
        text = text[:pos] + sign + text[pos:]
        self.copyrightEdit.setText(text)
        self.copyrightEdit.setFocus()
        self.copyrightEdit.setCursorPosition(pos + len(sign))

    def onMaintenanceButtonClicked(self):
        temp_song_book = None
        item = int(self.songBookComboBox.currentIndex())
        text = unicode(self.songBookComboBox.currentText())
        if item == 0 and text:
            temp_song_book = text
        self.parent.song_maintenance_form.exec_()
        self.loadAuthors()
        self.loadBooks()
        self.loadTopics()
        if temp_song_book:
            self.songBookComboBox.setEditText(temp_song_book)

    def onPreview(self, button):
        """
        Save and Preview button pressed.
        The Song is valid so as the plugin to add it to preview to see.

        ``button``
            A button (QPushButton).
        """
        log.debug(u'onPreview')
        if unicode(button.objectName()) == u'previewButton' and \
            self.saveSong(True):
            Receiver.send_message(u'songs_preview')

    def clearCaches(self):
        """
        Free up autocompletion memory on dialog exit
        """
        self.authors = []
        self.themes = []
        self.books = []
        self.topics = []

    def closePressed(self):
        """
        Exit Dialog and do not save
        """
        Receiver.send_message(u'songs_edit_clear')
        self.clearCaches()
        self.close()

    def accept(self):
        """
        Exit Dialog and save song if valid
        """
        log.debug(u'accept')
        self.clearCaches()
        if not self.song:
            self.song = Song()
        item = int(self.songBookComboBox.currentIndex())
        text = unicode(self.songBookComboBox.currentText())
        if self.songBookComboBox.findText(text, QtCore.Qt.MatchExactly) < 0:
            if QtGui.QMessageBox.question(self,
                translate('SongsPlugin.EditSongForm', 'Add Book'),
                translate('SongsPlugin.EditSongForm', 'This song book does '
                'not exist, do you want to add it?'),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                book = Book.populate(name=text, publisher=u'')
                self.manager.save_object(book, False)
            else:
                return
        if self.saveSong():
            Receiver.send_message(u'songs_load_list')
            self.close()

    def saveSong(self, preview=False):
        """
        Get all the data from the widgets on the form, and then save it to the
        database.

        ``preview``
            Should be ``True`` if the song is also previewed (boolean).
        """
        self.song.title = unicode(self.titleEdit.text())
        self.song.alternate_title = unicode(self.alternativeEdit.text())
        self.song.copyright = unicode(self.copyrightEdit.text())
        if self.song.alternate_title:
            self.song.search_title = self.song.title + u'@' + \
                self.song.alternate_title
        else:
            self.song.search_title = self.song.title
        self.song.comments = unicode(self.commentsEdit.toPlainText())
        self.song.verse_order = unicode(self.verseOrderEdit.text())
        self.song.ccli_number = unicode(self.CCLNumberEdit.text())
        self.song.song_number = unicode(self.songBookNumberEdit.text())
        book_name = unicode(self.songBookComboBox.currentText())
        if book_name:
            self.song.book = self.manager.get_object_filtered(Book,
                Book.name == book_name)
        else:
            self.song.book = None
        theme_name = unicode(self.themeComboBox.currentText())
        if theme_name:
            self.song.theme_name = theme_name
        else:
            self.song.theme_name = None
        if self._validate_song():
            self.processLyrics()
            self.processTitle()
            self.song.authors = []
            for row in range(self.authorsListView.count()):
                item = self.authorsListView.item(row)
                authorId = (item.data(QtCore.Qt.UserRole)).toInt()[0]
                self.song.authors.append(self.manager.get_object(Author,
                    authorId))
            self.song.topics = []
            for row in range(self.topicsListView.count()):
                item = self.topicsListView.item(row)
                topicId = (item.data(QtCore.Qt.UserRole)).toInt()[0]
                self.song.topics.append(self.manager.get_object(Topic, topicId))
            self.manager.save_object(self.song)
            if not preview:
                self.song = None
            return True
        return False

    def processLyrics(self):
        log.debug(u'processLyrics')
        try:
            sxml = SongXML()
            text = u''
            multiple = []
            for i in range(0, self.verseListWidget.rowCount()):
                item = self.verseListWidget.item(i, 0)
                verseId = unicode(item.data(QtCore.Qt.UserRole).toString())
                bits = verseId.split(u':')
                sxml.add_verse_to_lyrics(bits[0], bits[1], unicode(item.text()))
                text = text + self.whitespace.sub(u' ',
                    unicode(self.verseListWidget.item(i, 0).text())) + u' '
                if (bits[1] > u'1') and (bits[0][0] not in multiple):
                    multiple.append(bits[0][0])
            self.song.search_lyrics = text.lower()
            self.song.lyrics = unicode(sxml.extract_xml(), u'utf-8')
            for verse in multiple:
                self.song.verse_order = re.sub(u'([' + verse.upper() +
                    verse.lower() + u'])(\W|$)', r'\g<1>1\2',
                    self.song.verse_order)
        except:
            log.exception(u'Problem processing song Lyrics \n%s',
                sxml.dump_xml())

    def processTitle(self):
        log.debug(u'processTitle')
        self.song.search_title = re.sub(r'[\'"`,;:(){}?]+', u'',
            unicode(self.song.search_title)).lower()
