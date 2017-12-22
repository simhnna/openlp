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
This module contains tests for the lib submodule of the Presentations plugin.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from PyQt5 import QtCore, QtWidgets

from tests.helpers.testmixin import TestMixin

from openlp.core.common.registry import Registry
from openlp.core.lib import MediaManagerItem
from openlp.plugins.bibles.lib.mediaitem import BibleMediaItem, BibleSearch, ResultsTab, SearchStatus, SearchTabs, \
    get_reference_separators, VALID_TEXT_SEARCH


class TestBibleMediaItemModulefunctions(TestCase):
    """
    Test the module functions in :mod:`openlp.plugins.bibles.lib.mediaitem`
    """

    def test_valid_text_search(self):
        """
        Test the compiled VALID_TEXT_SEARCH regex expression
        """
        # GIVEN: Some test data and some expected results
        test_data = [('a a a', None), ('a ab a', None), ('a abc a', ((2, 5),)), ('aa 123 aa', ((3, 6),))]
        for data, expected_result in test_data:

            # WHEN: Calling search on the compiled regex expression
            result = VALID_TEXT_SEARCH.search(data)

            # THEN: The expected result should be returned
            if expected_result is None:
                assert result is None, expected_result
            else:
                assert result.regs == expected_result

    def test_get_reference_separators(self):
        """
        Test the module function get_reference_separators
        """
        # GIVEN: A mocked get_reference_separator from the :mod:`openlp.plugins.bibles.lib` module
        with patch('openlp.plugins.bibles.lib.mediaitem.get_reference_separator') as mocked_get_reference_separator:

            # WHEN: Calling get_reference_separators
            result = get_reference_separators()

            # THEN: The result should contain the 'verse', 'range', 'list' keys and get_reference_separator should have
            #       been called with the expected values.
            assert all(key in result for key in ('verse', 'range', 'list')) is True
            mocked_get_reference_separator.assert_has_calls(
                [call('sep_v_display'), call('sep_r_display'), call('sep_l_display')])

    def test_bible_search_enum(self):
        """
        Test that the :class:`BibleSearch` class contains the expected enumerations
        """
        # GIVEN: The BibleSearch class
        # WHEN: Testing its attributes
        # THEN: The BibleSearch class should have the following enumrations
        assert hasattr(BibleSearch, 'Combined')
        assert hasattr(BibleSearch, 'Reference')
        assert hasattr(BibleSearch, 'Text')

    def test_bible_media_item_subclass(self):
        """
        Test that the :class:`BibleMediaItem` class is a subclass of the :class:`MediaManagerItem` class
        """
        # GIVEN: The :class:`BibleMediaItem`
        # WHEN: Checking if it is a subclass of MediaManagerItem
        # THEN: BibleMediaItem should be a subclass of MediaManagerItem
        assert issubclass(BibleMediaItem, MediaManagerItem)

    def test_bible_media_item_signals(self):
        """
        Test that the :class:`BibleMediaItem` class has the expected signals
        """
        # GIVEN: The :class:`BibleMediaItem`
        # THEN:  The :class:`BibleMediaItem` should contain the following pyqtSignal's
        assert hasattr(BibleMediaItem, 'bibles_go_live')
        assert hasattr(BibleMediaItem, 'bibles_add_to_service')
        assert isinstance(BibleMediaItem.bibles_go_live, QtCore.pyqtSignal)
        assert isinstance(BibleMediaItem.bibles_add_to_service, QtCore.pyqtSignal)


class TestMediaItem(TestCase, TestMixin):
    """
    Test the bible mediaitem methods.
    """

    def setUp(self):
        """
        Set up the components need for all tests.
        """
        log_patcher = patch('openlp.plugins.bibles.lib.mediaitem.log')
        self.addCleanup(log_patcher.stop)
        self.mocked_log = log_patcher.start()

        qtimer_patcher = patch('openlp.plugins.bibles.lib.mediaitem.QtCore.QTimer')
        self.addCleanup(qtimer_patcher.stop)
        self.mocked_qtimer = qtimer_patcher.start()

        self.mocked_settings_instance = MagicMock()
        self.mocked_settings_instance.value.side_effect = lambda key: self.setting_values[key]
        settings_patcher = patch(
            'openlp.plugins.bibles.lib.mediaitem.Settings', return_value=self.mocked_settings_instance)
        self.addCleanup(settings_patcher.stop)
        self.mocked_settings = settings_patcher.start()

        Registry.create()

        # self.setup_application()
        self.mocked_application = MagicMock()
        Registry().register('application', self.mocked_application)
        self.mocked_main_window = MagicMock()
        Registry().register('main_window', self.mocked_main_window)

        self.mocked_plugin = MagicMock()
        with patch('openlp.plugins.bibles.lib.mediaitem.build_icon'), \
                patch('openlp.plugins.bibles.lib.mediaitem.MediaManagerItem._setup'), \
                patch('openlp.plugins.bibles.lib.mediaitem.BibleMediaItem.setup_item'):
            self.media_item = BibleMediaItem(None, self.mocked_plugin)

        self.media_item.settings_section = 'bibles'
        self.media_item.results_view_tab = MagicMock()

        self.mocked_book_1 = MagicMock(**{'get_name.return_value': 'Book 1', 'book_reference_id': 1})
        self.mocked_book_2 = MagicMock(**{'get_name.return_value': 'Book 2', 'book_reference_id': 2})
        self.mocked_book_3 = MagicMock(**{'get_name.return_value': 'Book 3', 'book_reference_id': 3})
        self.mocked_book_4 = MagicMock(**{'get_name.return_value': 'Book 4', 'book_reference_id': 4})

        self.book_list_1 = [self.mocked_book_1, self.mocked_book_2, self.mocked_book_3]
        self.book_list_2 = [self.mocked_book_2, self.mocked_book_3, self.mocked_book_4]
        self.mocked_bible_1 = MagicMock(**{'get_books.return_value': self.book_list_1})
        self.mocked_bible_1.name = 'Bible 1'
        self.mocked_bible_2 = MagicMock(**{'get_books.return_value': self.book_list_2})
        self.mocked_bible_2.name = 'Bible 2'

    def test_media_item_instance(self):
        """
        When creating an instance of C test that it is also an instance of
        :class:`MediaManagerItem`
        """
        # GIVEN: An instance of :class:`BibleMediaItem`
        # WEHN: Checking its class
        # THEN: It should be a subclass of :class:`MediaManagerItem`
        assert isinstance(self.media_item, MediaManagerItem)

    def test_steup_item(self):
        """
        Test the setup_item method
        """
        # Could have tested the connection of the custom signals, however they're class vairables, and I could not find
        # a way to properly test them.

        # GIVEN: A mocked Registry.register_function method and an instance of BibleMediaItem
        with patch.object(Registry(), 'register_function') as mocked_register_function:

            # WHEN: Calling setup_itme
            self.media_item.setup_item()

            # THEN: Registry.register_function method should have been called with the reload_bibles method
            mocked_register_function.assert_called_once_with('bibles_load_list', self.media_item.reload_bibles)

    def test_required_icons(self):
        """
        Test that all the required icons are set properly.
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        # WHEN: required_icons is called
        self.media_item.required_icons()

        # THEN: The correct icons should be set
        assert self.media_item.has_import_icon is True, 'Check that the icon is as True.'
        assert self.media_item.has_new_icon is False, 'Check that the icon is called as False.'
        assert self.media_item.has_edit_icon is True, 'Check that the icon is called as True.'
        assert self.media_item.has_delete_icon is True, 'Check that the icon is called as True.'
        assert self.media_item.add_to_service_item is False, 'Check that the icon is called as False'

    def test_on_focus_search_tab_visible(self):
        """
        Test the correct widget gets focus when the BibleMediaItem receives focus
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out tabs and primary widgets
        self.media_item.search_tab = MagicMock(**{'isVisible.return_value': True})
        self.media_item.search_edit = MagicMock()
        self.media_item.select_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.options_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.version_combo_box = MagicMock()

        # WHEN: Calling on_focus
        self.media_item.on_focus()

        # THEN: search_edit should now have focus and its text selected
        self.media_item.search_edit.assert_has_calls([call.setFocus(), call.selectAll()])
        self.media_item.select_book_combo_box.assert_not_called()
        self.media_item.version_combo_box.setFocus.assert_not_called()

    def test_on_focus_select_tab_visible(self):
        """
        Test the correct widget gets focus when the BibleMediaItem receives focus
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out tabs and primary widgets
        self.media_item.search_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.search_edit = MagicMock()
        self.media_item.select_tab = MagicMock(**{'isVisible.return_value': True})
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.options_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.version_combo_box = MagicMock()

        # WHEN: Calling on_focus
        self.media_item.on_focus()

        # THEN: select_book_combo_box should have focus
        self.media_item.search_edit.setFocus.assert_not_called()
        self.media_item.search_edit.selectAll.assert_not_called()
        self.media_item.select_book_combo_box.setFocus.assert_called_once_with()
        self.media_item.version_combo_box.setFocus.assert_not_called()

    def test_on_focus_options_tab_visible(self):
        """
        Test the correct widget gets focus when the BibleMediaItem receives focus
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out tabs and primary widgets
        self.media_item.search_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.search_edit = MagicMock()
        self.media_item.select_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.options_tab = MagicMock(**{'isVisible.return_value': True})
        self.media_item.version_combo_box = MagicMock()

        # WHEN: Calling on_focus
        self.media_item.on_focus()

        # THEN: version_combo_box have received focus
        self.media_item.search_edit.setFocus.assert_not_called()
        self.media_item.search_edit.selectAll.assert_not_called()
        self.media_item.select_book_combo_box.setFocus.assert_not_called()
        self.media_item.version_combo_box.setFocus.assert_called_once_with()

    def test_config_update_show_second_bible(self):
        """
        Test the config update method
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out settings class with known values
        self.setting_values = {'bibles/second bibles': True}
        self.media_item.general_bible_layout = MagicMock()
        self.media_item.second_combo_box = MagicMock()

        # WHEN: Calling config_update()
        self.media_item.config_update()

        # THEN: second_combo_box() should be set visible
        self.media_item.second_combo_box.setVisible.assert_called_once_with(True)

    def test_config_update_hide_second_bible(self):
        """
        Test the config update method
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out settings class with known values
        self.setting_values = {'bibles/second bibles': False}
        self.media_item.general_bible_layout = MagicMock()
        self.media_item.second_combo_box = MagicMock()

        # WHEN: Calling config_update()
        self.media_item.config_update()

        # THEN: second_combo_box() should hidden
        self.media_item.second_combo_box.setVisible.assert_called_once_with(False)

    def test_initalise(self):
        """
        Test the initalise method
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out settings class with known values
        self.setting_values = {'bibles/reset to combined quick search': False}
        with patch.object(self.media_item, 'populate_bible_combo_boxes'), \
                patch.object(self.media_item, 'config_update'):
            self.media_item.search_edit = MagicMock()

            # WHEN: Calling initialise()
            self.media_item.initialise()

            # THEN: The search_edit search types should have been set.
            assert self.media_item.search_edit.set_search_types.called is True
            assert self.media_item.search_edit.set_current_search_type.called is False

    def test_initalise_reset_search_type(self):
        """
        Test the initalise method
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out settings class with known values
        self.setting_values = {'bibles/reset to combined quick search': True}
        with patch.object(self.media_item, 'populate_bible_combo_boxes'), \
                patch.object(self.media_item, 'config_update'):
            self.media_item.search_edit = MagicMock()

            # WHEN: Calling initialise()
            self.media_item.initialise()

            # THEN: The search_edit search types should have been set and that the current search type should be set to
            #       'Combined'
            assert self.media_item.search_edit.set_search_types.called is True
            self.media_item.search_edit.set_current_search_type.assert_called_once_with(BibleSearch.Combined)

    def test_populate_bible_combo_boxes(self):
        """
        Test populate_bible_combo_boxes method
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out settings class with known values
        bible_1 = MagicMock()
        bible_2 = MagicMock()
        bible_3 = MagicMock()
        self.setting_values = {'bibles/primary bible': bible_2}
        self.media_item.version_combo_box = MagicMock()
        self.media_item.second_combo_box = MagicMock()
        self.mocked_plugin.manager.get_bibles.return_value = \
            {'Bible 2': bible_2, 'Bible 1': bible_1, 'Bible 3': bible_3}
        with patch('openlp.plugins.bibles.lib.mediaitem.get_locale_key', side_effect=lambda x: x), \
                patch('openlp.plugins.bibles.lib.mediaitem.find_and_set_in_combo_box'):

            # WHEN: Calling populate_bible_combo_boxes
            self.media_item.populate_bible_combo_boxes()

            # THEN: The bible combo boxes should be filled with the bible names and data, in a sorted order.
            self.media_item.version_combo_box.addItem.assert_has_calls(
                [call('Bible 1', bible_1), call('Bible 2', bible_2), call('Bible 3', bible_3)])
            self.media_item.second_combo_box.addItem.assert_has_calls(
                [call('', None), call('Bible 1', bible_1), call('Bible 2', bible_2), call('Bible 3', bible_3)])

    def test_reload_bibles(self):
        """
        Test reload_bibles
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out settings class with known values
        with patch.object(self.media_item, 'populate_bible_combo_boxes') as mocked_populate_bible_combo_boxes:
            # WHEN: Calling reload_bibles()
            self.media_item.reload_bibles()

            # THEN: The manager reload_bibles method should have been called and the bible combo boxes updated
            self.mocked_plugin.manager.reload_bibles.assert_called_once_with()
            mocked_populate_bible_combo_boxes.assert_called_once_with()

    def test_get_common_books_no_second_book(self):
        """
        Test get_common_books when called with out a second bible
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked first bible
        # WHEN: Calling get_common_books with only one bible
        result = self.media_item.get_common_books(self.mocked_bible_1)

        # THEN: The book of the bible should be returned
        assert result == self.book_list_1

    def test_get_common_books_second_book(self):
        """
        Test get_common_books when called with a second bible
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and two mocked bibles with differing books
        # WHEN: Calling get_common_books with two bibles
        result = self.media_item.get_common_books(self.mocked_bible_1, self.mocked_bible_2)

        # THEN: Only the books contained in both bibles should be returned
        assert result == [self.mocked_book_2, self.mocked_book_3]

    def test_initialise_advanced_bible_no_bible(self):
        """
        Test initialise_advanced_bible when there is no main bible
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.select_book_combo_box = MagicMock()
        with patch.object(self.media_item, 'get_common_books') as mocked_get_common_books:

            # WHEN: Calling initialise_advanced_bible() when there is no main bible
            self.media_item.bible = None
            result = self.media_item.initialise_advanced_bible()

            # THEN: initialise_advanced_bible should return with put calling get_common_books
            assert result is None
            mocked_get_common_books.assert_not_called()

    def test_initialise_advanced_bible_add_books_with_last_id_found(self):
        """
        Test initialise_advanced_bible when the last_id argument is supplied and it is found in the list
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked_book_combo_box which simulates data being found
        #        in the list
        self.media_item.select_book_combo_box = MagicMock(**{'findData.return_value': 2})
        with patch.object(self.media_item, 'get_common_books', return_value=self.book_list_1), \
                patch.object(self.media_item, 'on_advanced_book_combo_box'):

            # WHEN: Calling initialise_advanced_bible() with the last_id argument set
            self.media_item.bible = MagicMock()
            self.media_item.initialise_advanced_bible(10)

            # THEN: The books should be added to the combo box, and the chosen book should be reselected
            self.media_item.select_book_combo_box.addItem.assert_has_calls(
                [call('Book 1', 1), call('Book 2', 2), call('Book 3', 3)])
            self.media_item.select_book_combo_box.setCurrentIndex.assert_called_once_with(2)

    def test_initialise_advanced_bible_add_books_with_last_id_not_found(self):
        """
        Test initialise_advanced_bible when the last_id argument is supplied and it is not found in the list
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked_book_combo_box which simulates data not being
        #          found in the list
        self.media_item.select_book_combo_box = MagicMock(**{'findData.return_value': -1})
        with patch.object(self.media_item, 'get_common_books', return_value=self.book_list_1), \
                patch.object(self.media_item, 'on_advanced_book_combo_box'):

            # WHEN: Calling initialise_advanced_bible() with the last_id argument set
            self.media_item.bible = MagicMock()
            self.media_item.initialise_advanced_bible(10)

            # THEN: The books should be added to the combo box, and the first book should be selected
            self.media_item.select_book_combo_box.addItem.assert_has_calls(
                [call('Book 1', 1), call('Book 2', 2), call('Book 3', 3)])
            self.media_item.select_book_combo_box.setCurrentIndex.assert_called_once_with(0)

    def test_update_auto_completer_search_no_bible(self):
        """
        Test update_auto_completer when there is no main bible selected and the search_edit type is
        'BibleSearch.Reference'
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked search_edit
        mocked_search_edit = MagicMock(**{'current_search_type.return_value': BibleSearch.Reference})
        self.media_item.search_edit = mocked_search_edit
        self.media_item.bible = None
        with patch.object(self.media_item, 'get_common_books') as mocked_get_common_books, \
                patch('openlp.plugins.bibles.lib.mediaitem.set_case_insensitive_completer') \
                as mocked_set_case_insensitive_completer:

            # WHEN: Calling update_auto_completer
            self.media_item.update_auto_completer()

            # THEN: get_common_books should not have been called. set_case_insensitive_completer should have been called
            #       with an empty list
            mocked_get_common_books.assert_not_called()
            mocked_set_case_insensitive_completer.assert_called_once_with([], mocked_search_edit)

    def test_update_auto_completer_search_reference_type(self):
        """
        Test update_auto_completer when a main bible is selected and the search_edit type is 'BibleSearch.Reference'
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked search_edit
        mocked_search_edit = MagicMock(**{'current_search_type.return_value': BibleSearch.Reference})
        self.media_item.search_edit = mocked_search_edit
        self.media_item.bible = MagicMock()
        with patch.object(self.media_item, 'get_common_books', return_value=self.book_list_1), \
                patch('openlp.plugins.bibles.lib.mediaitem.get_locale_key', side_effect=lambda x: x), \
                patch('openlp.plugins.bibles.lib.mediaitem.set_case_insensitive_completer') \
                as mocked_set_case_insensitive_completer:

            # WHEN: Calling update_auto_completer
            self.media_item.update_auto_completer()

            # THEN: set_case_insensitive_completer should have been called with the names of the books + space in order
            mocked_set_case_insensitive_completer.assert_called_once_with(
                ['Book 1 ', 'Book 2 ', 'Book 3 '], mocked_search_edit)

    def test_update_auto_completer_search_combined_type(self):
        """
        Test update_auto_completer when a main bible is selected and the search_edit type is 'BibleSearch.Combined'
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked search_edit
        mocked_search_edit = MagicMock(**{'current_search_type.return_value': BibleSearch.Combined})
        self.media_item.search_edit = mocked_search_edit
        self.media_item.bible = MagicMock()
        with patch.object(self.media_item, 'get_common_books', return_value=self.book_list_1), \
                patch('openlp.plugins.bibles.lib.mediaitem.get_locale_key', side_effect=lambda x: x), \
                patch('openlp.plugins.bibles.lib.mediaitem.set_case_insensitive_completer') \
                as mocked_set_case_insensitive_completer:

            # WHEN: Calling update_auto_completer
            self.media_item.update_auto_completer()

            # THEN: set_case_insensitive_completer should have been called with the names of the books + space in order
            mocked_set_case_insensitive_completer.assert_called_once_with(
                ['Book 1 ', 'Book 2 ', 'Book 3 '], mocked_search_edit)

    def test_on_import_click_no_import_wizard_attr(self):
        """
        Test on_import_click when media_item does not have the `import_wizard` attribute. And the wizard was canceled.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked BibleImportForm
        mocked_bible_import_form_instance = MagicMock(**{'exec.return_value': False})
        with patch('openlp.plugins.bibles.lib.mediaitem.BibleImportForm',
                   return_value=mocked_bible_import_form_instance) as mocked_bible_import_form, \
                patch.object(self.media_item, 'reload_bibles') as mocked_reload_bibles:

            # WHEN: Calling on_import_click
            self.media_item.on_import_click()

            # THEN: BibleImport wizard should have been instianted and reload_bibles should not have been called
            assert mocked_bible_import_form.called is True
            assert mocked_reload_bibles.called is False

    def test_on_import_click_wizard_not_canceled(self):
        """
        Test on_import_click when the media item has the import_wizard attr set and wizard completes sucessfully.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked import_wizard
        mocked_import_wizard = MagicMock(**{'exec.return_value': True})
        self.media_item.import_wizard = mocked_import_wizard

        with patch.object(self.media_item, 'reload_bibles') as mocked_reload_bibles:

            # WHEN: Calling on_import_click
            self.media_item.on_import_click()

            # THEN: BibleImport wizard should have been instianted and reload_bibles should not have been called
            assert mocked_import_wizard.called is False
            assert mocked_reload_bibles.called is True

    def test_on_edit_click_no_bible(self):
        """
        Test on_edit_click when there is no main bible selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        with patch('openlp.plugins.bibles.lib.mediaitem.EditBibleForm') as mocked_edit_bible_form:

            # WHEN: A main bible is not selected and on_edit_click is called
            self.media_item.bible = None
            self.media_item.on_edit_click()

            # THEN: EditBibleForm should not have been instianted
            assert mocked_edit_bible_form.called is False

    def test_on_edit_click_user_cancel_edit_form(self):
        """
        Test on_edit_click when the user cancels the EditBibleForm
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked EditBibleForm which returns False when exec is
        #        called
        self.media_item.bible = MagicMock()
        mocked_edit_bible_form_instance = MagicMock(**{'exec.return_value': False})
        with patch('openlp.plugins.bibles.lib.mediaitem.EditBibleForm', return_value=mocked_edit_bible_form_instance) \
                as mocked_edit_bible_form, \
                patch.object(self.media_item, 'reload_bibles') as mocked_reload_bibles:

            # WHEN: on_edit_click is called, and the user cancels the EditBibleForm
            self.media_item.on_edit_click()

            # THEN: EditBibleForm should have been been instianted but reload_bibles should not have been called
            assert mocked_edit_bible_form.called is True
            assert mocked_reload_bibles.called is False

    def test_on_edit_click_user_accepts_edit_form(self):
        """
        Test on_edit_click when the user accepts the EditBibleForm
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked EditBibleForm which returns True when exec is
        #        called
        self.media_item.bible = MagicMock()
        mocked_edit_bible_form_instance = MagicMock(**{'exec.return_value': True})
        with patch('openlp.plugins.bibles.lib.mediaitem.EditBibleForm',
                   return_value=mocked_edit_bible_form_instance) \
                as mocked_edit_bible_form, \
                patch.object(self.media_item, 'reload_bibles') as mocked_reload_bibles:

            # WHEN: on_edit_click is called, and the user accpets the EditBibleForm
            self.media_item.on_edit_click()

            # THEN: EditBibleForm should have been been instianted and reload_bibles should have been called
            assert mocked_edit_bible_form.called is True
            assert mocked_reload_bibles.called is True

    def test_on_delete_click_no_bible(self):
        """
        Test on_delete_click when there is no main bible selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        with patch('openlp.plugins.bibles.lib.mediaitem.QtWidgets.QMessageBox') as mocked_qmessage_box:

            # WHEN: A main bible is not selected and on_delete_click is called
            self.media_item.bible = None
            self.media_item.on_delete_click()

            # THEN: QMessageBox.question should not have been called
            assert mocked_qmessage_box.question.called is False

    def test_on_delete_click_response_no(self):
        """
        Test on_delete_click when the user selects no from the message box
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a QMessageBox which reutrns QtWidgets.QMessageBox.No
        self.media_item.bible = MagicMock()
        with patch('openlp.plugins.bibles.lib.mediaitem.QtWidgets.QMessageBox.question',
                   return_value=QtWidgets.QMessageBox.No) as mocked_qmessage_box:

            # WHEN: on_delete_click is called
            self.media_item.on_delete_click()

            # THEN: QMessageBox.question should have been called, but the delete_bible should not have been called
            assert mocked_qmessage_box.called is True
            assert self.mocked_plugin.manager.delete_bible.called is False

    def test_on_delete_click_response_yes(self):
        """
        Test on_delete_click when the user selects yes from the message box
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a QMessageBox which reutrns QtWidgets.QMessageBox.Yes
        self.media_item.bible = MagicMock()
        with patch('openlp.plugins.bibles.lib.mediaitem.QtWidgets.QMessageBox.question',
                   return_value=QtWidgets.QMessageBox.Yes) as mocked_qmessage_box, \
                patch.object(self.media_item, 'reload_bibles'):

            # WHEN: on_delete_click is called
            self.media_item.on_delete_click()

            # THEN: QMessageBox.question should and delete_bible should not have been called
            assert mocked_qmessage_box.called is True
            assert self.mocked_plugin.manager.delete_bible.called is True

    def test_on_search_tab_bar_current_changed_search_tab_selected(self):
        """
        Test on_search_tab_bar_current_changed when the search_tab is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out search_tab and select_tab
        self.media_item.search_tab = MagicMock()
        self.media_item.select_tab = MagicMock()
        self.media_item.options_tab = MagicMock()
        self.media_item.search_button = MagicMock()
        with patch.object(self.media_item, 'on_focus'):

            # WHEN: The search_tab has been selected
            self.media_item.on_search_tab_bar_current_changed(SearchTabs.Search)

            # THEN: The search_button should be enabled, search_tab should be setVisible and select_tab should be hidden
            self.media_item.search_button.setEnabled.assert_called_once_with(True)
            self.media_item.search_tab.setVisible.assert_called_once_with(True)
            self.media_item.select_tab.setVisible.assert_called_once_with(False)

    def test_on_search_tab_bar_current_changed_select_tab_selected(self):
        """
        Test on_search_tab_bar_current_changed when the select_tab is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out search_tab and select_tab
        self.media_item.search_tab = MagicMock()
        self.media_item.select_tab = MagicMock()
        self.media_item.options_tab = MagicMock()
        self.media_item.search_button = MagicMock()
        with patch.object(self.media_item, 'on_focus'):

            # WHEN: The select_tab has been selected
            self.media_item.on_search_tab_bar_current_changed(SearchTabs.Select)

            # THEN: The search_button should be enabled, select_tab should be setVisible and search_tab should be hidden
            self.media_item.search_button.setEnabled.assert_called_once_with(True)
            self.media_item.search_tab.setVisible.assert_called_once_with(False)
            self.media_item.select_tab.setVisible.assert_called_once_with(True)

    def test_on_book_order_button_toggled_checked(self):
        """
        Test that 'on_book_order_button_toggled' changes the order of the book list
        """
        self.media_item.select_book_combo_box = MagicMock()

        # WHEN: When the book_order_button is checked
        self.media_item.on_book_order_button_toggled(True)

        # THEN: The select_book_combo_box model should have been sorted
        self.media_item.select_book_combo_box.model().sort.assert_called_once_with(0)

    def test_on_book_order_button_toggled_un_checked(self):
        """
        Test that 'on_book_order_button_toggled' changes the order of the book list
        """
        self.media_item.select_book_combo_box = MagicMock()

        # WHEN: When the book_order_button is un-checked
        self.media_item.on_book_order_button_toggled(False)

        # THEN: The select_book_combo_box model sort should have been reset
        self.media_item.select_book_combo_box.model().sort.assert_called_once_with(-1)

    def test_on_clear_button_clicked(self):
        """
        Test on_clear_button_clicked when the search tab is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked out search_tab and select_tab and a mocked out
        #        list_view and search_edit
        self.media_item.list_view = MagicMock(**{'selectedItems.return_value': ['Some', 'Results']})
        self.media_item.results_view_tab = MagicMock(**{'currentIndex.return_value': ResultsTab.Search})
        with patch.object(self.media_item, 'on_results_view_tab_total_update'):

            # WHEN: Calling on_clear_button_clicked
            self.media_item.on_clear_button_clicked()

            # THEN: The list_view and the search_edit should be cleared
            assert self.media_item.current_results == []
            assert self.media_item.list_view.takeItem.call_count == 2
            self.media_item.list_view.row.assert_has_calls([call('Some'), call('Results')])

    def test_on_save_results_button_clicked(self):
        """
        Test that "on_save_results_button_clicked" saves the results.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked list_view
        result_1 = MagicMock(**{'data.return_value': 'R1'})
        result_2 = MagicMock(**{'data.return_value': 'R2'})
        result_3 = MagicMock(**{'data.return_value': 'R3'})
        self.media_item.list_view = MagicMock(**{'selectedItems.return_value': [result_1, result_2, result_3]})

        with patch.object(self.media_item, 'on_results_view_tab_total_update') as \
                mocked_on_results_view_tab_total_update:

            # WHEN: When the save_results_button is clicked
            self.media_item.on_save_results_button_clicked()

            # THEN: The selected results in the list_view should be added to the 'saved_results' list. And the saved_tab
            #       total should be updated.
            assert self.media_item.saved_results == ['R1', 'R2', 'R3']
            mocked_on_results_view_tab_total_update.assert_called_once_with(ResultsTab.Saved)

    def test_on_style_combo_box_changed(self):
        """
        Test on_style_combo_box_index_changed
        """
        # GIVEN: An instance of :class:`MediaManagerItem` a mocked media_item.settings
        self.media_item.settings = MagicMock()

        # WHEN: Calling on_style_combo_box_index_changed
        self.media_item.on_style_combo_box_index_changed(2)

        # THEN: The layout_style setting should have been set
        assert self.media_item.settings.layout_style, 2
        self.media_item.settings.layout_style_combo_box.setCurrentIndex.assert_called_once_with(2)
        self.mocked_settings_instance.setValue.assert_called_once_with('bibles/verse layout style', 2)

    def test_on_version_combo_box_index_changed_no_bible(self):
        """
        Test on_version_combo_box_index_changed when there is no main bible.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked media_item.settings and select_book_combo_box
        self.media_item.version_combo_box = MagicMock(**{'currentData.return_value': None})
        self.media_item.select_book_combo_box = MagicMock()
        with patch.object(self.media_item, 'initialise_advanced_bible') as mocked_initialise_advanced_bible:

            # WHEN: Calling on_version_combo_box_index_changed
            self.media_item.on_version_combo_box_index_changed()

            # THEN: The version should be saved to settings and the 'select tab' should be initialised
            assert self.mocked_settings_instance.setValue.called is False
            assert self.media_item.initialise_advanced_bible.called is True

    def test_on_version_combo_box_index_changed_bible_selected(self):
        """
        Test on_version_combo_box_index_changed when a bible has been selected.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked media_item.settings and select_book_combo_box
        mocked_bible_db = MagicMock()
        mocked_bible_db.name = 'ABC'
        self.media_item.version_combo_box = MagicMock(**{'currentData.return_value': mocked_bible_db})
        self.media_item.select_book_combo_box = MagicMock()
        with patch.object(self.media_item, 'initialise_advanced_bible') as mocked_initialise_advanced_bible:

            # WHEN: Calling on_version_combo_box_index_changed
            self.media_item.on_version_combo_box_index_changed()

            # THEN: The version should be saved to settings and the 'select tab' should be initialised
            self.mocked_settings_instance.setValue.assert_called_once_with('bibles/primary bible', 'ABC')
            assert self.media_item.initialise_advanced_bible.called is True

    def test_on_second_combo_box_index_changed_mode_not_changed(self):
        """
        Test on_second_combo_box_index_changed when the user does not change from dual mode
        results and the user chooses no to the message box
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.list_view = MagicMock(**{'count.return_value': 5})
        self.media_item.style_combo_box = MagicMock()
        self.media_item.select_book_combo_box = MagicMock()
        with patch.object(self.media_item, 'initialise_advanced_bible') as mocked_initialise_advanced_bible, \
                patch('openlp.plugins.bibles.lib.mediaitem.critical_error_message_box') \
                as mocked_critical_error_message_box:

            # WHEN: The previously selected bible is one bible and the new selection is another bible
            self.media_item.second_bible = self.mocked_bible_1
            self.media_item.second_combo_box = MagicMock(**{'currentData.return_value': self.mocked_bible_2})
            self.media_item.on_second_combo_box_index_changed(5)

            # THEN: The new bible should now be the current bible
            assert mocked_critical_error_message_box.called is False
            self.media_item.style_combo_box.setEnabled.assert_called_once_with(False)
            assert self.media_item.second_bible == self.mocked_bible_2

    def test_on_second_combo_box_index_changed_single_to_dual_user_abort(self):
        """
        Test on_second_combo_box_index_changed when the user changes from single to dual bible mode, there are search
        results and the user chooses no to the message box
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.list_view = MagicMock(**{'count.return_value': 5})
        self.media_item.style_combo_box = MagicMock()
        self.media_item.select_book_combo_box = MagicMock()
        with patch.object(self.media_item, 'initialise_advanced_bible') as mocked_initialise_advanced_bible, \
                patch('openlp.plugins.bibles.lib.mediaitem.critical_error_message_box',
                      return_value=QtWidgets.QMessageBox.No) as mocked_critical_error_message_box:

            # WHEN: The previously selected bible is None and the new selection is a bible and the user selects yes
            #       to the dialog box
            self.media_item.second_bible = None
            self.media_item.second_combo_box = MagicMock(**{'currentData.return_value': self.mocked_bible_1})
            self.media_item.saved_results = ['saved_results']
            self.media_item.on_second_combo_box_index_changed(5)

            # THEN: The list_view should be cleared and the currently selected bible should not be changed
            assert mocked_critical_error_message_box.called is True
            assert self.media_item.second_combo_box.setCurrentIndex.called is True
            assert self.media_item.style_combo_box.setEnabled.called is False
            assert self.media_item.second_bible is None

    def test_on_second_combo_box_index_changed_single_to_dual(self):
        """
        Test on_second_combo_box_index_changed when the user changes from single to dual bible mode, there are search
        results and the user chooses yes to the message box
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.list_view = MagicMock(**{'count.return_value': 5})
        self.media_item.style_combo_box = MagicMock()
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.search_results = ['list', 'of', 'results']
        with patch.object(self.media_item, 'initialise_advanced_bible') as mocked_initialise_advanced_bible, \
                patch.object(self.media_item, 'display_results'), \
                patch('openlp.plugins.bibles.lib.mediaitem.critical_error_message_box',
                      return_value=QtWidgets.QMessageBox.Yes) as mocked_critical_error_message_box:

            # WHEN: The previously selected bible is None and the new selection is a bible and the user selects yes
            #       to the dialog box
            self.media_item.second_bible = None
            self.media_item.second_combo_box = MagicMock(**{'currentData.return_value': self.mocked_bible_1})
            self.media_item.saved_results = ['saved_results']
            self.media_item.on_second_combo_box_index_changed(5)

            # THEN: The selected bible should be set as the current bible
            assert mocked_critical_error_message_box.called is True
            self.media_item.style_combo_box.setEnabled.assert_called_once_with(False)
            assert mocked_initialise_advanced_bible.called is True
            assert self.media_item.second_bible == self.mocked_bible_1

    def test_on_second_combo_box_index_changed_dual_to_single(self):
        """
        Test on_second_combo_box_index_changed when the user changes from dual to single bible mode, there are search
        results and the user chooses yes to the message box
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.list_view = MagicMock(**{'count.return_value': 5})
        self.media_item.style_combo_box = MagicMock()
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.search_results = ['list', 'of', 'results']
        with patch.object(self.media_item, 'initialise_advanced_bible') as mocked_initialise_advanced_bible, \
                patch.object(self.media_item, 'display_results'), \
                patch('openlp.plugins.bibles.lib.mediaitem.critical_error_message_box',
                      return_value=QtWidgets.QMessageBox.Yes) as mocked_critical_error_message_box:
            # WHEN: The previously is a bible new selection is None and the user selects yes
            #       to the dialog box
            self.media_item.second_bible = self.mocked_bible_1
            self.media_item.second_combo_box = MagicMock(**{'currentData.return_value': None})
            self.media_item.saved_results = ['saved_results']
            self.media_item.on_second_combo_box_index_changed(0)

            # THEN: The selected bible should be set as the current bible
            assert mocked_critical_error_message_box.called is True
            self.media_item.style_combo_box.setEnabled.assert_called_once_with(True)
            assert mocked_initialise_advanced_bible.called is False
            assert self.media_item.second_bible is None

    def test_on_advanced_book_combo_box(self):
        """
        Test on_advanced_book_combo_box when the book returns 0 for the verse count.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked get_verse_count_by_book_ref_id which returns 0
        self.media_item.select_book_combo_box = MagicMock(**{'currentData.return_value': 2})
        self.media_item.bible = self.mocked_bible_1
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 0
        self.media_item.search_button = MagicMock()
        with patch('openlp.plugins.bibles.lib.mediaitem.critical_error_message_box') \
                as mocked_critical_error_message_box:

            # WHEN: Calling on_advanced_book_combo_box
            self.media_item.on_advanced_book_combo_box()

            # THEN: The user should be informed  that the bible cannot be used and the search button should be disabled
            self.mocked_plugin.manager.get_book_by_id.assert_called_once_with('Bible 1', 2)
            self.media_item.search_button.setEnabled.assert_called_once_with(False)
            assert mocked_critical_error_message_box.called is True

    def test_on_advanced_book_combo_box_set_up_comboboxes(self):
        """
        Test on_advanced_book_combo_box when the book returns 6 for the verse count.
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and a mocked get_verse_count_by_book_ref_id which returns 6
        self.media_item.from_chapter = 0
        self.media_item.to_chapter = 0
        self.media_item.from_verse = 0
        self.media_item.to_verse = 0
        self.media_item.select_book_combo_box = MagicMock(**{'currentData.return_value': 2})
        self.media_item.bible = self.mocked_bible_1
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 6
        self.media_item.select_tab = MagicMock(**{'isVisible.return_value': True})
        self.media_item.search_button = MagicMock()
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:
            # WHEN: Calling on_advanced_book_combo_box
            self.media_item.on_advanced_book_combo_box()

            # THEN: The verse selection combobox's should be set up
            self.mocked_plugin.manager.get_book_by_id.assert_called_once_with('Bible 1', 2)
            self.media_item.search_button.setEnabled.assert_called_once_with(True)
            assert mocked_adjust_combo_box.call_count == 4

    def test_on_from_chapter_activated_invalid_to_chapter(self):
        """
        Test on_from_chapter_activated when the to_chapter is less than the from_chapter
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.chapter_count = 25
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 10})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.from_verse = MagicMock()
        self.media_item.to_verse = MagicMock()
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:

            # WHEN: Calling on_from_chapter_activated
            self.media_item.on_from_chapter_activated()

            # THEN: The to_verse and to_chapter comboboxes should be updated appropriately
            assert mocked_adjust_combo_box.call_args_list == [
                call(1, 20, self.media_item.from_verse), call(1, 20, self.media_item.to_verse, False),
                call(10, 25, self.media_item.to_chapter, False)]

    def test_on_from_chapter_activated_same_chapter(self):
        """
        Test on_from_chapter_activated when the to_chapter is the same as from_chapter
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.chapter_count = 25
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.from_verse = MagicMock()
        self.media_item.to_verse = MagicMock()
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:

            # WHEN: Calling on_from_chapter_activated
            self.media_item.on_from_chapter_activated()

            # THEN: The to_verse and to_chapter comboboxes should be updated appropriately
            assert mocked_adjust_combo_box.call_args_list == [
                call(1, 20, self.media_item.from_verse), call(1, 20, self.media_item.to_verse, True),
                call(5, 25, self.media_item.to_chapter, False)]

    def test_on_from_chapter_activated_lower_chapter(self):
        """
        Test on_from_chapter_activated when the to_chapter is greater than the from_chapter
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.chapter_count = 25
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 7})
        self.media_item.from_verse = MagicMock()
        self.media_item.to_verse = MagicMock()
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:
            # WHEN: Calling on_from_chapter_activated
            self.media_item.on_from_chapter_activated()

            # THEN: The to_verse and to_chapter comboboxes should be updated appropriately
            assert mocked_adjust_combo_box.call_args_list == [
                call(1, 20, self.media_item.from_verse), call(5, 25, self.media_item.to_chapter, True)]

    def test_on_from_verse(self):
        """
        Test on_from_verse when the to_chapter is not equal to the from_chapter
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 2})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})

        # WHEN: Calling on_from_verse
        self.media_item.on_from_verse()

        # THEN: select_book_combo_box.currentData should nto be called
        assert self.media_item.select_book_combo_box.currentData.called is False

    def test_on_from_verse_equal(self):
        """
        Test on_from_verse when the to_chapter is equal to the from_chapter
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.from_verse = MagicMock(**{'currentData.return_value': 7})
        self.media_item.to_verse = MagicMock()
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:

            # WHEN: Calling on_from_verse
            self.media_item.on_from_verse()

            # THEN: The to_verse should have been updated
            mocked_adjust_combo_box.assert_called_once_with(7, 20, self.media_item.to_verse, True)

    def test_on_to_chapter_same_chapter_from_greater_than(self):
        """
        Test on_to_chapter when the to_chapter is equal to the from_chapter and the from_verse is greater than the
        to_verse
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.from_verse = MagicMock(**{'currentData.return_value': 10})
        self.media_item.to_verse = MagicMock(**{'currentData.return_value': 7})
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:

            # WHEN: Calling on_tp_chapter
            self.media_item.on_to_chapter()

            # THEN: The to_verse should have been updated
            mocked_adjust_combo_box.assert_called_once_with(10, 20, self.media_item.to_verse)

    def test_on_from_verse_chapters_not_equal(self):
        """
        Test on_from_verse when the to_chapter is not equal to the from_chapter
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 7})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.from_verse = MagicMock(**{'currentData.return_value': 10})
        self.media_item.to_verse = MagicMock(**{'currentData.return_value': 7})
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:

            # WHEN: Calling on_from_chapter_activated
            self.media_item.on_to_chapter()

            # THEN: The to_verse should have been updated
            mocked_adjust_combo_box.assert_called_once_with(1, 20, self.media_item.to_verse)

    def test_on_from_verse_from_verse_less_than(self):
        """
        Test on_from_verse when the to_chapter is equal to the from_chapter and from_verse is less than to_verse
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, some mocked comboboxes with test data
        self.media_item.bible = self.mocked_bible_1
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.to_chapter = MagicMock(**{'currentData.return_value': 5})
        self.media_item.from_verse = MagicMock(**{'currentData.return_value': 6})
        self.media_item.to_verse = MagicMock(**{'currentData.return_value': 7})
        self.mocked_plugin.manager.get_verse_count_by_book_ref_id.return_value = 20
        with patch.object(self.media_item, 'adjust_combo_box') as mocked_adjust_combo_box:

            # WHEN: Calling on_from_chapter_activated
            self.media_item.on_to_chapter()

            # THEN: The to_verse should have been updated
            mocked_adjust_combo_box.assert_called_once_with(1, 20, self.media_item.to_verse)

    def test_adjust_combo_box_no_restore(self):
        """
        Test adjust_combo_box  when being used with out the restore function
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        mocked_combo_box = MagicMock()

        # WHEN: Calling adjust_combo_box with out setting the kwarg `restore`
        self.media_item.adjust_combo_box(10, 13, mocked_combo_box)

        # THEN: The combo_box should be cleared, and new items added
        mocked_combo_box.clear.assert_called_once_with()
        assert mocked_combo_box.addItem.call_args_list == \
            [call('10', 10), call('11', 11), call('12', 12), call('13', 13)]

    def test_adjust_combo_box_restore_found(self):
        """
        Test adjust_combo_box  when being used with out the restore function
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, with the 2nd item '12' selected
        mocked_combo_box = MagicMock(**{'currentData.return_value': 12, 'findData.return_value': 2})

        # WHEN: Calling adjust_combo_box with the kwarg `restore` set to True
        self.media_item.adjust_combo_box(10, 13, mocked_combo_box, True)

        # THEN: The combo_box should be cleared, and new items added. Finally the previously selected item should be
        #       reselected
        mocked_combo_box.clear.assert_called_once_with()
        assert mocked_combo_box.addItem.call_args_list == \
               [call('10', 10), call('11', 11), call('12', 12), call('13', 13)]
        mocked_combo_box.setCurrentIndex.assert_called_once_with(2)

    def test_adjust_combo_box_restore_not_found(self):
        """
        Test adjust_combo_box  when being used with out the restore function when the selected item is not available
        after the combobox has been updated
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, with the 2nd item '12' selected
        mocked_combo_box = MagicMock(**{'currentData.return_value': 9, 'findData.return_value': -1})

        # WHEN: Calling adjust_combo_box with the kwarg `restore` set to True
        self.media_item.adjust_combo_box(10, 13, mocked_combo_box, True)

        # THEN: The combo_box should be cleared, and new items added. Finally the first item should be selected
        mocked_combo_box.clear.assert_called_once_with()
        assert mocked_combo_box.addItem.call_args_list == \
            [call('10', 10), call('11', 11), call('12', 12), call('13', 13)]
        mocked_combo_box.setCurrentIndex.assert_called_once_with(0)

    def test_on_search_button_no_bible(self):
        """
        Test on_search_button_clicked when there is no bible selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        # WHEN calling on_search_button_clicked and there is no selected bible
        self.media_item.bible = None
        self.media_item.on_search_button_clicked()

        # THEN: The user should be informed that there are no bibles selected
        assert self.mocked_main_window.information_message.call_count == 1

    def test_on_search_button_search_tab(self):
        """
        Test on_search_button_clicked when the `Search` tab is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, and a mocked text_search method
        self.media_item.bible = self.mocked_bible_1
        self.media_item.search_button = MagicMock()
        self.media_item.search_tab = MagicMock(**{'isVisible.return_value': True})
        with patch.object(self.media_item, 'text_search') as mocked_text_search:

            # WHEN: Calling on_search_button_clicked and the 'Search' tab is selected
            self.media_item.on_search_button_clicked()

            # THEN: The text_search method should have been called
            mocked_text_search.assert_called_once_with()

    def test_on_search_button_select_tab(self):
        """
        Test on_search_button_clicked when the `Select` tab is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem`, and a mocked select_search method
        self.media_item.bible = self.mocked_bible_1
        self.media_item.search_button = MagicMock()
        self.media_item.search_tab = MagicMock(**{'isVisible.return_value': False})
        self.media_item.select_tab = MagicMock(**{'isVisible.return_value': True})
        with patch.object(self.media_item, 'select_search') as mocked_select_search:

            # WHEN: Calling on_search_button_clicked and the 'Select' tab is selected
            self.media_item.on_search_button_clicked()

            # THEN: The text_search method should have been called
            mocked_select_search.assert_called_once_with()

    def test_select_search_single_bible(self):
        """
        Test select_search when only one bible is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked plugin.manager.get_verses
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock()
        self.media_item.from_verse = MagicMock()
        self.media_item.to_chapter = MagicMock()
        self.media_item.to_verse = MagicMock()
        with patch.object(self.media_item, 'display_results') as mocked_display_results:

            # WHEN: Calling select_search and there is only one bible selected
            self.media_item.bible = self.mocked_bible_1
            self.media_item.second_bible = None
            self.media_item.select_search()

            # THEN: reference_search should only be called once
            assert self.mocked_plugin.manager.get_verses.call_count == 1
            mocked_display_results.assert_called_once_with()

    def test_select_search_dual_bibles(self):
        """
        Test select_search when two bibles are selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked_reference_search
        self.media_item.select_book_combo_box = MagicMock()
        self.media_item.from_chapter = MagicMock()
        self.media_item.from_verse = MagicMock()
        self.media_item.to_chapter = MagicMock()
        self.media_item.to_verse = MagicMock()
        with patch.object(self.media_item, 'display_results') as mocked_display_results:

            # WHEN: Calling select_search and there are two bibles selected
            self.media_item.bible = self.mocked_bible_1
            self.media_item.second_bible = self.mocked_bible_2
            self.media_item.select_search()

            # THEN: reference_search should be called twice
            assert self.mocked_plugin.manager.get_verses.call_count == 2
            mocked_display_results.assert_called_once_with()

    def test_text_reference_search_single_bible(self):
        """
        Test text_reference_search when only one bible is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked plugin.manager.get_verses
        with patch.object(self.media_item, 'display_results') as mocked_display_results:

            # WHEN: Calling text_reference_search with only one bible selected
            self.media_item.bible = self.mocked_bible_1
            self.media_item.second_bible = None
            self.media_item.text_reference_search('Search Text')

            # THEN: reference_search should only be called once
            assert self.mocked_plugin.manager.get_verses.call_count == 1
            mocked_display_results.assert_called_once_with()

            def text_reference_search(self, search_text, search_while_type=False):
                """
                We are doing a 'Reference Search'.
                This search is called on def text_search by Reference and Combined Searches.
                """
                verse_refs = self.plugin.manager.parse_ref(self.bible.name, search_text)
                self.search_results = self.reference_search(verse_refs, self.bible)
                if self.second_bible and self.search_results:
                    self.second_search_results = self.reference_search(verse_refs, self.second_bible)
                self.display_results()

    def test_text_reference_search_dual_bible_no_results(self):
        """
        Test text_reference_search when two bible are selected, but the search of the first bible does not return any
        results
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked plugin.manager.get_verses
        # WHEN: Calling text_reference_search with two bibles selected, but no results are found in the first bible
        with patch.object(self.media_item, 'display_results') as mocked_display_results:
            self.mocked_plugin.manager.get_verses.return_value = []
            self.media_item.bible = self.mocked_bible_1
            self.media_item.second_bible = self.mocked_bible_2
            self.media_item.text_reference_search('Search Text')

            # THEN: reference_search should only be called once
            assert self.mocked_plugin.manager.get_verses.call_count == 1
            mocked_display_results.assert_called_once_with()

    def test_text_reference_search_dual_bible(self):
        """
        Test text_reference_search when two bible are selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and mocked plugin.manager.get_verses
        with patch.object(self.media_item, 'display_results') as mocked_display_results:
            self.media_item.bible = self.mocked_bible_1
            self.media_item.second_bible = self.mocked_bible_2

            # WHEN: Calling text_reference_search with two bibles selected
            self.media_item.text_reference_search('Search Text')

            # THEN: reference_search should be called twice
            assert self.mocked_plugin.manager.get_verses.call_count == 2
            mocked_display_results.assert_called_once_with()

    def test_on_text_search_single_bible(self):
        """
        Test on_text_search when only one bible is selected
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.bible = self.mocked_bible_1
        self.media_item.second_bible = None

        # WHEN: Calling on_text_search and plugin.manager.verse_search returns a list of results
        self.mocked_plugin.manager.verse_search.return_value = ['results', 'list']
        with patch.object(self.media_item, 'display_results') as mocked_display_results:
            self.media_item.on_text_search('Search Text')

            # THEN: The search results should be the same as those returned by plugin.manager.verse_search
            assert self.media_item.search_results == ['results', 'list']
            mocked_display_results.assert_called_once_with()

    def test_on_text_search_no_results(self):
        """
        Test on_text_search when the search of the first bible does not return any results
        """
        # GIVEN: An instance of :class:`MediaManagerItem`
        self.media_item.bible = self.mocked_bible_1
        self.media_item.second_bible = self.mocked_bible_2

        # WHEN: Calling on_text_search and plugin.manager.verse_search returns an empty list
        self.mocked_plugin.manager.verse_search.return_value = []
        with patch.object(self.media_item, 'display_results') as mocked_display_results:
            self.media_item.on_text_search('Search Text')

            # THEN: The search results should be an empty list
            assert self.media_item.search_results == []
            mocked_display_results.assert_called_once_with()

    def test_on_text_search_all_results_in_both_books(self):
        """
        Test on_text_search when all of the results from the first bible are found in the second
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and some test data
        mocked_verse_1 = MagicMock(**{'book.book_reference_id': 1, 'chapter': 2, 'verse': 3})
        mocked_verse_1a = MagicMock(**{'book.book_reference_id': 1, 'chapter': 2, 'verse': 3})
        mocked_verse_2 = MagicMock(**{'book.book_reference_id': 4, 'chapter': 5, 'verse': 6})
        mocked_verse_2a = MagicMock(**{'book.book_reference_id': 4, 'chapter': 5, 'verse': 6})
        self.media_item.bible = self.mocked_bible_1
        self.media_item.second_bible = self.mocked_bible_2
        self.media_item.second_search_results = []

        # WHEN: Calling on_text_search and plugin.manager.verse_search returns a list of search results
        self.mocked_plugin.manager.verse_search.return_value = [mocked_verse_1, mocked_verse_2]
        self.media_item.second_bible.get_verses.side_effect = [[mocked_verse_1a], [mocked_verse_2a]]
        with patch.object(self.media_item, 'display_results') as mocked_display_results:
            self.media_item.on_text_search('Search Text')

            # THEN: The search results for both bibles should be returned
            assert self.media_item.search_results == [mocked_verse_1, mocked_verse_2]
            assert self.media_item.second_search_results == [mocked_verse_1a, mocked_verse_2a]
            assert self.mocked_log.debug.called is False
            assert self.mocked_main_window.information_message.called is False
            mocked_display_results.assert_called_once_with()

    def test_on_text_search_not_all_results_in_both_books(self):
        """
        Test on_text_search when not all of the results from the first bible are found in the second
        """
        # GIVEN: An instance of :class:`MediaManagerItem` and some test data
        mocked_verse_1 = MagicMock(**{'book.book_reference_id': 1, 'chapter': 2, 'verse': 3})
        mocked_verse_1a = MagicMock(**{'book.book_reference_id': 1, 'chapter': 2, 'verse': 3})
        mocked_verse_2 = MagicMock(**{'book.book_reference_id': 4, 'chapter': 5, 'verse': 6})
        mocked_verse_3 = MagicMock(**{'book.book_reference_id': 7, 'chapter': 8, 'verse': 9})
        self.media_item.bible = self.mocked_bible_1
        self.media_item.second_bible = self.mocked_bible_2
        self.media_item.second_search_results = []

        # WHEN: Calling on_text_search and not all results are found in the second bible
        self.mocked_plugin.manager.verse_search.return_value = [mocked_verse_1, mocked_verse_2, mocked_verse_3]
        self.media_item.second_bible.get_verses.side_effect = [[mocked_verse_1a], [], []]
        with patch.object(self.media_item, 'display_results') as mocked_display_results:
            self.media_item.on_text_search('Search Text')

            # THEN: The search results included in  both bibles should be returned and the user should be notified of
            #       the missing verses
            assert self.media_item.search_results == [mocked_verse_1]
            assert self.media_item.second_search_results == [mocked_verse_1a]
            assert self.mocked_log.debug.call_count == 2
            assert self.mocked_main_window.information_message.called is True
            mocked_display_results.assert_called_once_with()

    def test_on_search_edit_text_changed_search_while_typing_disabled(self):
        """
        Test on_search_edit_text_changed when 'search while typing' is disabled
        """
        # GIVEN: An instance of BibleMediaItem and mocked Settings which returns False when the value
        #       'bibles/is search while typing enabled' is requested
        self.setting_values = {'bibles/is search while typing enabled': False}
        self.mocked_qtimer.isActive.return_value = False

        # WHEN: Calling on_search_edit_text_changed
        self.media_item.on_search_edit_text_changed()

        # THEN: The method should not have checked if the timer is active
        assert self.media_item.search_timer.isActive.called is False

    def test_on_search_edit_text_changed_search_while_typing_enabled(self):
        """
        Test on_search_edit_text_changed when 'search while typing' is enabled
        """
        # GIVEN: An instance of BibleMediaItem and mocked Settings which returns True when the value
        #       'bibles/is search while typing enabled' is requested
        self.setting_values = {'bibles/is search while typing enabled': True}
        self.media_item.search_timer.isActive.return_value = False
        self.media_item.bible = self.mocked_bible_1
        self.media_item.bible.is_web_bible = False

        # WHEN: Calling on_search_edit_text_changed
        self.media_item.on_search_edit_text_changed()

        # THEN: The method should start the search_timer
        self.media_item.search_timer.isActive.assert_called_once_with()
        self.media_item.search_timer.start.assert_called_once_with()

    def test_on_search_timer_timeout(self):
        """
        Test on_search_timer_timeout
        """
        # GIVEN: An instance of BibleMediaItem
        with patch.object(self.media_item, 'text_search') as mocked_text_search:

            # WHEN: Calling on_search_timer_timeout
            self.media_item.on_search_timer_timeout()

            # THEN: The search_status should be set to SearchAsYouType and text_search should have been called
            assert self.media_item.search_status == SearchStatus.SearchAsYouType
            mocked_text_search.assert_called_once_with()

    def test_display_results_no_results(self):
        """
        Test the display_results method when there are no items to display
        """
        # GIVEN: An instance of BibleMediaItem and a mocked build_display_results which returns an empty list
        self.media_item.list_view = MagicMock()
        self.media_item.bible = self.mocked_bible_1
        self.media_item.second_bible = self.mocked_bible_2
        self.media_item.search_results = []

        with patch.object(self.media_item, 'build_display_results', return_value=[]):

            # WHEN: Calling display_results with True
            self.media_item.display_results()

            # THEN: No items should be added to the list
            assert self.media_item.list_view.addItem.called is False

    def test_display_results_results(self):
        """
        Test the display_results method when there are items to display
        """
        # GIVEN: An instance of BibleMediaItem and a mocked build_display_results which returns a list of results
        with patch.object(self.media_item, 'build_display_results', return_value=[
            {'item_title': 'Title 1'}, {'item_title': 'Title 2'}]), \
            patch.object(self.media_item, 'add_built_results_to_list_widget') as \
                mocked_add_built_results_to_list_widget:
            self.media_item.search_results = ['results']
            self.media_item.list_view = MagicMock()

            # WHEN: Calling display_results
            self.media_item.display_results()

            # THEN: addItem should have been with the display items
            mocked_add_built_results_to_list_widget.assert_called_once_with(
                [{'item_title': 'Title 1'}, {'item_title': 'Title 2'}])
