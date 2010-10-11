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

import re
import logging

from PyQt4 import QtCore, QtGui

from openlp.plugins.songs.lib import VerseType

from editversedialog import Ui_EditVerseDialog

log = logging.getLogger(__name__)

class EditVerseForm(QtGui.QDialog, Ui_EditVerseDialog):
    """
    This is the form that is used to edit the verses of the song.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        QtCore.QObject.connect(self.verseTextEdit,
            QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
            self.contextMenu)
        QtCore.QObject.connect(self.insertButton, QtCore.SIGNAL(u'clicked()'),
            self.onInsertButtonClicked)
        QtCore.QObject.connect(self.verseTextEdit,
            QtCore.SIGNAL(u'cursorPositionChanged()'),
            self.onCursorPositionChanged)
        QtCore.QObject.connect(self.verseTypeComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'),
            self.onVerseTypeComboBoxChanged)
        self.verse_regex = re.compile(r'---\[([-\w]+):([\d]+)\]---')

    def contextMenu(self, point):
        item = self.serviceManagerList.itemAt(point)
        print item

    def insertVerse(self, title, num=1):
        if self.verseTextEdit.textCursor().columnNumber() != 0:
            self.verseTextEdit.insertPlainText(u'\n')
        self.verseTextEdit.insertPlainText(u'---[%s:%s]---\n' % (title, num))
        self.verseTextEdit.setFocus()

    def onInsertButtonClicked(self):
        verse_type = self.verseTypeComboBox.currentIndex()
        if VerseType.to_string(verse_type) is not None:
            self.insertVerse(VerseType.to_string(verse_type),
                self.verseNumberBox.value())

    def onVerseTypeComboBoxChanged(self):
        """
        Adjusts the verse number SpinBox in regard to the selected verse type.
        """
        position = self.verseTextEdit.textCursor().position()
        text = unicode(self.verseTextEdit.toPlainText())
        verse_type = VerseType.to_string(self.verseTypeComboBox.currentIndex())
        if not text:
            return
        position = text.rfind(u'---[%s' % verse_type, 0, position)
        if position == -1:
            self.verseNumberBox.setValue(1)
            return
        text = text[position:]
        position = text.find(u']---')
        if position == -1:
            return
        text = text[:position + 4]
        match = self.verse_regex.match(text)
        if match:
            verse_type = match.group(1)
            verse_number = int(match.group(2))
            verse_type_index = VerseType.from_string(verse_type)
            if verse_type_index is not None:
                self.verseNumberBox.setValue(verse_number)

    def onCursorPositionChanged(self):
        """
        Determines the previous verse type and number in regard to the cursor's
        position and adjusts the ComboBox and SpinBox to these values.
        """
        position = self.verseTextEdit.textCursor().position()
        text = unicode(self.verseTextEdit.toPlainText())
        if not text:
            return
        if text.rfind(u'[', 0, position) > text.rfind(u']', 0, position) and \
            text.find(u']', position) < text.find(u'[', position):
            return
        position = text.rfind(u'---[', 0, position)
        if position == -1:
            return
        text = text[position:]
        position = text.find(u']---')
        if position == -1:
            return
        text = text[:position + 4]
        match = self.verse_regex.match(text)
        if match:
            verse_type = match.group(1)
            verse_number = int(match.group(2))
            verse_type_index = VerseType.from_string(verse_type)
            if verse_type_index is not None:
                self.verseTypeComboBox.setCurrentIndex(verse_type_index)
                self.verseNumberBox.setValue(verse_number)

    def setVerse(self, text, single=False,
        tag=u'%s:1' % VerseType.to_string(VerseType.Verse)):
        if single:
            verse_type, verse_number = tag.split(u':')
            verse_type_index = VerseType.from_string(verse_type)
            if verse_type_index is not None:
                self.verseTypeComboBox.setCurrentIndex(verse_type_index)
            self.verseNumberBox.setValue(int(verse_number))
            self.insertButton.setVisible(False)
        else:
            if not text:
                text = u'---[%s:1]---\n' % VerseType.to_string(VerseType.Verse)
            self.verseTypeComboBox.setCurrentIndex(0)
            self.verseNumberBox.setValue(1)
            self.insertButton.setVisible(True)
        self.verseTextEdit.setPlainText(text)
        self.verseTextEdit.setFocus(QtCore.Qt.OtherFocusReason)
        self.verseTextEdit.moveCursor(QtGui.QTextCursor.End)

    def getVerse(self):
        return self.verseTextEdit.toPlainText(), \
            VerseType.to_string(self.verseTypeComboBox.currentIndex()), \
            unicode(self.verseNumberBox.value())

    def getVerseAll(self):
        text = self.verseTextEdit.toPlainText()
        if not text.startsWith(u'---['):
            text = u'---[%s:1]---\n%s' % (VerseType.to_string(VerseType.Verse),
                text)
        return text
