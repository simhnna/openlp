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
This module contains tests for the lib submodule of the Bibles plugin.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.bibles.lib import BibleManager, parse_reference, LanguageSelection
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


class TestBibleManager(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the environment for testing bible parse reference
        """
        self.setup_application()
        self.build_settings()
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('application', MagicMock())
        bible_settings = {
            'bibles/proxy name': '',
            'bibles/db type': 'sqlite',
            'bibles/book name language': LanguageSelection.Bible,
            'bibles/verse separator': '',
            'bibles/range separator': '',
            'bibles/list separator': '',
            'bibles/end separator': '',
        }
        Settings().extend_default_settings(bible_settings)
        with patch('openlp.core.common.applocation.Settings') as mocked_class, \
                patch('openlp.core.common.applocation.AppLocation.get_section_data_path') as mocked_get_data_path, \
                patch('openlp.core.common.applocation.AppLocation.get_files') as mocked_get_files:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_files()
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = False
            mocked_get_files.return_value = ["tests.sqlite"]
            mocked_get_data_path.return_value = TEST_RESOURCES_PATH + "/bibles"
            self.manager = BibleManager(MagicMock())

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.manager
        self.destroy_settings()

    def test_parse_reference_one(self):
        """
        Test the parse_reference method with 1 Timothy 1
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a verse array should be returned
        assert [(54, 1, 1, -1)] == results, "The bible verses should matches the expected results"

    def test_parse_reference_two(self):
        """
        Test the parse_reference method with 1 Timothy 1:1-2
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1:1-2', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a verse array should be returned
        assert [(54, 1, 1, 2)] == results, "The bible verses should matches the expected results"

    def test_parse_reference_three(self):
        """
        Test the parse_reference method with 1 Timothy 1:1-2
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1:1-2:1', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a verse array should be returned
        assert [(54, 1, 1, -1), (54, 2, 1, 1)] == results, \
            "The bible verses should match the expected results"

    def test_parse_reference_four(self):
        """
        Test the parse_reference method with non existence book
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('Raoul 1', self.manager.db_cache['tests'], MagicMock())
        # THEN a verse array should be returned
        assert [] == results, "The bible Search should return an empty list"

    def test_parse_reference_five(self):
        """
        Test the parse_reference method with 1 Timothy 1:3-end
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1:3-end', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a verse array should be returned
        assert [(54, 1, 3, -1)] == results, "The bible verses should matches the expected results"
