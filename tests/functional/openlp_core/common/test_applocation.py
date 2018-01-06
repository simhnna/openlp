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
Functional tests to test the AppLocation class and related methods.
"""
import os
from unittest.mock import patch

from openlp.core.common import get_frozen_path
from openlp.core.common.applocation import AppLocation
from openlp.core.common.path import Path

FILE_LIST = ['file1', 'file2', 'file3.txt', 'file4.txt', 'file5.mp3', 'file6.mp3']


@patch('openlp.core.common.applocation.Settings')
@patch('openlp.core.common.applocation.AppLocation.get_directory')
@patch('openlp.core.common.applocation.create_paths')
@patch('openlp.core.common.applocation.os')
def test_get_data_path(mocked_os, mocked_create_paths, mocked_get_directory, MockSettings):
    """
    Test the AppLocation.get_data_path() method
    """
    # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_directory()
    MockSettings.return_value.contains.return_value = False
    mocked_get_directory.return_value = os.path.join('tests', 'dir')
    mocked_create_paths.return_value = True
    mocked_os.path.normpath.return_value = os.path.join('tests', 'dir')

    # WHEN: we call AppLocation.get_data_path()
    data_path = AppLocation.get_data_path()

    # THEN: check that all the correct methods were called, and the result is correct
    MockSettings.return_value.contains.assert_called_with('advanced/data path')
    mocked_get_directory.assert_called_with(AppLocation.DataDir)
    mocked_create_paths.assert_called_with(os.path.join('tests', 'dir'))
    assert data_path == os.path.join('tests', 'dir'), 'Result should be "tests/dir"'


@patch('openlp.core.common.applocation.Settings')
def test_get_data_path_with_custom_location(MockSettings):
    """
    Test the AppLocation.get_data_path() method when a custom location is set in the settings
    """
    # GIVEN: A mocked out Settings class which returns a custom data location
    MockSettings.return_value.contains.return_value = True
    MockSettings.return_value.value.return_value = Path('custom', 'dir')

    # WHEN: we call AppLocation.get_data_path()
    data_path = AppLocation.get_data_path()

    # THEN: the mocked Settings methods were called and the value returned was our set up value
    MockSettings.return_value.contains.assert_called_with('advanced/data path')
    MockSettings.return_value.value.assert_called_with('advanced/data path')
    assert data_path == Path('custom', 'dir'), 'Result should be "custom/dir"'


@patch('openlp.core.common.applocation.Path.glob')
@patch('openlp.core.common.applocation.AppLocation.get_data_path')
def test_get_files_no_section_no_extension(mocked_get_data_path, mocked_glob):
    """
    Test the AppLocation.get_files() method with no parameters passed.
    """
    # GIVEN: Our mocked modules/methods.
    mocked_glob.return_value = [Path('/dir/file5.mp3'), Path('/dir/file6.mp3')]
    mocked_get_data_path.return_value = Path('/dir')

    # When: Get the list of files.
    result = AppLocation.get_files()

    # Then: Check if the section parameter was used correctly, and the glob argument was passed.
    mocked_glob.assert_called_once_with('*')
    assert result == [Path('file5.mp3'), Path('file6.mp3')], 'The file lists should be identical.'


@patch('openlp.core.common.applocation.Path.glob')
@patch('openlp.core.common.applocation.AppLocation.get_data_path')
def test_get_files(mocked_get_data_path, mocked_glob):
    """
    Test the AppLocation.get_files() method with all parameters passed.
    """
    # GIVEN: Our mocked modules/methods.
    mocked_glob.return_value = [Path('/dir/section/file5.mp3'), Path('/dir/section/file6.mp3')]
    mocked_get_data_path.return_value = Path('/dir')

    # When: Get the list of files.
    result = AppLocation.get_files('section', '.mp3')

    # Then: The section parameter was used correctly, and the glob argument was passed..
    mocked_glob.assert_called_once_with('*.mp3')
    assert result == [Path('file5.mp3'), Path('file6.mp3')], 'The file lists should be identical.'


@patch('openlp.core.common.applocation.AppLocation.get_data_path')
@patch('openlp.core.common.applocation.create_paths')
def test_get_section_data_path(mocked_create_paths, mocked_get_data_path):
    """
    Test the AppLocation.get_section_data_path() method
    """
    # GIVEN: A mocked out AppLocation.get_data_path()
    mocked_get_data_path.return_value = Path('test', 'dir')
    mocked_create_paths.return_value = True

    # WHEN: we call AppLocation.get_data_path()
    data_path = AppLocation.get_section_data_path('section')

    # THEN: check that all the correct methods were called, and the result is correct
    mocked_create_paths.assert_called_with(Path('test', 'dir', 'section'))
    assert data_path == Path('test', 'dir', 'section'), 'Result should be "test/dir/section"'


@patch('openlp.core.common.applocation.get_frozen_path')
def test_get_directory_for_app_dir(mocked_get_frozen_path):
    """
    Test the AppLocation.get_directory() method for AppLocation.AppDir
    """
    # GIVEN: A mocked out _get_frozen_path function
    mocked_get_frozen_path.return_value = Path('app', 'dir')

    # WHEN: We call AppLocation.get_directory
    directory = AppLocation.get_directory(AppLocation.AppDir)

    # THEN: check that the correct directory is returned
    assert directory == Path('app', 'dir'), 'Directory should be "app/dir"'


@patch('openlp.core.common.applocation.get_frozen_path')
@patch('openlp.core.common.applocation.os.path.abspath')
@patch('openlp.core.common.applocation.os.path.split')
@patch('openlp.core.common.applocation.sys')
def test_get_directory_for_plugins_dir(mocked_sys, mocked_split, mocked_abspath, mocked_get_frozen_path):
    """
    Test the AppLocation.get_directory() method for AppLocation.PluginsDir
    """
    # GIVEN: _get_frozen_path, abspath, split and sys are mocked out
    mocked_abspath.return_value = os.path.join('plugins', 'dir')
    mocked_split.return_value = ['openlp']
    mocked_get_frozen_path.return_value = Path('dir')
    mocked_sys.frozen = 1
    mocked_sys.argv = ['openlp']

    # WHEN: We call AppLocation.get_directory
    directory = AppLocation.get_directory(AppLocation.PluginsDir)

    # THEN: The correct directory should be returned
    assert directory == Path('dir', 'plugins'), 'Directory should be "dir/plugins"'


@patch('openlp.core.common.sys')
def test_get_frozen_path_in_unfrozen_app(mocked_sys):
    """
    Test the _get_frozen_path() function when the application is not frozen (compiled by PyInstaller)
    """
    # GIVEN: The sys module "without" a "frozen" attribute
    mocked_sys.frozen = None

    # WHEN: We call _get_frozen_path() with two parameters
    frozen_path = get_frozen_path('frozen', 'not frozen')

    # THEN: The non-frozen parameter is returned
    assert frozen_path == 'not frozen', '_get_frozen_path should return "not frozen"'


@patch('openlp.core.common.sys')
def test_get_frozen_path_in_frozen_app(mocked_sys):
    """
    Test the get_frozen_path() function when the application is frozen (compiled by PyInstaller)
    """
    # GIVEN: The sys module *with* a "frozen" attribute
    mocked_sys.frozen = 1

    # WHEN: We call _get_frozen_path() with two parameters
    frozen_path = get_frozen_path('frozen', 'not frozen')

    # THEN: The frozen parameter is returned
    assert frozen_path == 'frozen', 'Should return "frozen"'
