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
Module to test the EditCustomForm.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from PyQt5 import QtCore, QtGui, QtTest, QtWidgets

from openlp.core.common import Registry
from openlp.core.lib.searchedit import SearchEdit

from tests.helpers.testmixin import TestMixin


class SearchTypes(object):
    """
    Types of search
    """
    First = 0
    Second = 1


SECOND_PLACEHOLDER_TEXT = "Second Placeholder Text"
SEARCH_TYPES = [(SearchTypes.First, QtGui.QIcon(), "First", "First Placeholder Text"),
                (SearchTypes.Second, QtGui.QIcon(), "Second", SECOND_PLACEHOLDER_TEXT)]


class TestSearchEdit(TestCase, TestMixin):
    """
    Test the EditCustomForm.
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtWidgets.QMainWindow()
        Registry().register('main_window', self.main_window)

        settings_patcher = patch(
            'openlp.core.lib.searchedit.Settings', return_value=MagicMock(**{'value.return_value': SearchTypes.First}))
        self.addCleanup(settings_patcher.stop)
        self.mocked_settings = settings_patcher.start()

        self.search_edit = SearchEdit(self.main_window, 'settings_section')
        # To complete set up we have to set the search types.
        self.search_edit.set_search_types(SEARCH_TYPES)

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.search_edit
        del self.main_window

    def test_set_search_types(self):
        """
        Test setting the search types of the search edit.
        """
        # GIVEN: The search edit with the search types set. NOTE: The set_search_types(types) is called in the setUp()
        # method!

        # WHEN:

        # THEN: The first search type should be the first one in the list. The selected type should be saved in the
        #       settings
        self.assertEqual(self.search_edit.current_search_type(), SearchTypes.First,
                         "The first search type should be selected.")
        self.mocked_settings().setValue.assert_called_once_with('settings_section/last search type', 0)

    def test_set_current_search_type(self):
        """
        Test if changing the search type works.
        """
        # GIVEN:
        # WHEN: Change the search type
        result = self.search_edit.set_current_search_type(SearchTypes.Second)

        # THEN:
        self.assertTrue(result, "The call should return success (True).")
        self.assertEqual(self.search_edit.current_search_type(), SearchTypes.Second,
                         "The search type should be SearchTypes.Second")
        self.assertEqual(self.search_edit.placeholderText(), SECOND_PLACEHOLDER_TEXT,
                         "The correct placeholder text should be 'Second Placeholder Text'.")
        self.mocked_settings().setValue.assert_has_calls(
            [call('settings_section/last search type', 0), call('settings_section/last search type', 1)])

    def test_clear_button_visibility(self):
        """
        Test if the clear button is hidden/shown correctly.
        """
        # GIVEN: Everything is left to its defaults (hidden).
        assert self.search_edit.clear_button.isHidden(), "Pre condition not met. Button should be hidden."

        # WHEN: Type something in the search edit.
        QtTest.QTest.keyPress(self.search_edit, QtCore.Qt.Key_A)
        QtTest.QTest.keyRelease(self.search_edit, QtCore.Qt.Key_A)

        # THEN: The clear button should not be hidden any more.
        assert not self.search_edit.clear_button.isHidden(), "The clear button should be visible."

    def test_press_clear_button(self):
        """
        Check if the search edit behaves correctly when pressing the clear button.
        """
        # GIVEN: A search edit with text.
        QtTest.QTest.keyPress(self.search_edit, QtCore.Qt.Key_A)
        QtTest.QTest.keyRelease(self.search_edit, QtCore.Qt.Key_A)

        # WHEN: Press the clear button.
        QtTest.QTest.mouseClick(self.search_edit.clear_button, QtCore.Qt.LeftButton)

        # THEN: The search edit text should be cleared and the button be hidden.
        assert not self.search_edit.text(), "The search edit should not have any text."
        assert self.search_edit.clear_button.isHidden(), "The clear button should be hidden."
