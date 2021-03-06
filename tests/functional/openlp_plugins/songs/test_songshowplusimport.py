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
This module contains tests for the SongShow Plus song importer.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.importers.songshowplus import SongShowPlusImport
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'songshowplus'


class TestSongShowPlusFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'SongShowPlusImport'
        self.importer_module_name = 'songshowplus'
        super(TestSongShowPlusFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading a SongShow Plus file works correctly on various files
        """
        self.file_import([TEST_PATH / 'Amazing Grace.sbsong'],
                         self.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
        self.file_import([TEST_PATH / 'Beautiful Garden Of Prayer.sbsong'],
                         self.load_external_result_data(TEST_PATH / 'Beautiful Garden Of Prayer.json'))
        self.file_import([TEST_PATH / 'a mighty fortress is our god.sbsong'],
                         self.load_external_result_data(TEST_PATH / 'a mighty fortress is our god.json'))
        self.file_import([TEST_PATH / 'cleanse-me.sbsong'],
                         self.load_external_result_data(TEST_PATH / 'cleanse-me.json'))


class TestSongShowPlusImport(TestCase):
    """
    Test the functions in the :mod:`songshowplusimport` module.
    """
    def test_create_importer(self):
        """
        Test creating an instance of the SongShow Plus file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songshowplus.SongImport'):
            mocked_manager = MagicMock()

            # WHEN: An importer object is created
            importer = SongShowPlusImport(mocked_manager, file_paths=[])

            # THEN: The importer object should not be None
            assert importer is not None, 'Import should not be none'

    def test_invalid_import_source(self):
        """
        Test SongShowPlusImport.do_import handles different invalid import_source values
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songshowplus.SongImport'):
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            importer = SongShowPlusImport(mocked_manager, file_paths=[])
            importer.import_wizard = mocked_import_wizard
            importer.stop_import_flag = True

            # WHEN: Import source is not a list
            for source in ['not a list', 0]:
                importer.import_source = source

                # THEN: do_import should return none and the progress bar maximum should not be set.
                assert importer.do_import() is None, 'do_import should return None when import_source is not a list'
                assert mocked_import_wizard.progress_bar.setMaximum.called is False, \
                    'setMaximum on import_wizard.progress_bar should not have been called'

    def test_valid_import_source(self):
        """
        Test SongShowPlusImport.do_import handles different invalid import_source values
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songshowplus.SongImport'):
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            importer = SongShowPlusImport(mocked_manager, file_paths=[])
            importer.import_wizard = mocked_import_wizard
            importer.stop_import_flag = True

            # WHEN: Import source is a list
            importer.import_source = ['List', 'of', 'files']

            # THEN: do_import should return none and the progress bar setMaximum should be called with the length of
            #       import_source.
            assert importer.do_import() is None, \
                'do_import should return None when import_source is a list and stop_import_flag is True'
            mocked_import_wizard.progress_bar.setMaximum.assert_called_with(len(importer.import_source))

    def test_to_openlp_verse_tag(self):
        """
        Test to_openlp_verse_tag method by simulating adding a verse
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songshowplus.SongImport'):
            mocked_manager = MagicMock()
            importer = SongShowPlusImport(mocked_manager, file_paths=[])

            # WHEN: Supplied with the following arguments replicating verses being added
            test_values = [
                ('Verse 1', VerseType.tags[VerseType.Verse] + '1'),
                ('Verse 2', VerseType.tags[VerseType.Verse] + '2'),
                ('verse1', VerseType.tags[VerseType.Verse] + '1'),
                ('Verse', VerseType.tags[VerseType.Verse] + '1'),
                ('Verse1', VerseType.tags[VerseType.Verse] + '1'),
                ('chorus 1', VerseType.tags[VerseType.Chorus] + '1'),
                ('bridge 1', VerseType.tags[VerseType.Bridge] + '1'),
                ('pre-chorus 1', VerseType.tags[VerseType.PreChorus] + '1'),
                ('different 1', VerseType.tags[VerseType.Other] + '1'),
                ('random 1', VerseType.tags[VerseType.Other] + '2')]

            # THEN: The returned value should should correlate with the input arguments
            for original_tag, openlp_tag in test_values:
                assert importer.to_openlp_verse_tag(original_tag) == openlp_tag, \
                    'SongShowPlusImport.to_openlp_verse_tag should return "%s" when called with "%s"' % \
                    (openlp_tag, original_tag)

    def test_to_openlp_verse_tag_verse_order(self):
        """
        Test to_openlp_verse_tag method by simulating adding a verse to the verse order
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songshowplus.SongImport'):
            mocked_manager = MagicMock()
            importer = SongShowPlusImport(mocked_manager, file_paths=[])

            # WHEN: Supplied with the following arguments replicating a verse order being added
            test_values = [
                ('Verse 1', VerseType.tags[VerseType.Verse] + '1'),
                ('Verse 2', VerseType.tags[VerseType.Verse] + '2'),
                ('verse1', VerseType.tags[VerseType.Verse] + '1'),
                ('Verse', VerseType.tags[VerseType.Verse] + '1'),
                ('Verse1', VerseType.tags[VerseType.Verse] + '1'),
                ('chorus 1', VerseType.tags[VerseType.Chorus] + '1'),
                ('bridge 1', VerseType.tags[VerseType.Bridge] + '1'),
                ('pre-chorus 1', VerseType.tags[VerseType.PreChorus] + '1'),
                ('different 1', VerseType.tags[VerseType.Other] + '1'),
                ('random 1', VerseType.tags[VerseType.Other] + '2'),
                ('unused 2', None)]

            # THEN: The returned value should should correlate with the input arguments
            for original_tag, openlp_tag in test_values:
                assert importer.to_openlp_verse_tag(original_tag, ignore_unique=True) == openlp_tag, \
                    'SongShowPlusImport.to_openlp_verse_tag should return "%s" when called with "%s"' % \
                    (openlp_tag, original_tag)
