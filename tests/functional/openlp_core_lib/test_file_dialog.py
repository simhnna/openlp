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
Package to test the openlp.core.lib.filedialog package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch



class TestFileDialog(TestCase):
    """
    Test the functions in the :mod:`filedialog` module.
    """
    def setUp(self):
        self.os_patcher = patch('openlp.core.lib.filedialog.os')
        self.qt_gui_patcher = patch('openlp.core.lib.filedialog.QtWidgets')
        self.ui_strings_patcher = patch('openlp.core.lib.filedialog.UiStrings')
        self.mocked_os = self.os_patcher.start()
        self.mocked_qt_gui = self.qt_gui_patcher.start()
        self.mocked_ui_strings = self.ui_strings_patcher.start()
        self.mocked_parent = MagicMock()

    def tearDown(self):
        self.os_patcher.stop()
        self.qt_gui_patcher.stop()
        self.ui_strings_patcher.stop()
