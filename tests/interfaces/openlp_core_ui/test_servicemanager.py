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
    Package to test the openlp.core.lib package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common import Registry
from openlp.core.lib import ScreenList, ServiceItem, ItemCapabilities
from openlp.core.ui.mainwindow import MainWindow
from openlp.core.ui.servicemanager import ServiceManagerList
from openlp.core.lib.serviceitem import ServiceItem

from tests.helpers.testmixin import TestMixin

from PyQt5 import QtCore, QtGui, QtWidgets


class TestServiceManager(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        ScreenList.create(self.app.desktop())
        Registry().register('application', MagicMock())
        # Mock classes and methods used by mainwindow.
        with patch('openlp.core.ui.mainwindow.SettingsForm') as mocked_settings_form, \
                patch('openlp.core.ui.mainwindow.ImageManager') as mocked_image_manager, \
                patch('openlp.core.ui.mainwindow.LiveController') as mocked_live_controller, \
                patch('openlp.core.ui.mainwindow.PreviewController') as mocked_preview_controller, \
                patch('openlp.core.ui.mainwindow.OpenLPDockWidget') as mocked_dock_widget, \
                patch('openlp.core.ui.mainwindow.QtWidgets.QToolBox') as mocked_q_tool_box_class, \
                patch('openlp.core.ui.mainwindow.QtWidgets.QMainWindow.addDockWidget') as mocked_add_dock_method, \
                patch('openlp.core.ui.mainwindow.ThemeManager') as mocked_theme_manager, \
                patch('openlp.core.ui.mainwindow.ProjectorManager') as mocked_projector_manager, \
                patch('openlp.core.ui.mainwindow.Renderer') as mocked_renderer, \
                patch('openlp.core.ui.mainwindow.websockets.WebSocketServer') as mocked_websocketserver, \
                patch('openlp.core.ui.mainwindow.server.HttpServer') as mocked_httpserver:
            self.main_window = MainWindow()
        self.service_manager = Registry().get('service_manager')

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.main_window

    def test_basic_service_manager(self):
        """
        Test the Service Manager UI Functionality
        """
        # GIVEN: A New Service Manager instance

        # WHEN I have set up the display
        self.service_manager.setup_ui(self.service_manager)
        # THEN the count of items should be zero
        self.assertEqual(self.service_manager.service_manager_list.topLevelItemCount(), 0,
                         'The service manager list should be empty ')

    def test_default_context_menu(self):
        """
        Test the context_menu() method with a default service item
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_edit_context_menu(self):
        """
        Test the context_menu() method with a edit service item
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanEdit)
            service_item.edit_id = 1
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_maintain_context_menu(self):
        """
        Test the context_menu() method with a maintain
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanMaintain)
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_loopy_context_menu(self):
        """
        Test the context_menu() method with a loop
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanLoop)
            service_item._raw_frames.append("One")
            service_item._raw_frames.append("Two")
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_start_time_context_menu(self):
        """
        Test the context_menu() method with a start time
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.HasVariableStartTime)
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_auto_start_context_menu(self):
        """
        Test the context_menu() method with can auto start
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()
            self.service_manager.rename_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.rename_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_click_on_new_service(self):
        """
        Test the on_new_service event handler is called by the UI
        """
        # GIVEN: An initial form
        mocked_event = MagicMock()
        self.service_manager.on_new_service_clicked = mocked_event
        self.service_manager.setup_ui(self.service_manager)

        # WHEN displaying the UI and pressing cancel
        new_service = self.service_manager.toolbar.actions['newService']
        new_service.trigger()

        assert mocked_event.call_count == 1, 'The on_new_service_clicked method should have been called once'

    def test_expand_selection_on_right_arrow(self):
        """
        Test that a right arrow key press event calls the on_expand_selection function
        """
        # GIVEN a mocked expand function
        self.service_manager.on_expand_selection = MagicMock()

        # WHEN the right arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Right, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_expand_selection function should have been called.
        self.service_manager.on_expand_selection.assert_called_once_with()

    def test_collapse_selection_on_left_arrow(self):
        """
        Test that a left arrow key press event calls the on_collapse_selection function
        """
        # GIVEN a mocked collapse function
        self.service_manager.on_collapse_selection = MagicMock()

        # WHEN the left arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Left, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_collapse_selection function should have been called.
        self.service_manager.on_collapse_selection.assert_called_once_with()

    def test_move_selection_down_on_down_arrow(self):
        """
        Test that a down arrow key press event calls the on_move_selection_down function
        """
        # GIVEN a mocked move down function
        self.service_manager.on_move_selection_down = MagicMock()

        # WHEN the down arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Down, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_move_selection_down function should have been called.
        self.service_manager.on_move_selection_down.assert_called_once_with()

    def test_move_selection_up_on_up_arrow(self):
        """
        Test that an up arrow key press event calls the on_move_selection_up function
        """
        # GIVEN a mocked move up function
        self.service_manager.on_move_selection_up = MagicMock()

        # WHEN the up arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Up, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_move_selection_up function should have been called.
        self.service_manager.on_move_selection_up.assert_called_once_with()

    def _setup_service_manager_list(self):
        self.service_manager.expanded = MagicMock()
        self.service_manager.collapsed = MagicMock()
        verse_1 = QtWidgets.QTreeWidgetItem(0)
        verse_2 = QtWidgets.QTreeWidgetItem(0)
        song_item = QtWidgets.QTreeWidgetItem(0)
        song_item.addChild(verse_1)
        song_item.addChild(verse_2)
        self.service_manager.setup_ui(self.service_manager)
        self.service_manager.service_manager_list.addTopLevelItem(song_item)
        return verse_1, verse_2, song_item

    def test_on_expand_selection(self):
        """
        Test that the on_expand_selection function successfully expands an item and moves to its first child
        """
        # GIVEN a mocked servicemanager list
        verse_1, verse_2, song_item = self._setup_service_manager_list()
        self.service_manager.service_manager_list.setCurrentItem(song_item)
        # Reset expanded function in case it has been called and/or changed in initialisation of the service manager.
        self.service_manager.expanded = MagicMock()

        # WHEN on_expand_selection is called
        self.service_manager.on_expand_selection()

        # THEN selection should be expanded
        selected_index = self.service_manager.service_manager_list.currentIndex()
        above_selected_index = self.service_manager.service_manager_list.indexAbove(selected_index)
        self.assertTrue(self.service_manager.service_manager_list.isExpanded(above_selected_index),
                        'Item should have been expanded')
        self.service_manager.expanded.assert_called_once_with(song_item)

    def test_on_collapse_selection_with_parent_selected(self):
        """
        Test that the on_collapse_selection function successfully collapses an item
        """
        # GIVEN a mocked servicemanager list
        verse_1, verse_2, song_item = self._setup_service_manager_list()
        self.service_manager.service_manager_list.setCurrentItem(song_item)
        self.service_manager.service_manager_list.expandItem(song_item)

        # Reset collapsed function in case it has been called and/or changed in initialisation of the service manager.
        self.service_manager.collapsed = MagicMock()

        # WHEN on_expand_selection is called
        self.service_manager.on_collapse_selection()

        # THEN selection should be expanded
        selected_index = self.service_manager.service_manager_list.currentIndex()
        self.assertFalse(self.service_manager.service_manager_list.isExpanded(selected_index),
                         'Item should have been collapsed')
        self.assertTrue(self.service_manager.service_manager_list.currentItem() == song_item,
                        'Top item should have been selected')
        self.service_manager.collapsed.assert_called_once_with(song_item)

    def test_on_collapse_selection_with_child_selected(self):
        """
        Test that the on_collapse_selection function successfully collapses child's parent item
        and moves selection to its parent.
        """
        # GIVEN a mocked servicemanager list
        verse_1, verse_2, song_item = self._setup_service_manager_list()
        self.service_manager.service_manager_list.setCurrentItem(verse_2)
        self.service_manager.service_manager_list.expandItem(song_item)
        # Reset collapsed function in case it has been called and/or changed in initialisation of the service manager.
        self.service_manager.collapsed = MagicMock()

        # WHEN on_expand_selection is called
        self.service_manager.on_collapse_selection()

        # THEN selection should be expanded
        selected_index = self.service_manager.service_manager_list.currentIndex()
        self.assertFalse(self.service_manager.service_manager_list.isExpanded(selected_index),
                         'Item should have been collapsed')
        self.assertTrue(self.service_manager.service_manager_list.currentItem() == song_item,
                        'Top item should have been selected')
        self.service_manager.collapsed.assert_called_once_with(song_item)
