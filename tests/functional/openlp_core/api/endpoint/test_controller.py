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
from unittest import TestCase
from unittest.mock import MagicMock

from PyQt5 import QtCore

from openlp.core.common.registry import Registry
from openlp.core.api.endpoint.controller import controller_text, controller_direction
from openlp.core.display.renderer import Renderer
from openlp.core.display.screens import ScreenList
from openlp.core.lib import ServiceItem

from tests.utils import convert_file_service_item
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = str(RESOURCE_PATH / 'service')

SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


class TestController(TestCase):
    """
    Test the Remote plugin deploy functions
    """

    def setUp(self):
        """
        Setup for tests
        """
        Registry.create()
        self.registry = Registry()
        self.mocked_live_controller = MagicMock()
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']
        self.screens = ScreenList.create(self.desktop)
        renderer = Renderer()
        renderer.empty_height = 1000
        Registry().register('live_controller', self.mocked_live_controller)

    def test_controller_text_empty(self):
        """
        Remote API Tests : test the controller text method can be called with empty service item
        """
        # GIVEN: A mocked service with a dummy service item
        self.mocked_live_controller.service_item = MagicMock()
        # WHEN: I trigger the method
        ret = controller_text("SomeText")
        # THEN: I get a basic set of results
        results = ret['results']
        assert isinstance(results['item'], MagicMock)
        assert len(results['slides']) == 0

    def test_controller_text(self):
        """
        Remote API Tests : test the controller text method can be called with a real service item
        """
        # GIVEN: A mocked service with a dummy service item
        line = convert_file_service_item(TEST_PATH, 'serviceitem_custom_1.osj')
        self.mocked_live_controller.service_item = ServiceItem(None)
        self.mocked_live_controller.service_item.set_from_service(line)
        self.mocked_live_controller.service_item.render(True)
        # WHEN: I trigger the method
        ret = controller_text("SomeText")
        # THEN: I get a basic set of results
        results = ret['results']
        assert isinstance(ret, dict)
        assert len(results['slides']) == 2

    def test_controller_direction_next(self):
        """
        Text the live next method is triggered
        """
        # GIVEN: A mocked service with a dummy service item
        self.mocked_live_controller.service_item = MagicMock()
        # WHEN: I trigger the method
        controller_direction(None, 'live', 'next')
        # THEN: The correct method is called
        self.mocked_live_controller.slidecontroller_live_next.emit.assert_called_once_with()

    def test_controller_direction_previous(self):
        """
        Text the live next method is triggered
        """
        # GIVEN: A mocked service with a dummy service item
        self.mocked_live_controller.service_item = MagicMock()
        # WHEN: I trigger the method
        controller_direction(None, 'live', 'previous')
        # THEN: The correct method is called
        self.mocked_live_controller.slidecontroller_live_previous.emit.assert_called_once_with()
