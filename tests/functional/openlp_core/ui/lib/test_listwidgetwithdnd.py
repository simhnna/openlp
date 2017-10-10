# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is    free software; you can redistribute it and/or modify it     #
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
This module contains tests for the openlp.core.lib.listwidgetwithdnd module
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch
from types import GeneratorType

from openlp.core.common.i18n import UiStrings
from openlp.core.ui.lib.listwidgetwithdnd import ListWidgetWithDnD


class TestListWidgetWithDnD(TestCase):
    """
    Test the :class:`~openlp.core.lib.listwidgetwithdnd.ListWidgetWithDnD` class
    """
    def test_clear(self):
        """
        Test the clear method when called without any arguments.
        """
        # GIVEN: An instance of ListWidgetWithDnD
        widget = ListWidgetWithDnD()

        # WHEN: Calling clear with out any arguments
        widget.clear()

        # THEN: The results text should be the standard 'no results' text.
        self.assertEqual(widget.no_results_text, UiStrings().NoResults)

    def test_clear_search_while_typing(self):
        """
        Test the clear method when called with the search_while_typing argument set to True
        """
        # GIVEN: An instance of ListWidgetWithDnD
        widget = ListWidgetWithDnD()

        # WHEN: Calling clear with search_while_typing set to True
        widget.clear(search_while_typing=True)

        # THEN: The results text should be the 'short results' text.
        self.assertEqual(widget.no_results_text, UiStrings().ShortResults)

    def test_all_items_no_list_items(self):
        """
        Test allItems when there are no items in the list widget
        """
        # GIVEN: An instance of ListWidgetWithDnD
        widget = ListWidgetWithDnD()
        with patch.object(widget, 'count', return_value=0), \
                patch.object(widget, 'item', side_effect=lambda x: [][x]):

            # WHEN: Calling allItems
            result = widget.allItems()

            # THEN: An instance of a Generator object should be returned. The generator should not yeild any results
            self.assertIsInstance(result, GeneratorType)
            self.assertEqual(list(result), [])

    def test_all_items_list_items(self):
        """
        Test allItems when the list widget contains some items.
        """
        # GIVEN: An instance of ListWidgetWithDnD
        widget = ListWidgetWithDnD()
        with patch.object(widget, 'count', return_value=2), \
                patch.object(widget, 'item', side_effect=lambda x: [5, 3][x]):

            # WHEN: Calling allItems
            result = widget.allItems()

            # THEN: An instance of a Generator object should be returned. The generator should not yeild any results
            self.assertIsInstance(result, GeneratorType)
            self.assertEqual(list(result), [5, 3])

    def test_paint_event(self):
        """
        Test the paintEvent method when the list is not empty
        """
        # GIVEN: An instance of ListWidgetWithDnD with a mocked out count methode which returns 1
        #       (i.e the list has an item)
        widget = ListWidgetWithDnD()
        with patch('openlp.core.ui.lib.listwidgetwithdnd.QtWidgets.QListWidget.paintEvent') as mocked_paint_event, \
                patch.object(widget, 'count', return_value=1), \
                patch.object(widget, 'viewport') as mocked_viewport:
            mocked_event = MagicMock()

            # WHEN: Calling paintEvent
            widget.paintEvent(mocked_event)

            # THEN: The overridden paintEvnet should have been called
            mocked_paint_event.assert_called_once_with(mocked_event)
            self.assertFalse(mocked_viewport.called)

    def test_paint_event_no_items(self):
        """
        Test the paintEvent method when the list is empty
        """
        # GIVEN: An instance of ListWidgetWithDnD with a mocked out count methode which returns 0
        #       (i.e the list is empty)
        widget = ListWidgetWithDnD()
        mocked_painter_instance = MagicMock()
        mocked_qrect = MagicMock()
        with patch('openlp.core.ui.lib.listwidgetwithdnd.QtWidgets.QListWidget.paintEvent') as mocked_paint_event, \
                patch.object(widget, 'count', return_value=0), \
                patch.object(widget, 'viewport'), \
                patch('openlp.core.ui.lib.listwidgetwithdnd.QtGui.QPainter',
                      return_value=mocked_painter_instance) as mocked_qpainter, \
                patch('openlp.core.ui.lib.listwidgetwithdnd.QtCore.QRect', return_value=mocked_qrect):
            mocked_event = MagicMock()

            # WHEN: Calling paintEvent
            widget.paintEvent(mocked_event)

            # THEN: The overridden paintEvnet should have been called, and some text should be drawn.
            mocked_paint_event.assert_called_once_with(mocked_event)
            mocked_qpainter.assert_called_once_with(widget.viewport())
            mocked_painter_instance.drawText.assert_called_once_with(mocked_qrect, 4100, 'No Search Results')
