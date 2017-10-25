# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
The :mod:`listpreviewwidget` is a widget that lists the slides in the slide controller.
It is based on a QTableWidget but represents its contents in list form.
"""
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import is_win
from openlp.core.common.i18n import UiStrings
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import ImageSource, ItemCapabilities, ServiceItem


class ListPreviewWidget(QtWidgets.QTableWidget, RegistryProperties):
    """
    A special type of QTableWidget which lists the slides in the slide controller

    :param parent:
    :param screen_ratio:
    """

    def __init__(self, parent, screen_ratio):
        """
        Initializes the widget to default state.

        An empty ``ServiceItem`` is used by default. replace_service_manager_item() needs to be called to make this
        widget display something.
        """
        super(QtWidgets.QTableWidget, self).__init__(parent)
        self._setup(screen_ratio)

    def _setup(self, screen_ratio):
        """
        Set up the widget
        """
        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.setColumnWidth(0, self.parent().width())
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setAlternatingRowColors(True)
        # Initialize variables.
        self.service_item = ServiceItem()
        self.screen_ratio = screen_ratio
        self.auto_row_height = 100
        # Connect signals
        self.verticalHeader().sectionResized.connect(self.row_resized)

    def resizeEvent(self, event):
        """
        Overloaded method from QTableWidget. Will recalculate the layout.
        """
        self.__recalculate_layout()

    def __recalculate_layout(self):
        """
        Recalculates the layout of the table widget. It will set height and width
        of the table cells. QTableWidget does not adapt the cells to the widget size on its own.
        """
        self.setColumnWidth(0, self.viewport().width())
        if self.service_item:
            # Sort out songs, bibles, etc.
            if self.service_item.is_text():
                self.resizeRowsToContents()
            # Sort out image heights.
            else:
                height = self.viewport().width() // self.screen_ratio
                max_img_row_height = Settings().value('advanced/slide max height')
                # Adjust for row height cap if in use.
                if isinstance(max_img_row_height, int):
                    if max_img_row_height > 0 and height > max_img_row_height:
                        height = max_img_row_height
                    elif max_img_row_height < 0:
                        # If auto setting, show that number of slides, or if the resulting slides too small, 100px.
                        # E.g. If setting is -4, 4 slides will be visible, unless those slides are < 100px high.
                        self.auto_row_height = max(self.viewport().height() / (-1 * max_img_row_height), 100)
                        height = min(height, self.auto_row_height)
                # Apply new height to slides
                for frame_number in range(len(self.service_item.get_frames())):
                    self.setRowHeight(frame_number, height)

    def row_resized(self, row, old_height, new_height):
        """
        Will scale non-image slides.
        """
        # Only for non-text slides when row height cap in use
        max_img_row_height = Settings().value('advanced/slide max height')
        if self.service_item.is_text() or not isinstance(max_img_row_height, int) or max_img_row_height == 0:
            return
        # Get and validate label widget containing slide & adjust max width
        try:
            self.cellWidget(row, 0).children()[1].setMaximumWidth(new_height * self.screen_ratio)
        except:
            return

    def screen_size_changed(self, screen_ratio):
        """
        This method is called whenever the live screen size changes, which then makes a layout recalculation necessary

        :param screen_ratio: The new screen ratio
        """
        self.screen_ratio = screen_ratio
        self.__recalculate_layout()

    def replace_service_item(self, service_item, width, slide_number):
        """
        Replace the current preview items with the ones in service_item and display the given slide

        :param service_item: The service item to insert
        :param width: The width of the column
        :param slide_number: The slide number to pre-select
        """
        self.service_item = service_item
        self.setRowCount(0)
        self.clear()
        self.setColumnWidth(0, width)
        row = 0
        text = []
        for frame_number, frame in enumerate(self.service_item.get_frames()):
            self.setRowCount(self.slide_count() + 1)
            item = QtWidgets.QTableWidgetItem()
            slide_height = 0
            if self.service_item.is_text():
                if frame['verseTag']:
                    # These tags are already translated.
                    verse_def = frame['verseTag']
                    verse_def = '%s%s' % (verse_def[0], verse_def[1:])
                    two_line_def = '%s\n%s' % (verse_def[0], verse_def[1:])
                    row = two_line_def
                else:
                    row += 1
                item.setText(frame['text'])
            else:
                label = QtWidgets.QLabel()
                label.setContentsMargins(4, 4, 4, 4)
                if self.service_item.is_media():
                    label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                else:
                    label.setScaledContents(True)
                if self.service_item.is_command():
                    if self.service_item.is_capable(ItemCapabilities.HasThumbnails):
                        image = self.image_manager.get_image(frame['image'], ImageSource.CommandPlugins)
                        pixmap = QtGui.QPixmap.fromImage(image)
                    else:
                        pixmap = QtGui.QPixmap(frame['image'])
                else:
                    image = self.image_manager.get_image(frame['path'], ImageSource.ImagePlugin)
                    pixmap = QtGui.QPixmap.fromImage(image)
                pixmap.setDevicePixelRatio(label.devicePixelRatio())
                label.setPixmap(pixmap)
                slide_height = width // self.screen_ratio
                # Setup and validate row height cap if in use.
                max_img_row_height = Settings().value('advanced/slide max height')
                if isinstance(max_img_row_height, int) and max_img_row_height != 0:
                    if max_img_row_height > 0 and slide_height > max_img_row_height:
                        # Manual Setting
                        slide_height = max_img_row_height
                    elif max_img_row_height < 0 and slide_height > self.auto_row_height:
                        # Auto Setting
                        slide_height = self.auto_row_height
                    label.setMaximumWidth(slide_height * self.screen_ratio)
                    label.resize(slide_height * self.screen_ratio, slide_height)
                    # Build widget with stretch padding
                    container = QtWidgets.QWidget()
                    hbox = QtWidgets.QHBoxLayout()
                    hbox.setContentsMargins(0, 0, 0, 0)
                    hbox.addWidget(label, stretch=1)
                    hbox.addStretch(0)
                    container.setLayout(hbox)
                    # Add to table
                    self.setCellWidget(frame_number, 0, container)
                else:
                    # Add to table
                    self.setCellWidget(frame_number, 0, label)
                row += 1
            text.append(str(row))
            self.setItem(frame_number, 0, item)
            if slide_height:
                self.setRowHeight(frame_number, slide_height)
        self.setVerticalHeaderLabels(text)
        if self.service_item.is_text():
            self.resizeRowsToContents()
        self.setColumnWidth(0, self.viewport().width())
        self.change_slide(slide_number)

    def change_slide(self, slide):
        """
        Switches to the given row.
        """
        # Retrieve setting
        auto_scrolling = Settings().value('advanced/autoscrolling')
        # Check if auto-scroll disabled (None) and validate value as dict containing 'dist' and 'pos'
        # 'dist' represents the slide to scroll to relative to the new slide (-1 = previous, 0 = current, 1 = next)
        # 'pos' represents the vert position of of the slide (0 = in view, 1 = top, 2 = middle, 3 = bottom)
        if not (isinstance(auto_scrolling, dict) and 'dist' in auto_scrolling and 'pos' in auto_scrolling and
                isinstance(auto_scrolling['dist'], int) and isinstance(auto_scrolling['pos'], int)):
            return
        # prevent scrolling past list bounds
        scroll_to_slide = slide + auto_scrolling['dist']
        if scroll_to_slide < 0:
            scroll_to_slide = 0
        if scroll_to_slide >= self.slide_count():
            scroll_to_slide = self.slide_count() - 1
        # Scroll to item if possible.
        self.scrollToItem(self.item(scroll_to_slide, 0), auto_scrolling['pos'])
        self.selectRow(slide)

    def current_slide_number(self):
        """
        Returns the position of the currently active item. Will return -1 if the widget is empty.
        """
        return super(ListPreviewWidget, self).currentRow()

    def slide_count(self):
        """
        Returns the number of slides this widget holds.
        """
        return super(ListPreviewWidget, self).rowCount()


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
        self.no_results_text = UiStrings().NoResults
        self.setSpacing(1)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

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
            self.no_results_text = UiStrings().ShortResults
        else:
            self.no_results_text = UiStrings().NoResults
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

    def allItems(self):
        """
        An generator to list all the items in the widget

        :return: a generator
        """
        for row in range(self.count()):
            yield self.item(row)

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


class TreeWidgetWithDnD(QtWidgets.QTreeWidget):
    """
    Provide a tree widget to store objects and handle drag and drop events
    """
    def __init__(self, parent=None, name=''):
        """
        Initialise the tree widget
        """
        super(TreeWidgetWithDnD, self).__init__(parent)
        self.mime_data_text = name
        self.allow_internal_dnd = False
        self.header().close()
        self.default_indentation = self.indentation()
        self.setIndentation(0)
        self.setAnimated(True)

    def activateDnD(self):
        """
        Activate DnD of widget
        """
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        Registry().register_function(('%s_dnd' % self.mime_data_text), self.parent().load_file)
        Registry().register_function(('%s_dnd_internal' % self.mime_data_text), self.parent().dnd_move_internal)

    def mouseMoveEvent(self, event):
        """
        Drag and drop event does not care what data is selected as the recipient will use events to request the data
        move just tell it what plugin to call

        :param event: The event that occurred
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
        Receive drag enter event, check if it is a file or internal object and allow it if it is.

        :param event:  The event that occurred
        """
        if event.mimeData().hasUrls():
            event.accept()
        elif self.allow_internal_dnd:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Receive drag move event, check if it is a file or internal object and allow it if it is.

        :param event: The event that occurred
        """
        QtWidgets.QTreeWidget.dragMoveEvent(self, event)
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        elif self.allow_internal_dnd:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Receive drop event, check if it is a file or internal object and process it if it is.

        :param event: Handle of the event pint passed
        """
        # If we are on Windows, OpenLP window will not be set on top. For example, user can drag images to Library and
        # the folder stays on top of the group creation box. This piece of code fixes this issue.
        if is_win():
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.setWindowState(QtCore.Qt.WindowNoState)
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            files = []
            for url in event.mimeData().urls():
                local_file = url.toLocalFile()
                if os.path.isfile(local_file):
                    files.append(local_file)
                elif os.path.isdir(local_file):
                    listing = os.listdir(local_file)
                    for file_name in listing:
                        files.append(os.path.join(local_file, file_name))
            Registry().execute('%s_dnd' % self.mime_data_text, {'files': files, 'target': self.itemAt(event.pos())})
        elif self.allow_internal_dnd:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            Registry().execute('%s_dnd_internal' % self.mime_data_text, self.itemAt(event.pos()))
        else:
            event.ignore()

    # Convenience methods for emulating a QListWidget. This helps keeping MediaManagerItem simple.
    def addItem(self, item):
        self.addTopLevelItem(item)

    def count(self):
        return self.topLevelItemCount()

    def item(self, index):
        return self.topLevelItem(index)
