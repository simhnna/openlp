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
Module to test the custom widgets.
"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from openlp.core.common.registry import Registry
from openlp.core.common.settings import ProxyMode
from openlp.core.widgets.widgets import ProxyWidget
from tests.helpers.testmixin import TestMixin


class TestProxyWidget(TestCase, TestMixin):
    """
    Test the EditCustomForm.
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()

    def test_radio_button_exclusivity(self):
        """
        Test that only one radio button can be checked at a time, and that the line edits are only enabled when the
        `manual_proxy_radio` is checked
        """
        # GIVEN: An instance of the `openlp.core.common.widgets.widgets.ProxyWidget`
        proxy_widget = ProxyWidget()

        # WHEN: 'Checking' the `no_proxy_radio` button
        proxy_widget.no_proxy_radio.setChecked(True)

        # THEN: The other radio buttons should not be checked and the line edits should not be enabled
        assert proxy_widget.use_sysem_proxy_radio.isChecked() is False
        assert proxy_widget.manual_proxy_radio.isChecked() is False
        assert proxy_widget.http_edit.isEnabled() is False
        assert proxy_widget.https_edit.isEnabled() is False
        assert proxy_widget.username_edit.isEnabled() is False
        assert proxy_widget.password_edit.isEnabled() is False

        # WHEN: 'Checking' the `use_sysem_proxy_radio` button
        proxy_widget.use_sysem_proxy_radio.setChecked(True)

        # THEN: The other radio buttons should not be checked and the line edits should not be enabled
        assert proxy_widget.no_proxy_radio.isChecked() is False
        assert proxy_widget.manual_proxy_radio.isChecked() is False
        assert proxy_widget.http_edit.isEnabled() is False
        assert proxy_widget.https_edit.isEnabled() is False
        assert proxy_widget.username_edit.isEnabled() is False
        assert proxy_widget.password_edit.isEnabled() is False

        # WHEN: 'Checking' the `manual_proxy_radio` button
        proxy_widget.manual_proxy_radio.setChecked(True)

        # THEN: The other radio buttons should not be checked and the line edits should be enabled
        assert proxy_widget.no_proxy_radio.isChecked() is False
        assert proxy_widget.use_sysem_proxy_radio.isChecked() is False
        assert proxy_widget.http_edit.isEnabled() is True
        assert proxy_widget.https_edit.isEnabled() is True
        assert proxy_widget.username_edit.isEnabled() is True
        assert proxy_widget.password_edit.isEnabled() is True

    def test_proxy_widget_load_default_settings(self):
        """
        Test that the default settings are loaded from the config correctly
        """
        # GIVEN: And instance of the widget with default settings
        proxy_widget = ProxyWidget()

        # WHEN: Calling the `load` method
        proxy_widget.load()

        # THEN: The widget should be in its default state
        assert proxy_widget.use_sysem_proxy_radio.isChecked() is True
        assert proxy_widget.http_edit.text() == ''
        assert proxy_widget.https_edit.text() == ''
        assert proxy_widget.username_edit.text() == ''
        assert proxy_widget.password_edit.text() == ''

    @patch.object(ProxyWidget, 'load')
    @patch('openlp.core.widgets.widgets.Settings')
    def test_proxy_widget_save_no_proxy_settings(self, settings_patcher, proxy_widget_load_patcher):
        """
        Test that the settings are saved correctly
        """
        # GIVEN: A Mocked settings instance of the proxy widget with some known values set
        settings_instance = MagicMock()
        settings_patcher.return_value = settings_instance
        proxy_widget = ProxyWidget()
        proxy_widget.no_proxy_radio.setChecked(True)
        proxy_widget.http_edit.setText('')
        proxy_widget.https_edit.setText('')
        proxy_widget.username_edit.setText('')
        proxy_widget.password_edit.setText('')

        # WHEN: Calling save
        proxy_widget.save()

        # THEN: The settings should be set as expected
        settings_instance.setValue.assert_has_calls(
            [call('advanced/proxy mode', ProxyMode.NO_PROXY),
             call('advanced/proxy http', ''),
             call('advanced/proxy https', ''),
             call('advanced/proxy username', ''),
             call('advanced/proxy password', '')])

    @patch.object(ProxyWidget, 'load')
    @patch('openlp.core.widgets.widgets.Settings')
    def test_proxy_widget_save_manual_settings(self, settings_patcher, proxy_widget_load_patcher):
        """
        Test that the settings are saved correctly
        """
        # GIVEN: A Mocked and instance of the proxy widget with some known values set
        settings_instance = MagicMock()
        settings_patcher.return_value = settings_instance
        proxy_widget = ProxyWidget()
        proxy_widget.manual_proxy_radio.setChecked(True)
        proxy_widget.http_edit.setText('http_proxy_server:port')
        proxy_widget.https_edit.setText('https_proxy_server:port')
        proxy_widget.username_edit.setText('username')
        proxy_widget.password_edit.setText('password')

        # WHEN: Calling save
        proxy_widget.save()

        # THEN: The settings should be set as expected
        settings_instance.setValue.assert_has_calls(
            [call('advanced/proxy mode', ProxyMode.MANUAL_PROXY),
             call('advanced/proxy http', 'http_proxy_server:port'),
             call('advanced/proxy https', 'https_proxy_server:port'),
             call('advanced/proxy username', 'username'),
             call('advanced/proxy password', 'password')])
