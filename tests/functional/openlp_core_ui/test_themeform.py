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
Package to test the openlp.core.ui.themeform package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.path import Path
from openlp.core.ui import ThemeForm


class TestThemeManager(TestCase):
    """
    Test the functions in the ThemeManager Class
    """
    def setUp(self):
        with patch('openlp.core.ui.ThemeForm._setup'):
            self.instance = ThemeForm(None)

    def test_on_image_path_edit_path_changed(self):
        """
        Test the `image_path_edit.pathChanged` handler
        """
        # GIVEN: An instance of Theme Form
        with patch.object(self.instance, 'set_background_page_values') as mocked_set_background_page_values:
            self.instance.theme = MagicMock()

            # WHEN: `on_image_path_edit_path_changed` is clicked
            self.instance.on_image_path_edit_path_changed(Path('/', 'new', 'pat.h'))

            # THEN: The theme background file should be set and `set_background_page_values` should have been called
            self.assertEqual(self.instance.theme.background_filename, '/new/pat.h')
            mocked_set_background_page_values.assert_called_once_with()
