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
Package to test the openlp.core.lib.pluginmanager package.
"""
import gc
import sys
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtWidgets

from openlp.core.common.path import Path
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib.pluginmanager import PluginManager
from tests.helpers.testmixin import TestMixin


class TestPluginManager(TestCase, TestMixin):
    """
    Test the PluginManager class
    """

    def setUp(self):
        """
        Some pre-test setup required.
        """
        self.setup_application()
        self.build_settings()
        self.temp_dir_path = Path(mkdtemp('openlp'))
        Settings().setValue('advanced/data path', self.temp_dir_path)
        Registry.create()
        Registry().register('service_list', MagicMock())
        self.main_window = QtWidgets.QMainWindow()
        Registry().register('main_window', self.main_window)

    def tearDown(self):
        Settings().remove('advanced/data path')
        self.destroy_settings()
        del self.main_window
        # On windows we need to manually garbage collect to close sqlalchemy files
        # to avoid errors when temporary files are deleted.
        gc.collect()
        self.temp_dir_path.rmtree()

    @patch('openlp.plugins.songusage.lib.db.init_schema')
    @patch('openlp.plugins.songs.lib.db.init_schema')
    @patch('openlp.plugins.images.lib.db.init_schema')
    @patch('openlp.plugins.custom.lib.db.init_schema')
    @patch('openlp.plugins.alerts.lib.db.init_schema')
    @patch('openlp.plugins.bibles.lib.db.init_schema')
    def test_find_plugins(self, mocked_is1, mocked_is2, mocked_is3, mocked_is4, mocked_is5, mocked_is6):
        """
        Test the find_plugins() method to ensure it imports the correct plugins
        """
        # GIVEN: A plugin manager
        plugin_manager = PluginManager()

        # WHEN: We mock out sys.platform to make it return "darwin" and then find the plugins
        old_platform = sys.platform
        sys.platform = 'darwin'
        plugin_manager.find_plugins()
        sys.platform = old_platform

        # THEN: We should find the "Songs", "Bibles", etc in the plugins list
        plugin_names = [plugin.name for plugin in plugin_manager.plugins]
        assert 'songs' in plugin_names, 'There should be a "songs" plugin'
        assert 'bibles' in plugin_names, 'There should be a "bibles" plugin'
        assert 'presentations' in plugin_names, 'There should be a "presentations" plugin'
        assert 'images' in plugin_names, 'There should be a "images" plugin'
        assert 'media' in plugin_names, 'There should be a "media" plugin'
        assert 'custom' in plugin_names, 'There should be a "custom" plugin'
        assert 'songusage'in plugin_names, 'There should be a "songusage" plugin'
        assert 'alerts' in plugin_names, 'There should be a "alerts" plugin'
