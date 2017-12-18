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
Package to test the openlp.core.lib.settings package.
"""
from pathlib import Path
from unittest import TestCase
from unittest.mock import call, patch

from openlp.core.common import settings
from openlp.core.common.settings import Settings, media_players_conv

from tests.helpers.testmixin import TestMixin


class TestSettings(TestCase, TestMixin):
    """
    Test the functions in the Settings module
    """
    def setUp(self):
        """
        Create the UI
        """
        self.setup_application()
        self.build_settings()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()

    def test_media_players_conv(self):
        """Test the media players conversion function"""
        # GIVEN: A list of media players
        media_players = 'phonon,webkit,vlc'

        # WHEN: The media converter function is called
        result = media_players_conv(media_players)

        # THEN: The list should have been converted correctly
        assert result == 'system,webkit,vlc'

    def test_default_value(self):
        """Test reading a setting that doesn't exist yet"""
        # GIVEN: A setting that doesn't exist yet

        # WHEN reading a setting for the first time
        default_value = Settings().value('core/has run wizard')

        # THEN the default value is returned
        assert default_value is False, 'The default value should be False'

    def test_save_new_value(self):
        """Test saving a new setting"""
        # GIVEN: A setting that hasn't been saved yet
        # WHEN a new value is saved into config
        Settings().setValue('core/has run wizard', True)

        # THEN the new value is returned when re-read
        assert Settings().value('core/has run wizard') is True, 'The saved value should have been returned'

    def test_set_up_default_values(self):
        """Test that the default values are updated"""
        # GIVEN: A Settings object with defaults
        # WHEN: set_up_default_values() is called
        Settings.set_up_default_values()

        # THEN: The default values should have been added to the dictionary
        assert 'advanced/default service name' in Settings.__default_settings__

    def test_get_default_value(self):
        """Test that the default value for a setting is returned"""
        # GIVEN: A Settings class with a default value
        Settings.__default_settings__['test/moo'] = 'baa'

        # WHEN: get_default_value() is called
        result = Settings().get_default_value('test/moo')

        # THEN: The correct default value should be returned
        assert result == 'baa'

    def test_settings_override(self):
        """Test the Settings creation and its override usage"""
        # GIVEN: an override for the settings
        screen_settings = {
            'test/extend': 'very wide',
        }
        Settings().extend_default_settings(screen_settings)

        # WHEN reading a setting for the first time
        extend = Settings().value('test/extend')

        # THEN the default value is returned
        assert extend == 'very wide', 'The default value of "very wide" should be returned'

    def test_save_existing_setting(self):
        """Test that saving an existing setting returns the new value"""
        # GIVEN: An existing setting
        Settings().extend_default_settings({'test/existing value': None})
        Settings().setValue('test/existing value', 'old value')

        # WHEN a new value is saved into config
        Settings().setValue('test/existing value', 'new value')

        # THEN the new value is returned when re-read
        assert Settings().value('test/existing value') == 'new value', 'The saved value should be returned'

    def test_settings_override_with_group(self):
        """Test the Settings creation and its override usage - with groups"""
        # GIVEN: an override for the settings
        screen_settings = {
            'test/extend': 'very wide',
        }
        Settings.extend_default_settings(screen_settings)

        # WHEN reading a setting for the first time
        settings = Settings()
        settings.beginGroup('test')
        extend = settings.value('extend')

        # THEN the default value is returned
        assert 'very wide' == extend, 'The default value defined should be returned'

        # WHEN a new value is saved into config
        Settings().setValue('test/extend', 'very short')

        # THEN the new value is returned when re-read
        assert 'very short' == Settings().value('test/extend'), 'The saved value should be returned'

    def test_settings_nonexisting(self):
        """Test the Settings on query for non-existing value"""
        # GIVEN: A new Settings setup
        with self.assertRaises(KeyError) as cm:
            # WHEN reading a setting that doesn't exists
            Settings().value('core/does not exists')

        # THEN: An exception with the non-existing key should be thrown
        assert str(cm.exception) == "'core/does not exists'", 'We should get an exception'

    def test_extend_default_settings(self):
        """Test that the extend_default_settings method extends the default settings"""
        # GIVEN: A patched __default_settings__ dictionary
        with patch.dict(Settings.__default_settings__,
                        {'test/setting 1': 1, 'test/setting 2': 2, 'test/setting 3': 3}, True):

            # WHEN: Calling extend_default_settings
            Settings.extend_default_settings({'test/setting 3': 4, 'test/extended 1': 1, 'test/extended 2': 2})

            # THEN: The _default_settings__ dictionary_ should have the new keys
            assert Settings.__default_settings__ == {'test/setting 1': 1, 'test/setting 2': 2, 'test/setting 3': 4,
                                                     'test/extended 1': 1, 'test/extended 2': 2}

    @patch('openlp.core.common.settings.QtCore.QSettings.contains')
    @patch('openlp.core.common.settings.QtCore.QSettings.value')
    @patch('openlp.core.common.settings.QtCore.QSettings.setValue')
    @patch('openlp.core.common.settings.QtCore.QSettings.remove')
    def test_upgrade_single_setting(self, mocked_remove, mocked_setValue, mocked_value, mocked_contains):
        """Test that the upgrade mechanism for settings works correctly for single value upgrades"""
        # GIVEN: A settings object with an upgrade step to take (99, so that we don't interfere with real ones)
        local_settings = Settings()
        local_settings.__setting_upgrade_99__ = [
            ('single/value', 'single/new value', [(str, '')])
        ]
        settings.__version__ = 99
        mocked_value.side_effect = [98, 10]
        mocked_contains.return_value = True

        # WHEN: upgrade_settings() is called
        local_settings.upgrade_settings()

        # THEN: The correct calls should have been made with the correct values
        assert mocked_value.call_count == 2, 'Settings().value() should have been called twice'
        assert mocked_value.call_args_list == [call('settings/version', 0), call('single/value')]
        assert mocked_setValue.call_count == 2, 'Settings().setValue() should have been called twice'
        assert mocked_setValue.call_args_list == [call('single/new value', '10'), call('settings/version', 99)]
        mocked_contains.assert_called_once_with('single/value')
        mocked_remove.assert_called_once_with('single/value')

    @patch('openlp.core.common.settings.QtCore.QSettings.contains')
    @patch('openlp.core.common.settings.QtCore.QSettings.value')
    @patch('openlp.core.common.settings.QtCore.QSettings.setValue')
    @patch('openlp.core.common.settings.QtCore.QSettings.remove')
    def test_upgrade_setting_value(self, mocked_remove, mocked_setValue, mocked_value, mocked_contains):
        """Test that the upgrade mechanism for settings correctly uses the new value when it's not a function"""
        # GIVEN: A settings object with an upgrade step to take (99, so that we don't interfere with real ones)
        local_settings = Settings()
        local_settings.__setting_upgrade_99__ = [
            ('values/old value', 'values/new value', [(True, 1)])
        ]
        settings.__version__ = 99
        mocked_value.side_effect = [98, 1]
        mocked_contains.return_value = True

        # WHEN: upgrade_settings() is called
        local_settings.upgrade_settings()

        # THEN: The correct calls should have been made with the correct values
        assert mocked_value.call_count == 2, 'Settings().value() should have been called twice'
        assert mocked_value.call_args_list == [call('settings/version', 0), call('values/old value')]
        assert mocked_setValue.call_count == 2, 'Settings().setValue() should have been called twice'
        assert mocked_setValue.call_args_list == [call('values/new value', True), call('settings/version', 99)]
        mocked_contains.assert_called_once_with('values/old value')
        mocked_remove.assert_called_once_with('values/old value')

    @patch('openlp.core.common.settings.QtCore.QSettings.contains')
    @patch('openlp.core.common.settings.QtCore.QSettings.value')
    @patch('openlp.core.common.settings.QtCore.QSettings.setValue')
    @patch('openlp.core.common.settings.QtCore.QSettings.remove')
    def test_upgrade_multiple_one_invalid(self, mocked_remove, mocked_setValue, mocked_value, mocked_contains):
        """Test that the upgrade mechanism for settings works correctly for multiple values where one is invalid"""
        # GIVEN: A settings object with an upgrade step to take
        local_settings = Settings()
        local_settings.__setting_upgrade_99__ = [
            (['multiple/value 1', 'multiple/value 2'], 'single/new value', [])
        ]
        settings.__version__ = 99
        mocked_value.side_effect = [98, 10]
        mocked_contains.side_effect = [True, False]

        # WHEN: upgrade_settings() is called
        local_settings.upgrade_settings()

        # THEN: The correct calls should have been made with the correct values
        mocked_value.assert_called_once_with('settings/version', 0)
        mocked_setValue.assert_called_once_with('settings/version', 99)
        assert mocked_contains.call_args_list == [call('multiple/value 1'), call('multiple/value 2')]

    def test_can_upgrade(self):
        """Test the Settings.can_upgrade() method"""
        # GIVEN: A Settings object
        local_settings = Settings()

        # WHEN: can_upgrade() is run
        result = local_settings.can_upgrade()

        # THEN: The result should be True
        assert result is True, 'The settings should be upgradeable'

    def test_convert_value_setting_none_str(self):
        """Test the Settings._convert_value() method when a setting is None and the default value is a string"""
        # GIVEN: A settings object
        # WHEN: _convert_value() is run
        result = Settings()._convert_value(None, 'string')

        # THEN: The result should be an empty string
        assert result == '', 'The result should be an empty string'

    def test_convert_value_setting_none_list(self):
        """Test the Settings._convert_value() method when a setting is None and the default value is a list"""
        # GIVEN: A settings object
        # WHEN: _convert_value() is run
        result = Settings()._convert_value(None, [None])

        # THEN: The result should be an empty list
        assert result == [], 'The result should be an empty list'

    def test_convert_value_setting_json_Path(self):
        """Test the Settings._convert_value() method when a setting is JSON and represents a Path object"""
        # GIVEN: A settings object
        # WHEN: _convert_value() is run
        result = Settings()._convert_value('{"__Path__": ["openlp", "core"]}', None)

        # THEN: The result should be a Path object
        assert isinstance(result, Path), 'The result should be a Path object'

    def test_convert_value_setting_bool_str(self):
        """Test the Settings._convert_value() method when a setting is supposed to be a boolean"""
        # GIVEN: A settings object
        # WHEN: _convert_value() is run
        result = Settings()._convert_value('false', True)

        # THEN: The result should be False
        assert result is False, 'The result should be False'
