# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
Test the openlp.core.ui package.
"""
from unittest.mock import MagicMock, patch

from openlp.core.ui import SingleColumnTableWidget


def test_single_col_widget_create():
    """
    Test creating the SingleColumnTableWidget object
    """
    # GIVEN: the SingleColumnTableWidget class
    # WHEN: An object is created
    widget = SingleColumnTableWidget(None)

    # THEN: The object should have 1 column and no visible header
    assert widget.columnCount() == 1, 'There should be only 1 column'
    assert widget.horizontalHeader().isVisible() is False, 'The horizontal header should not be visible'


@patch('openlp.core.ui.QtWidgets.QTableWidget')
def test_single_col_widget_resize_event(MockQTableWidget):
    """
    Test that the resizeEvent method does the right thing
    """
    # GIVEN: An instance of a SingleColumnTableWidget and a mocked event
    widget = SingleColumnTableWidget(None)
    mocked_event = MagicMock()
    mocked_event.size.return_value.width.return_value = 10

    # WHEN: resizeEvent() is called
    with patch.object(widget, 'columnCount') as mocked_column_count, \
            patch.object(widget, 'setColumnWidth') as mocked_set_column_width, \
            patch.object(widget, 'resizeRowsToContents') as mocked_resize_rows_to_contents:
        mocked_column_count.return_value = 1
        widget.resizeEvent(mocked_event)

    # THEN: The correct calls should have been made
    MockQTableWidget.resizeEvent.assert_called_once_with(widget, mocked_event)
    mocked_column_count.assert_called_once_with()
    mocked_set_column_width.assert_called_once_with(0, 10)
    mocked_resize_rows_to_contents.assert_called_once_with()
