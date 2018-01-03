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
Functional tests to test the PresentationController and PresentationDocument
classes and related methods.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from openlp.core.common.path import Path
from openlp.plugins.presentations.lib.presentationcontroller import PresentationController, PresentationDocument

FOLDER_TO_PATCH = 'openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder'


class TestPresentationController(TestCase):
    """
    Test the PresentationController.
    """
    def setUp(self):
        self.get_thumbnail_folder_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder',
                  return_value=Path())
        self.get_thumbnail_folder_patcher.start()
        mocked_plugin = MagicMock()
        mocked_plugin.settings_section = 'presentations'
        self.presentation = PresentationController(mocked_plugin)
        self.document = PresentationDocument(self.presentation, '')

    def tearDown(self):
        self.get_thumbnail_folder_patcher.stop()

    def test_constructor(self):
        """
        Test the Constructor
        """
        # GIVEN: A mocked plugin

        # WHEN: The PresentationController is created

        # THEN: The name of the presentation controller should be correct
        assert 'PresentationController' == self.presentation.name, \
            'The name of the presentation controller should be correct'

    def test_save_titles_and_notes(self):
        """
        Test PresentationDocument.save_titles_and_notes method with two valid lists
        """
        # GIVEN: two lists of length==2 and a mocked open and get_thumbnail_folder
        with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.write_text') as mocked_write_text, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
            titles = ['uno', 'dos']
            notes = ['one', 'two']

            # WHEN: calling save_titles_and_notes
            mocked_get_thumbnail_folder.return_value = Path('test')
            self.document.save_titles_and_notes(titles, notes)

            # THEN: the last call to open should have been for slideNotes2.txt
            assert mocked_write_text.call_count == 3, 'There should be exactly three files written'
            mocked_write_text.assert_has_calls([call('uno\ndos'), call('one'), call('two')])

    def test_save_titles_and_notes_with_None(self):
        """
        Test PresentationDocument.save_titles_and_notes method with no data
        """
        # GIVEN: None and an empty list and a mocked open and get_thumbnail_folder
        with patch('builtins.open') as mocked_open, patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
            titles = None
            notes = None

            # WHEN: calling save_titles_and_notes
            mocked_get_thumbnail_folder.return_value = 'test'
            self.document.save_titles_and_notes(titles, notes)

            # THEN: No file should have been created
            assert mocked_open.call_count == 0, 'No file should be created'

    def test_get_titles_and_notes(self):
        """
        Test PresentationDocument.get_titles_and_notes method
        """
        # GIVEN: A mocked open, get_thumbnail_folder and exists

        with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.read_text',
                   return_value='uno\ndos\n') as mocked_read_text, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder, \
                patch('openlp.plugins.presentations.lib.presentationcontroller.Path.exists') as mocked_exists:
            mocked_get_thumbnail_folder.return_value = Path('test')
            mocked_exists.return_value = True

            # WHEN: calling get_titles_and_notes
            result_titles, result_notes = self.document.get_titles_and_notes()

            # THEN: it should return two items for the titles and two empty strings for the notes
            assert type(result_titles) is list, 'result_titles should be of type list'
            assert len(result_titles) == 2, 'There should be two items in the titles'
            assert type(result_notes) is list, 'result_notes should be of type list'
            assert len(result_notes) == 2, 'There should be two items in the notes'
            assert mocked_read_text.call_count == 3, 'Three files should be read'

    def test_get_titles_and_notes_with_file_not_found(self):
        """
        Test PresentationDocument.get_titles_and_notes method with file not found
        """
        # GIVEN: A mocked open, get_thumbnail_folder and exists
        with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.read_text') as mocked_read_text, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
            mocked_read_text.side_effect = FileNotFoundError()
            mocked_get_thumbnail_folder.return_value = Path('test')

            # WHEN: calling get_titles_and_notes
            result_titles, result_notes = self.document.get_titles_and_notes()

            # THEN: it should return two empty lists
            assert isinstance(result_titles, list), 'result_titles should be of type list'
            assert len(result_titles) == 0, 'there be no titles'
            assert isinstance(result_notes, list), 'result_notes should be a list'
            assert len(result_notes) == 0, 'but the list should be empty'

    def test_get_titles_and_notes_with_file_error(self):
        """
        Test PresentationDocument.get_titles_and_notes method with file errors
        """
        # GIVEN: A mocked open, get_thumbnail_folder and exists
        with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.read_text') as mocked_read_text, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
            mocked_read_text.side_effect = OSError()
            mocked_get_thumbnail_folder.return_value = Path('test')

            # WHEN: calling get_titles_and_notes
            result_titles, result_notes = self.document.get_titles_and_notes()

            # THEN: it should return two empty lists
            assert type(result_titles) is list, 'result_titles should be a list'


class TestPresentationDocument(TestCase):
    """
    Test the PresentationDocument Class
    """
    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.create_paths_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.create_paths')
        self.get_thumbnail_folder_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder')
        self._setup_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument._setup')

        self.mock_create_paths = self.create_paths_patcher.start()
        self.mock_get_thumbnail_folder = self.get_thumbnail_folder_patcher.start()
        self.mock_setup = self._setup_patcher.start()

        self.mock_controller = MagicMock()

        self.mock_get_thumbnail_folder.return_value = Path('returned/path/')

    def tearDown(self):
        """
        Stop the patches
        """
        self.create_paths_patcher.stop()
        self.get_thumbnail_folder_patcher.stop()
        self._setup_patcher.stop()

    def test_initialise_presentation_document(self):
        """
        Test the PresentationDocument __init__ method when initialising the PresentationDocument Class
        """
        # GIVEN: A mocked setup method and mocked controller
        self.mock_setup.reset()

        # WHEN: Creating an instance of PresentationDocument
        PresentationDocument(self.mock_controller, 'Name')

        # THEN: PresentationDocument._setup should have been called with the argument 'Name'
        self.mock_setup.assert_called_once_with('Name')

    def test_presentation_document_setup(self):
        """
        Test the PresentationDocument _setup method when initialising the PresentationDocument Class
        """
        self._setup_patcher.stop()

        # GIVEN: A mocked controller, patched create_paths and get_thumbnail_folder methods

        # WHEN: Creating an instance of PresentationDocument
        PresentationDocument(self.mock_controller, 'Name')

        # THEN: create_paths should have been called with 'returned/path/'
        self.mock_create_paths.assert_called_once_with(Path('returned', 'path/'))

        self._setup_patcher.start()

    def test_load_presentation(self):
        """
        Test the PresentationDocument.load_presentation method.
        """

        # GIVEN: An instance of PresentationDocument
        instance = PresentationDocument(self.mock_controller, 'Name')

        # WHEN: Calling load_presentation()
        result = instance.load_presentation()

        # THEN: load_presentation should return false
        assert result is False, "PresentationDocument.load_presentation should return false."
