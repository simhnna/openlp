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
Package to test the :mod:`~openlp.core.ui.style` module.
"""
from unittest import skipIf
from unittest.mock import MagicMock, patch

import openlp.core.ui.style
from openlp.core.ui.style import MEDIA_MANAGER_STYLE, WIN_REPAIR_STYLESHEET, get_application_stylesheet, \
    get_library_stylesheet


@skipIf(not hasattr(openlp.core.ui.style, 'qdarkstyle'), 'qdarkstyle is not installed')
@patch('openlp.core.ui.style.HAS_DARK_STYLE', True)
@patch('openlp.core.ui.style.Settings')
@patch('openlp.core.ui.style.qdarkstyle')
def test_get_application_stylesheet_dark(mocked_qdarkstyle, MockSettings):
    """Test that the dark stylesheet is returned when available and enabled"""
    # GIVEN: We're on Windows and no dark style is set
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = True
    MockSettings.return_value = mocked_settings
    mocked_qdarkstyle.load_stylesheet_pyqt5.return_value = 'dark_style'

    # WHEN: can_show_icon() is called
    result = get_application_stylesheet()

    # THEN: the result should be false
    assert result == 'dark_style'


@patch('openlp.core.ui.style.HAS_DARK_STYLE', False)
@patch('openlp.core.ui.style.is_win')
@patch('openlp.core.ui.style.Settings')
@patch('openlp.core.ui.style.Registry')
def test_get_application_stylesheet_not_alternate_rows(MockRegistry, MockSettings, mocked_is_win):
    """Test that the alternate rows stylesheet is returned when enabled in settings"""
    # GIVEN: We're on Windows and no dark style is set
    mocked_is_win.return_value = False
    MockSettings.return_value.value.return_value = False
    MockRegistry.return_value.get.return_value.palette.return_value.color.return_value.name.return_value = 'color'

    # WHEN: can_show_icon() is called
    result = get_application_stylesheet()

    # THEN: the result should be false
    MockSettings.return_value.value.assert_called_once_with('advanced/alternate rows')
    assert result == 'QTableWidget, QListWidget, QTreeWidget {alternate-background-color: color;}\n', result


@patch('openlp.core.ui.style.HAS_DARK_STYLE', False)
@patch('openlp.core.ui.style.is_win')
@patch('openlp.core.ui.style.Settings')
def test_get_application_stylesheet_win_repair(MockSettings, mocked_is_win):
    """Test that the Windows repair stylesheet is returned when on Windows"""
    # GIVEN: We're on Windows and no dark style is set
    mocked_is_win.return_value = True
    MockSettings.return_value.value.return_value = True

    # WHEN: can_show_icon() is called
    result = get_application_stylesheet()

    # THEN: the result should be false
    MockSettings.return_value.value.assert_called_once_with('advanced/alternate rows')
    assert result == WIN_REPAIR_STYLESHEET


@patch('openlp.core.ui.style.HAS_DARK_STYLE', False)
@patch('openlp.core.ui.style.Settings')
def test_get_library_stylesheet_no_dark_style(MockSettings):
    """Test that the media manager stylesheet is returned when there's no dark theme available"""
    # GIVEN: No dark style
    MockSettings.return_value.value.return_value = False

    # WHEN: get_library_stylesheet() is called
    result = get_library_stylesheet()

    # THEN: The correct stylesheet should be returned
    assert result == MEDIA_MANAGER_STYLE


@patch('openlp.core.ui.style.HAS_DARK_STYLE', True)
@patch('openlp.core.ui.style.Settings')
def test_get_library_stylesheet_dark_style(MockSettings):
    """Test that no stylesheet is returned when the dark theme is enabled"""
    # GIVEN: No dark style
    MockSettings.return_value.value.return_value = True

    # WHEN: get_library_stylesheet() is called
    result = get_library_stylesheet()

    # THEN: The correct stylesheet should be returned
    assert result == ''
