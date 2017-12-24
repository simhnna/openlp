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
This module contains tests for the LyriX song importer.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'lyrixsongs'


class TestLyrixFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'LyrixImport'
        self.importer_module_name = 'lyrix'
        super(TestLyrixFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading an LyriX file works correctly on various files
        """
        self.file_import([TEST_PATH / 'A06.TXT'],
                         self.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
        self.file_import([TEST_PATH / 'A002.TXT'],
                         self.load_external_result_data(TEST_PATH / 'Amazing Grace2.json'))
        self.file_import([TEST_PATH / 'AO05.TXT'],
                         self.load_external_result_data(TEST_PATH / 'in die regterhand.json'))
