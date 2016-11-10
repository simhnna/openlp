# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
Extend QListWidget to handle drag and drop functionality
"""
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import Registry, translate

NO_RESULTS = translate('OpenLP.ListWidgetWithDnD', 'No Search Results')
SHORT_RESULTS = translate('OpenLP.ListWidgetWithDnD', 'Please type more text to use \'Search As You Type\'')


class ListWidgetWithDnD(QtWidgets.QListWidget):
    """
    Provide a list widget to store objects and handle drag and drop events
    """
    def __init__(self, parent=None, name=''):
        """
        Initialise the list widget
        """
        super().__init__(parent)
        self.mime_data_text = name
        self.no_results_text = NO_RESULTS

    def activateDnD(self):
        """
        Activate DnD of widget
        """
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        Registry().register_function(('%s_dnd' % self.mime_data_text), self.parent().load_file)

    def clear(self, search_while_typing=False):
        """
        Re-implement clear, so that we can customise feedback when using 'Search as you type'

        :param search_while_typing: True if we want to display the customised message
        :return: None
        """
        if search_while_typing:
            self.no_results_text = SHORT_RESULTS
        else:
            self.no_results_text = NO_RESULTS
        super().clear()

    def mouseMoveEvent(self, event):
        """
        Drag and drop event does not care what data is selected as the recipient will use events to request the data
        move just tell it what plugin to call
        """
        if event.buttons() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        if not self.selectedItems():
            event.ignore()
            return
        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        drag.setMimeData(mime_data)
        mime_data.setText(self.mime_data_text)
        drag.exec(QtCore.Qt.CopyAction)

    def dragEnterEvent(self, event):
        """
        When something is dragged into this object, check if you should be able to drop it in here.
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Make an object droppable, and set it to copy the contents of the object, not move it.
        """
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Receive drop event check if it is a file and process it if it is.

        :param event:  Handle of the event pint passed
        """
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            files = []
            for url in event.mimeData().urls():
                local_file = os.path.normpath(url.toLocalFile())
                if os.path.isfile(local_file):
                    files.append(local_file)
                elif os.path.isdir(local_file):
                    listing = os.listdir(local_file)
                    for file in listing:
                        files.append(os.path.join(local_file, file))
            Registry().execute('{mime_data}_dnd'.format(mime_data=self.mime_data_text),
                               {'files': files, 'target': self.itemAt(event.pos())})
        else:
            event.ignore()

    def paintEvent(self, event):
        """
        Re-implement paintEvent so that we can add 'No Results' text when the listWidget is empty.

        :param event: A QPaintEvent
        :return: None
        """
        super().paintEvent(event)
        if not self.count():
            viewport = self.viewport()
            painter = QtGui.QPainter(viewport)
            font = QtGui.QFont()
            font.setItalic(True)
            painter.setFont(font)
            painter.drawText(QtCore.QRect(0, 0, viewport.width(), viewport.height()),
                             (QtCore.Qt.AlignHCenter | QtCore.Qt.TextWordWrap), self.no_results_text)
