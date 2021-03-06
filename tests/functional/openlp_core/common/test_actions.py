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
Package to test the openlp.core.common.actions package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from PyQt5 import QtGui, QtCore, QtWidgets

import openlp.core.common.actions
from openlp.core.common.actions import CategoryActionList, ActionList
from openlp.core.common.settings import Settings
from tests.helpers.testmixin import TestMixin


class TestCategoryActionList(TestCase):
    def setUp(self):
        """
        Create an instance and a few example actions.
        """
        self.action1 = MagicMock()
        self.action1.text.return_value = 'first'
        self.action2 = MagicMock()
        self.action2.text.return_value = 'second'
        self.list = CategoryActionList()

    def tearDown(self):
        """
        Clean up
        """
        del self.list

    def test_contains(self):
        """
        Test the __contains__() method
        """
        # GIVEN: The list.
        # WHEN: Add an action
        self.list.append(self.action1)

        # THEN: The actions should (not) be in the list.
        assert self.action1 in self.list
        assert self.action2 not in self.list

    def test_len(self):
        """
        Test the __len__ method
        """
        # GIVEN: The list.
        # WHEN: Do nothing.
        # THEN: Check the length.
        assert len(self.list) == 0, "The length should be 0."

        # GIVEN: The list.
        # WHEN: Append an action.
        self.list.append(self.action1)

        # THEN: Check the length.
        assert len(self.list) == 1, "The length should be 1."

    def test_append(self):
        """
        Test the append() method
        """
        # GIVEN: The list.
        # WHEN: Append an action.
        self.list.append(self.action1)
        self.list.append(self.action2)

        # THEN: Check if the actions are in the list and check if they have the correct weights.
        assert self.action1 in self.list
        assert self.action2 in self.list
        assert self.list.actions[0] == (0, self.action1)
        assert self.list.actions[1] == (1, self.action2)

    def test_add(self):
        """
        Test the add() method
        """
        # GIVEN: The list and weights.
        action1_weight = 42
        action2_weight = 41

        # WHEN: Add actions and their weights.
        self.list.add(self.action1, action1_weight)
        self.list.add(self.action2, action2_weight)

        # THEN: Check if they were added and have the specified weights.
        assert self.action1 in self.list
        assert self.action2 in self.list
        # Now check if action1 is second and action2 is first (due to their weights).
        assert self.list.actions[0] == (41, self.action2)
        assert self.list.actions[1] == (42, self.action1)

    def test_iterator(self):
        """
        Test the __iter__ and __next__ methods
        """
        # GIVEN: The list including two actions
        self.list.add(self.action1)
        self.list.add(self.action2)

        # WHEN: Iterating over the list
        local_list = [a for a in self.list]
        # THEN: Make sure they are returned in correct order
        assert len(self.list) == 2
        assert local_list[0] is self.action1
        assert local_list[1] is self.action2

    def test_remove(self):
        """
        Test the remove() method
        """
        # GIVEN: The list
        self.list.append(self.action1)

        # WHEN: Delete an item from the list.
        self.list.remove(self.action1)

        # THEN: Now the element should not be in the list anymore.
        assert self.action1 not in self.list

    def test_remove_not_in_list(self):
        """
        Test the remove() method when action not in list
        """
        with patch.object(openlp.core.common.actions, 'log') as mock_log:
            log_warn_calls = [call('Action "" does not exist.')]

            # GIVEN: The list
            self.list.append(self.action1)

            # WHEN: Delete an item not in the list.
            self.list.remove('')

            # THEN: Warning should be logged
            mock_log.warning.assert_has_calls(log_warn_calls)


class TestActionList(TestCase, TestMixin):
    """
    Test the ActionList class
    """

    def setUp(self):
        """
        Prepare the tests
        """
        self.setup_application()
        self.action_list = ActionList.get_instance()
        self.build_settings()
        self.settings = Settings()
        self.settings.beginGroup('shortcuts')

    def tearDown(self):
        """
        Clean up
        """
        self.settings.endGroup()
        self.destroy_settings()

    def test_add_action_same_parent(self):
        """
        ActionList test - Tests the add_action method. The actions have the same parent, the same shortcuts and both
        have the QtCore.Qt.WindowShortcut shortcut context set.
        """
        # GIVEN: Two actions with the same shortcuts.
        parent = QtCore.QObject()
        action1 = QtWidgets.QAction(parent)
        action1.setObjectName('action1')
        action_with_same_shortcuts1 = QtWidgets.QAction(parent)
        action_with_same_shortcuts1.setObjectName('action_with_same_shortcuts1')
        # Add default shortcuts to Settings class.
        default_shortcuts = {
            'shortcuts/action1': [QtGui.QKeySequence(QtCore.Qt.Key_A), QtGui.QKeySequence(QtCore.Qt.Key_B)],
            'shortcuts/action_with_same_shortcuts1': [QtGui.QKeySequence(QtCore.Qt.Key_B),
                                                      QtGui.QKeySequence(QtCore.Qt.Key_A)]
        }
        Settings.extend_default_settings(default_shortcuts)

        # WHEN: Add the two actions to the action list.
        self.action_list.add_action(action1, 'example_category')
        self.action_list.add_action(action_with_same_shortcuts1, 'example_category')
        # Remove the actions again.
        self.action_list.remove_action(action1, 'example_category')
        self.action_list.remove_action(action_with_same_shortcuts1, 'example_category')

        # THEN: As both actions have the same shortcuts, they should be removed from one action.
        assert len(action1.shortcuts()) == 2, 'The action should have two shortcut assigned.'
        assert len(action_with_same_shortcuts1.shortcuts()) == 0, 'The action should not have a shortcut assigned.'

    def test_add_action_different_parent(self):
        """
        ActionList test - Tests the add_action method. The actions have the different parent, the same shortcuts and
        both have the QtCore.Qt.WindowShortcut shortcut context set.
        """
        # GIVEN: Two actions with the same shortcuts.
        parent = QtCore.QObject()
        action2 = QtWidgets.QAction(parent)
        action2.setObjectName('action2')
        second_parent = QtCore.QObject()
        action_with_same_shortcuts2 = QtWidgets.QAction(second_parent)
        action_with_same_shortcuts2.setObjectName('action_with_same_shortcuts2')
        # Add default shortcuts to Settings class.
        default_shortcuts = {
            'shortcuts/action2': [QtGui.QKeySequence(QtCore.Qt.Key_C), QtGui.QKeySequence(QtCore.Qt.Key_D)],
            'shortcuts/action_with_same_shortcuts2': [QtGui.QKeySequence(QtCore.Qt.Key_D),
                                                      QtGui.QKeySequence(QtCore.Qt.Key_C)]
        }
        Settings.extend_default_settings(default_shortcuts)

        # WHEN: Add the two actions to the action list.
        self.action_list.add_action(action2, 'example_category')
        self.action_list.add_action(action_with_same_shortcuts2, 'example_category')
        # Remove the actions again.
        self.action_list.remove_action(action2, 'example_category')
        self.action_list.remove_action(action_with_same_shortcuts2, 'example_category')

        # THEN: As both actions have the same shortcuts, they should be removed from one action.
        assert len(action2.shortcuts()) == 2, 'The action should have two shortcut assigned.'
        assert len(action_with_same_shortcuts2.shortcuts()) == 0, 'The action should not have a shortcut assigned.'

    def test_add_action_different_context(self):
        """
        ActionList test - Tests the add_action method. The actions have the different parent, the same shortcuts and
        both have the QtCore.Qt.WidgetShortcut shortcut context set.
        """
        # GIVEN: Two actions with the same shortcuts.
        parent = QtCore.QObject()
        action3 = QtWidgets.QAction(parent)
        action3.setObjectName('action3')
        action3.setShortcutContext(QtCore.Qt.WidgetShortcut)
        second_parent = QtCore.QObject()
        action_with_same_shortcuts3 = QtWidgets.QAction(second_parent)
        action_with_same_shortcuts3.setObjectName('action_with_same_shortcuts3')
        action_with_same_shortcuts3.setShortcutContext(QtCore.Qt.WidgetShortcut)
        # Add default shortcuts to Settings class.
        default_shortcuts = {
            'shortcuts/action3': [QtGui.QKeySequence(QtCore.Qt.Key_E), QtGui.QKeySequence(QtCore.Qt.Key_F)],
            'shortcuts/action_with_same_shortcuts3': [QtGui.QKeySequence(QtCore.Qt.Key_E),
                                                      QtGui.QKeySequence(QtCore.Qt.Key_F)]
        }
        Settings.extend_default_settings(default_shortcuts)

        # WHEN: Add the two actions to the action list.
        self.action_list.add_action(action3, 'example_category2')
        self.action_list.add_action(action_with_same_shortcuts3, 'example_category2')
        # Remove the actions again.
        self.action_list.remove_action(action3, 'example_category2')
        self.action_list.remove_action(action_with_same_shortcuts3, 'example_category2')

        # THEN: Both action should keep their shortcuts.
        assert len(action3.shortcuts()) == 2, 'The action should have two shortcut assigned.'
        assert len(action_with_same_shortcuts3.shortcuts()) == 2, 'The action should have two shortcuts assigned.'
