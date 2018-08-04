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
The :mod:`~openlp.core.widgets.widgets` module contains custom widgets used in OpenLP
"""
from PyQt5 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.settings import ProxyMode, Settings


class ProxyWidget(QtWidgets.QGroupBox):
    """
    A proxy settings widget that implements loading and saving its settings.
    """
    def __init__(self, parent=None):
        """
        Initialise the widget.

        :param QtWidgets.QWidget | None parent: The widgets parent
        """
        super().__init__(parent)
        self._setup()

    def _setup(self):
        """
        A setup method seperate from __init__ to allow easier testing
        """
        self.setup_ui()
        self.load()

    def setup_ui(self):
        """
        Create the widget layout and sub widgets
        """
        self.layout = QtWidgets.QFormLayout(self)
        self.radio_group = QtWidgets.QButtonGroup(self)
        self.no_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.no_proxy_radio, ProxyMode.NO_PROXY)
        self.layout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.no_proxy_radio)
        self.use_sysem_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.use_sysem_proxy_radio, ProxyMode.SYSTEM_PROXY)
        self.layout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.use_sysem_proxy_radio)
        self.manual_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.manual_proxy_radio, ProxyMode.MANUAL_PROXY)
        self.layout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.manual_proxy_radio)
        self.http_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('HTTP:', self.http_edit)
        self.https_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('HTTPS:', self.https_edit)
        self.username_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('Username:', self.username_edit)
        self.password_edit = QtWidgets.QLineEdit(self)
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.layout.addRow('Password:', self.password_edit)
        # Signal / Slots
        self.radio_group.buttonToggled.connect(self.on_radio_group_button_toggled)

    def on_radio_group_button_toggled(self, button, checked):
        """
        Handles the toggled signal on the radio buttons. The signal is emitted twice if a radio butting being toggled on
        causes another radio button in the group to be toggled off.

        En/Disables the `Manual Proxy` line edits depending on the currently selected radio button

        :param QtWidgets.QRadioButton button: The button that has toggled
        :param bool checked: The buttons new state
        """
        id = self.radio_group.id(button)  # The work around (see above comment)
        enable_manual_edits = id == ProxyMode.MANUAL_PROXY and checked
        self.http_edit.setEnabled(enable_manual_edits)
        self.https_edit.setEnabled(enable_manual_edits)
        self.username_edit.setEnabled(enable_manual_edits)
        self.password_edit.setEnabled(enable_manual_edits)

    def retranslate_ui(self):
        """
        Translate the Ui
        """
        self.setTitle(translate('OpenLP.ProxyWidget', 'Proxy Server Settings'))
        self.no_proxy_radio.setText(translate('OpenLP.ProxyWidget', 'No prox&y'))
        self.use_sysem_proxy_radio.setText(translate('OpenLP.ProxyWidget', '&Use system proxy'))
        self.manual_proxy_radio.setText(translate('OpenLP.ProxyWidget', '&Manual proxy configuration'))
        proxy_example = translate('OpenLP.ProxyWidget', 'e.g. proxy_server_address:port_no')
        self.layout.labelForField(self.http_edit).setText(translate('OpenLP.ProxyWidget', 'HTTP:'))
        self.http_edit.setPlaceholderText(proxy_example)
        self.layout.labelForField(self.https_edit).setText(translate('OpenLP.ProxyWidget', 'HTTPS:'))
        self.https_edit.setPlaceholderText(proxy_example)
        self.layout.labelForField(self.username_edit).setText(translate('OpenLP.ProxyWidget', 'Username:'))
        self.layout.labelForField(self.password_edit).setText(translate('OpenLP.ProxyWidget', 'Password:'))

    def load(self):
        """
        Load the data from the settings to the widget.
        """
        settings = Settings()
        checked_radio = self.radio_group.button(settings.value('advanced/proxy mode'))
        checked_radio.setChecked(True)
        self.http_edit.setText(settings.value('advanced/proxy http'))
        self.https_edit.setText(settings.value('advanced/proxy https'))
        self.username_edit.setText(settings.value('advanced/proxy username'))
        self.password_edit.setText(settings.value('advanced/proxy password'))

    def save(self):
        """
        Save the widget data to the settings
        """
        settings = Settings()  # TODO: Migrate from old system
        settings.setValue('advanced/proxy mode', self.radio_group.checkedId())
        settings.setValue('advanced/proxy http', self.http_edit.text())
        settings.setValue('advanced/proxy https', self.https_edit.text())
        settings.setValue('advanced/proxy username', self.username_edit.text())
        settings.setValue('advanced/proxy password', self.password_edit.text())
