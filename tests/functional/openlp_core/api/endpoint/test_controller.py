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
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.api.endpoint.controller import controller_text


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
        Registry().register('live_controller', self.mocked_live_controller)

    def test_controller_text(self):
        """
        Remote Deploy tests - test the dummy zip file is processed correctly
        """
        # GIVEN: A mocked service with a dummy service item
        self.mocked_live_controller.service_item = MagicMock()
        # WHEN: I trigger the method
        ret = controller_text("SomeText")
        # THEN: I get a basic set of results
        results = ret['results']
        assert isinstance(results['item'], MagicMock)
        assert len(results['slides']) == 0