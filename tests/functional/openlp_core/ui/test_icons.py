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
Package to test the openlp.core.ui.icons package.
"""
from unittest import TestCase, skipUnless
from unittest.mock import MagicMock, patch

from PyQt5 import QtGui

from openlp.core.ui.icons import UiIcons

from tests.helpers.testmixin import TestMixin


class TestIcons(TestCase, TestMixin):

    @patch('openlp.core.ui.icons.UiIcons.load')
    def test_simple_icon(self, _):
        # GIVEN: an basic set of icons
        icons = UiIcons()
        icon_list = {
            'active': {'icon': 'fa.child'}

        }

        icons.load_icons(icon_list)
        # WHEN: I use the icons
        icon_active = UiIcons().active
        # THEN: I should have an icon
        assert isinstance(icon_active, QtGui.QIcon)
