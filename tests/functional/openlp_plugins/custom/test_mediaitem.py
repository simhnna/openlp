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
This module contains tests for the lib submodule of the Songs plugin.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from PyQt5 import QtCore

from openlp.core.common.registry import Registry
from openlp.core.lib import ServiceItem, PluginStatus
from openlp.plugins.custom.lib import CustomMediaItem

from tests.helpers.testmixin import TestMixin

FOOTER = ['Arky Arky (Unknown)', 'Public Domain', 'CCLI 123456']


class TestMediaItem(TestCase, TestMixin):
    """
    Test the functions in the :mod:`lib` module.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('main_window', MagicMock())
        with patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup'), \
                patch('openlp.core.lib.mediamanageritem.MediaManagerItem.setup_item'), \
                patch('openlp.plugins.custom.forms.editcustomform.EditCustomForm.__init__'), \
                patch('openlp.plugins.custom.lib.mediaitem.CustomMediaItem.setup_item'):
            self.media_item = CustomMediaItem(None, MagicMock())
        self.setup_application()
        self.build_settings()
        QtCore.QLocale.setDefault(QtCore.QLocale('en_GB'))

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()

    def test_service_load_inactive(self):
        """
        Test the service load in custom with a default service item
        """
        # GIVEN: An empty Service Item
        service_item = ServiceItem(None)

        # WHEN: I search for the custom in the database
        item = self.media_item.service_load(service_item)

        # THEN: the processing should be ignored
        assert item is None, 'The Service item is inactive so processing should be bypassed'

    def test_service_load_basic_custom_false(self):
        """
        Test the service load in custom with a default service item and no requirement to add to the database
        """
        # GIVEN: An empty Service Item and an active plugin
        service_item = ServiceItem(None)
        service_item.raw_footer = FOOTER
        self.media_item.plugin = MagicMock()
        self.media_item.plugin.status = PluginStatus.Active
        self.media_item.plugin.db_manager = MagicMock()
        self.media_item.plugin.db_manager.get_object_filtered = MagicMock()
        self.media_item.plugin.db_manager.get_object_filtered.return_value = None

        with patch('openlp.plugins.custom.lib.mediaitem.CustomSlide'):
            # WHEN: I search for the custom in the database
            self.media_item.add_custom_from_service = False
            self.media_item.create_from_service_item = MagicMock()
            self.media_item.service_load(service_item)

            # THEN: the item should not be added to the database.
            assert self.media_item.create_from_service_item.call_count == 0, \
                'The item should not have been added to the database'

    def test_service_load_basic_custom_true(self):
        """
        Test the service load in custom with a default service item and a requirement to add to the database
        """
        # GIVEN: An empty Service Item and an active plugin
        service_item = ServiceItem(None)
        service_item.raw_footer = FOOTER
        self.media_item.plugin = MagicMock()
        self.media_item.plugin.status = PluginStatus.Active
        self.media_item.plugin.db_manager = MagicMock()
        self.media_item.plugin.db_manager.get_object_filtered = MagicMock()
        self.media_item.plugin.db_manager.get_object_filtered.return_value = None

        with patch('openlp.plugins.custom.lib.mediaitem.CustomSlide'):
            # WHEN: I search for the custom in the database
            self.media_item.add_custom_from_service = True
            self.media_item.create_from_service_item = MagicMock()
            self.media_item.service_load(service_item)

            # THEN: the item should not be added to the database.
            assert self.media_item.create_from_service_item.call_count == 1, \
                'The item should have been added to the database'
