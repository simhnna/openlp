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
from unittest.mock import patch, MagicMock, call

from openlp.core.common.registry import Registry
from openlp.core.common.path import Path
from openlp.plugins.presentations.lib.mediaitem import PresentationMediaItem

from tests.helpers.testmixin import TestMixin


class TestMediaItem(TestCase, TestMixin):
    """
    Test the mediaitem methods.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        Registry.create()
        Registry().register('service_manager', MagicMock())
        Registry().register('main_window', MagicMock())
        with patch('openlp.plugins.presentations.lib.mediaitem.MediaManagerItem._setup'), \
                patch('openlp.plugins.presentations.lib.mediaitem.PresentationMediaItem.setup_item'):
            self.media_item = PresentationMediaItem(None, MagicMock, MagicMock())
        self.setup_application()

    def test_build_file_mask_string(self):
        """
        Test the build_file_mask_string() method
        """
        # GIVEN: Different controllers.
        impress_controller = MagicMock()
        impress_controller.enabled.return_value = True
        impress_controller.supports = ['odp']
        impress_controller.also_supports = ['ppt']
        presentation_controller = MagicMock()
        presentation_controller.enabled.return_value = True
        presentation_controller.supports = ['ppt']
        presentation_controller.also_supports = []
        presentation_viewer_controller = MagicMock()
        presentation_viewer_controller.enabled.return_value = False
        pdf_controller = MagicMock()
        pdf_controller.enabled.return_value = True
        pdf_controller.supports = ['pdf']
        pdf_controller.also_supports = ['xps', 'oxps']
        # Mock the controllers.
        self.media_item.controllers = {
            'Impress': impress_controller,
            'Powerpoint': presentation_controller,
            'Powerpoint Viewer': presentation_viewer_controller,
            'Pdf': pdf_controller
        }

        # WHEN: Build the file mask.
        with patch('openlp.plugins.presentations.lib.mediaitem.translate') as mocked_translate:
            mocked_translate.side_effect = lambda module, string_to_translate: string_to_translate
            self.media_item.build_file_mask_string()

        # THEN: The file mask should be generated correctly
        assertIn('*.odp', self.media_item.on_new_file_masks, 'The file mask should contain the odp extension')
        assertIn('*.ppt', self.media_item.on_new_file_masks, 'The file mask should contain the ppt extension')
        assertIn('*.pdf', self.media_item.on_new_file_masks, 'The file mask should contain the pdf extension')
        assertIn('*.xps', self.media_item.on_new_file_masks, 'The file mask should contain the xps extension')
        assertIn('*.oxps', self.media_item.on_new_file_masks, 'The file mask should contain the oxps extension')

    def test_clean_up_thumbnails(self):
        """
        Test that the clean_up_thumbnails method works as expected when files exists.
        """
        # GIVEN: A mocked controller, and mocked os.path.getmtime
        mocked_controller = MagicMock()
        mocked_doc = MagicMock(**{'get_thumbnail_path.return_value': Path()})
        mocked_controller.add_document.return_value = mocked_doc
        mocked_controller.supports = ['tmp']
        self.media_item.controllers = {
            'Mocked': mocked_controller
        }

        thmub_path = MagicMock(st_mtime=100)
        file_path = MagicMock(st_mtime=400)
        with patch.object(Path, 'stat', side_effect=[thmub_path, file_path]), \
                patch.object(Path, 'exists', return_value=True):
            presentation_file = Path('file.tmp')

            # WHEN: calling clean_up_thumbnails
            self.media_item.clean_up_thumbnails(presentation_file, True)

        # THEN: doc.presentation_deleted should have been called since the thumbnails mtime will be greater than
        #       the presentation_file's mtime.
        mocked_doc.assert_has_calls([call.get_thumbnail_path(1, True), call.presentation_deleted()], True)

    def test_clean_up_thumbnails_missing_file(self):
        """
        Test that the clean_up_thumbnails method works as expected when file is missing.
        """
        # GIVEN: A mocked controller, and mocked os.path.exists
        mocked_controller = MagicMock()
        mocked_doc = MagicMock()
        mocked_controller.add_document.return_value = mocked_doc
        mocked_controller.supports = ['tmp']
        self.media_item.controllers = {
            'Mocked': mocked_controller
        }
        presentation_file = Path('file.tmp')
        with patch.object(Path, 'exists', return_value=False):

            # WHEN: calling clean_up_thumbnails
            self.media_item.clean_up_thumbnails(presentation_file, True)

        # THEN: doc.presentation_deleted should have been called since the presentation file did not exists.
        mocked_doc.assert_has_calls([call.get_thumbnail_path(1, True), call.presentation_deleted()], True)

    @patch('openlp.plugins.presentations.lib.mediaitem.MediaManagerItem._setup')
    @patch('openlp.plugins.presentations.lib.mediaitem.PresentationMediaItem.setup_item')
    @patch('openlp.plugins.presentations.lib.mediaitem.Settings')
    def test_search(self, mocked_settings, *unreferenced_mocks):
        """
        Test that the search method finds the correct results
        """
        # GIVEN: A mocked Settings class which returns a list of Path objects,
        #        and an instance of the PresentationMediaItem
        path_1 = Path('some_dir', 'Impress_file_1')
        path_2 = Path('some_other_dir', 'impress_file_2')
        path_3 = Path('another_dir', 'ppt_file')
        mocked_returned_settings = MagicMock()
        mocked_returned_settings.value.return_value = [path_1, path_2, path_3]
        mocked_settings.return_value = mocked_returned_settings
        media_item = PresentationMediaItem(None, MagicMock(), None)
        media_item.settings_section = ''

        # WHEN: Calling search
        results = media_item.search('IMPRE', False)

        # THEN: The first two results should have been returned
        assert results == [[str(path_1), 'Impress_file_1'], [str(path_2), 'impress_file_2']]
