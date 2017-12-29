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
Functional tests to test the Impress class and related methods.
"""
import shutil
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.path import Path
from openlp.core.common.settings import Settings
from openlp.plugins.presentations.lib.impresscontroller import ImpressController, ImpressDocument, TextType
from openlp.plugins.presentations.presentationplugin import __default_settings__

from tests.utils.constants import RESOURCE_PATH
from tests.helpers.testmixin import TestMixin


class TestImpressController(TestCase, TestMixin):
    """
    Test the ImpressController Class
    """

    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.setup_application()
        self.build_settings()
        self.mock_plugin = MagicMock()
        self.temp_folder = mkdtemp()
        self.mock_plugin.settings_section = self.temp_folder

    def tearDown(self):
        """
        Stop the patches
        """
        self.destroy_settings()
        shutil.rmtree(self.temp_folder)

    def test_constructor(self):
        """
        Test the Constructor from the ImpressController
        """
        # GIVEN: No presentation controller
        controller = None

        # WHEN: The presentation controller object is created
        controller = ImpressController(plugin=self.mock_plugin)

        # THEN: The name of the presentation controller should be correct
        assert 'Impress' == controller.name, 'The name of the presentation controller should be correct'

    @patch('openlp.plugins.presentations.lib.impresscontroller.log')
    def test_check_available(self, mocked_log):
        """
        Test `ImpressController.check_available` on Windows
        """
        # GIVEN: An instance of :class:`ImpressController`
        controller = ImpressController(plugin=self.mock_plugin)

        # WHEN: `check_available` is called on Windows and `get_com_servicemanager` returns None
        with patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=True), \
                patch.object(controller, 'get_com_servicemanager', return_value=None) as mocked_get_com_servicemanager:
            result = controller.check_available()

            # THEN: `check_available` should return False
            assert mocked_get_com_servicemanager.called is True
            assert result is False

    @patch('openlp.plugins.presentations.lib.impresscontroller.log')
    def test_check_available1(self, mocked_log):
        """
        Test `ImpressController.check_available` on Windows
        """
        # GIVEN: An instance of :class:`ImpressController`
        controller = ImpressController(plugin=self.mock_plugin)

        # WHEN: `check_available` is called on Windows and `get_com_servicemanager` returns an object
        mocked_com_object = MagicMock()
        with patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=True), \
                patch.object(controller, 'get_com_servicemanager', return_value=mocked_com_object) \
                as mocked_get_com_servicemanager:
            result = controller.check_available()

            # THEN: `check_available` should return True
            assert mocked_get_com_servicemanager.called is True
            assert result is True

    @patch('openlp.plugins.presentations.lib.impresscontroller.log')
    @patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=False)
    def test_check_available2(self, mocked_is_win, mocked_log):
        """
        Test `ImpressController.check_available` when not on Windows
        """
        # GIVEN: An instance of :class:`ImpressController`
        controller = ImpressController(plugin=self.mock_plugin)

        # WHEN: `check_available` is called on Windows and `uno_available` is True
        with patch('openlp.plugins.presentations.lib.impresscontroller.uno_available', True), \
                patch.object(controller, 'get_com_servicemanager') as mocked_get_com_servicemanager:
            result = controller.check_available()

            # THEN: `check_available` should return True
            assert mocked_get_com_servicemanager.called is False
            assert result is True


class TestImpressDocument(TestCase):
    """
    Test the ImpressDocument Class
    """
    def setUp(self):
        mocked_plugin = MagicMock()
        mocked_plugin.settings_section = 'presentations'
        Settings().extend_default_settings(__default_settings__)
        self.file_name = RESOURCE_PATH / 'presentations' / 'test.pptx'
        self.ppc = ImpressController(mocked_plugin)
        self.doc = ImpressDocument(self.ppc, self.file_name)

    def test_create_titles_and_notes(self):
        """
        Test ImpressDocument.create_titles_and_notes
        """
        # GIVEN: mocked PresentationController.save_titles_and_notes with
        # 0 pages and the LibreOffice Document
        self.doc.save_titles_and_notes = MagicMock()
        self.doc.document = MagicMock()
        self.doc.document.getDrawPages.return_value = MagicMock()
        self.doc.document.getDrawPages().getCount.return_value = 0

        # WHEN reading the titles and notes
        self.doc.create_titles_and_notes()

        # THEN save_titles_and_notes should have been called with empty arrays
        self.doc.save_titles_and_notes.assert_called_once_with([], [])

        # GIVEN: reset mock and set it to 2 pages
        self.doc.save_titles_and_notes.reset_mock()
        self.doc.document.getDrawPages().getCount.return_value = 2

        # WHEN: a new call to create_titles_and_notes
        self.doc.create_titles_and_notes()

        # THEN: save_titles_and_notes should have been called once with
        # two arrays of two elements
        self.doc.save_titles_and_notes.assert_called_once_with(['\n', '\n'], [' ', ' '])

    def test_get_text_from_page_out_of_bound(self):
        """
        Test ImpressDocument.__get_text_from_page with out-of-bounds index
        """
        # GIVEN: mocked LibreOffice Document with one slide,
        # two notes and three texts
        self.doc.document = self._mock_a_LibreOffice_document(1, 2, 3)

        # WHEN: __get_text_from_page is called with an index of 0x00
        result = self.doc._ImpressDocument__get_text_from_page(0, TextType.Notes)

        # THEN: the result should be an empty string
        assert result == '', 'Result should be an empty string'

        # WHEN: regardless of the type of text, index 0x00 is out of bounds
        result = self.doc._ImpressDocument__get_text_from_page(0, TextType.Title)

        # THEN: result should be an empty string
        assert result == '', 'Result should be an empty string'

        # WHEN: when called with 2, it should also be out of bounds
        result = self.doc._ImpressDocument__get_text_from_page(2, TextType.SlideText)

        # THEN: result should be an empty string ... and, getByIndex should
        # have never been called
        assert result == '', 'Result should be an empty string'
        assert self.doc.document.getDrawPages().getByIndex.call_count == 0, 'There should be no call to getByIndex'

    def test_get_text_from_page_wrong_type(self):
        """
        Test ImpressDocument.__get_text_from_page with wrong TextType
        """
        # GIVEN: mocked LibreOffice Document with one slide, two notes and
        # three texts
        self.doc.document = self._mock_a_LibreOffice_document(1, 2, 3)

        # WHEN: called with TextType 3
        result = self.doc._ImpressDocument__get_text_from_page(1, 3)

        # THEN: result should be an empty string
        assert result == '', 'Result should be and empty string'
        assert self.doc.document.getDrawPages().getByIndex.call_count == 0, 'There should be no call to getByIndex'

    def test_get_text_from_page_valid_params(self):
        """
        Test ImpressDocument.__get_text_from_page with valid parameters
        """
        # GIVEN: mocked LibreOffice Document with one slide,
        # two notes and three texts
        self.doc.document = self._mock_a_LibreOffice_document(1, 2, 3)

        # WHEN: __get_text_from_page is called to get the Notes
        result = self.doc._ImpressDocument__get_text_from_page(1, TextType.Notes)

        # THEN: result should be 'Note\nNote\n'
        assert result == 'Note\nNote\n', 'Result should be \'Note\\n\' times the count of notes in the page'

        # WHEN: get the Title
        result = self.doc._ImpressDocument__get_text_from_page(1, TextType.Title)

        # THEN: result should be 'Title\n'
        assert result == 'Title\n', 'Result should be exactly \'Title\\n\''

        # WHEN: get all text
        result = self.doc._ImpressDocument__get_text_from_page(1, TextType.SlideText)

        # THEN: result should be 'Title\nString\nString\n'
        assert result == 'Title\nString\nString\n', 'Result should be exactly \'Title\\nString\\nString\\n\''

    def _mock_a_LibreOffice_document(self, page_count, note_count, text_count):
        """
        Helper function, creates a mock libreoffice document.

        :param page_count: Number of pages in the document
        :param note_count: Number of note pages in the document
        :param text_count: Number of text pages in the document
        """
        pages = MagicMock()
        page = MagicMock()
        pages.getByIndex.return_value = page
        notes_page = MagicMock()
        notes_page.getCount.return_value = note_count
        shape = MagicMock()
        shape.supportsService.return_value = True
        shape.getString.return_value = 'Note'
        notes_page.getByIndex.return_value = shape
        page.getNotesPage.return_value = notes_page
        page.getCount.return_value = text_count
        page.getByIndex.side_effect = self._get_page_shape_side_effect
        pages.getCount.return_value = page_count
        document = MagicMock()
        document.getDrawPages.return_value = pages
        document.getByIndex.return_value = page
        return document

    def _get_page_shape_side_effect(*args):
        """
        Helper function.
        """
        page_shape = MagicMock()
        page_shape.supportsService.return_value = True
        if args[1] == 0:
            page_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
            page_shape.getString.return_value = 'Title'
        else:
            page_shape.getString.return_value = 'String'
        return page_shape
