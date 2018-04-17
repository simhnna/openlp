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
The :mod:`~openlp.core.api.tab` module contains the settings tab for the API
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import get_local_ip4
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import SettingsTab
from openlp.core.ui.icons import UiIcons

ZERO_URL = '0.0.0.0'


class ApiTab(SettingsTab):
    """
    RemoteTab is the Remotes settings tab in the settings dialog.
    """
    def __init__(self, parent):
        self.icon_path = UiIcons().remote
        advanced_translated = translate('OpenLP.AdvancedTab', 'Advanced')
        super(ApiTab, self).__init__(parent, 'api', advanced_translated)

    def setupUi(self):
        self.setObjectName('ApiTab')
        super(ApiTab, self).setupUi()
        self.server_settings_group_box = QtWidgets.QGroupBox(self.left_column)
        self.server_settings_group_box.setObjectName('server_settings_group_box')
        self.server_settings_layout = QtWidgets.QFormLayout(self.server_settings_group_box)
        self.server_settings_layout.setObjectName('server_settings_layout')
        self.address_label = QtWidgets.QLabel(self.server_settings_group_box)
        self.address_label.setObjectName('address_label')
        self.address_edit = QtWidgets.QLineEdit(self.server_settings_group_box)
        self.address_edit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.address_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
                                       self))
        self.address_edit.setObjectName('address_edit')
        self.server_settings_layout.addRow(self.address_label, self.address_edit)
        self.twelve_hour_check_box = QtWidgets.QCheckBox(self.server_settings_group_box)
        self.twelve_hour_check_box.setObjectName('twelve_hour_check_box')
        self.server_settings_layout.addRow(self.twelve_hour_check_box)
        self.thumbnails_check_box = QtWidgets.QCheckBox(self.server_settings_group_box)
        self.thumbnails_check_box.setObjectName('thumbnails_check_box')
        self.server_settings_layout.addRow(self.thumbnails_check_box)
        self.left_layout.addWidget(self.server_settings_group_box)
        self.http_settings_group_box = QtWidgets.QGroupBox(self.left_column)
        self.http_settings_group_box.setObjectName('http_settings_group_box')
        self.http_setting_layout = QtWidgets.QFormLayout(self.http_settings_group_box)
        self.http_setting_layout.setObjectName('http_setting_layout')
        self.port_label = QtWidgets.QLabel(self.http_settings_group_box)
        self.port_label.setObjectName('port_label')
        self.port_spin_box = QtWidgets.QLabel(self.http_settings_group_box)
        self.port_spin_box.setObjectName('port_spin_box')
        self.http_setting_layout.addRow(self.port_label, self.port_spin_box)
        self.remote_url_label = QtWidgets.QLabel(self.http_settings_group_box)
        self.remote_url_label.setObjectName('remote_url_label')
        self.remote_url = QtWidgets.QLabel(self.http_settings_group_box)
        self.remote_url.setObjectName('remote_url')
        self.remote_url.setOpenExternalLinks(True)
        self.http_setting_layout.addRow(self.remote_url_label, self.remote_url)
        self.stage_url_label = QtWidgets.QLabel(self.http_settings_group_box)
        self.stage_url_label.setObjectName('stage_url_label')
        self.stage_url = QtWidgets.QLabel(self.http_settings_group_box)
        self.stage_url.setObjectName('stage_url')
        self.stage_url.setOpenExternalLinks(True)
        self.http_setting_layout.addRow(self.stage_url_label, self.stage_url)
        self.chords_url_label = QtWidgets.QLabel(self.http_settings_group_box)
        self.chords_url_label.setObjectName('chords_url_label')
        self.chords_url = QtWidgets.QLabel(self.http_settings_group_box)
        self.chords_url.setObjectName('chords_url')
        self.chords_url.setOpenExternalLinks(True)
        self.http_setting_layout.addRow(self.chords_url_label, self.chords_url)
        self.live_url_label = QtWidgets.QLabel(self.http_settings_group_box)
        self.live_url_label.setObjectName('live_url_label')
        self.live_url = QtWidgets.QLabel(self.http_settings_group_box)
        self.live_url.setObjectName('live_url')
        self.live_url.setOpenExternalLinks(True)
        self.http_setting_layout.addRow(self.live_url_label, self.live_url)
        self.left_layout.addWidget(self.http_settings_group_box)
        self.user_login_group_box = QtWidgets.QGroupBox(self.left_column)
        self.user_login_group_box.setCheckable(True)
        self.user_login_group_box.setChecked(False)
        self.user_login_group_box.setObjectName('user_login_group_box')
        self.user_login_layout = QtWidgets.QFormLayout(self.user_login_group_box)
        self.user_login_layout.setObjectName('user_login_layout')
        self.user_id_label = QtWidgets.QLabel(self.user_login_group_box)
        self.user_id_label.setObjectName('user_id_label')
        self.user_id = QtWidgets.QLineEdit(self.user_login_group_box)
        self.user_id.setObjectName('user_id')
        self.user_login_layout.addRow(self.user_id_label, self.user_id)
        self.password_label = QtWidgets.QLabel(self.user_login_group_box)
        self.password_label.setObjectName('password_label')
        self.password = QtWidgets.QLineEdit(self.user_login_group_box)
        self.password.setObjectName('password')
        self.user_login_layout.addRow(self.password_label, self.password)
        self.left_layout.addWidget(self.user_login_group_box)
        self.update_site_group_box = QtWidgets.QGroupBox(self.left_column)
        self.update_site_group_box.setCheckable(True)
        self.update_site_group_box.setChecked(False)
        self.update_site_group_box.setObjectName('update_site_group_box')
        self.update_site_layout = QtWidgets.QFormLayout(self.update_site_group_box)
        self.update_site_layout.setObjectName('update_site_layout')
        self.current_version_label = QtWidgets.QLabel(self.update_site_group_box)
        self.current_version_label.setObjectName('current_version_label')
        self.current_version_value = QtWidgets.QLabel(self.update_site_group_box)
        self.current_version_value.setObjectName('current_version_value')
        self.update_site_layout.addRow(self.current_version_label, self.current_version_value)
        self.master_version_label = QtWidgets.QLabel(self.update_site_group_box)
        self.master_version_label.setObjectName('master_version_label')
        self.master_version_value = QtWidgets.QLabel(self.update_site_group_box)
        self.master_version_value.setObjectName('master_version_value')
        self.update_site_layout.addRow(self.master_version_label, self.master_version_value)
        self.left_layout.addWidget(self.update_site_group_box)
        self.app_group_box = QtWidgets.QGroupBox(self.right_column)
        self.app_group_box.setObjectName('app_group_box')
        self.right_layout.addWidget(self.app_group_box)
        self.app_qr_layout = QtWidgets.QVBoxLayout(self.app_group_box)
        self.app_qr_layout.setObjectName('app_qr_layout')
        self.app_qr_code_label = QtWidgets.QLabel(self.app_group_box)
        self.app_qr_code_label.setPixmap(QtGui.QPixmap(':/remotes/app_qr.svg'))
        self.app_qr_code_label.setAlignment(QtCore.Qt.AlignCenter)
        self.app_qr_code_label.setObjectName('app_qr_code_label')
        self.app_qr_layout.addWidget(self.app_qr_code_label)
        self.app_qr_description_label = QtWidgets.QLabel(self.app_group_box)
        self.app_qr_description_label.setObjectName('app_qr_description_label')
        self.app_qr_description_label.setOpenExternalLinks(True)
        self.app_qr_description_label.setWordWrap(True)
        self.app_qr_layout.addWidget(self.app_qr_description_label)
        self.left_layout.addStretch()
        self.right_layout.addStretch()
        self.twelve_hour_check_box.stateChanged.connect(self.on_twelve_hour_check_box_changed)
        self.thumbnails_check_box.stateChanged.connect(self.on_thumbnails_check_box_changed)
        self.address_edit.textChanged.connect(self.set_urls)

    def retranslateUi(self):
        self.tab_title_visible = translate('RemotePlugin.RemoteTab', 'Remote Interface')
        self.server_settings_group_box.setTitle(translate('RemotePlugin.RemoteTab', 'Server Settings'))
        self.address_label.setText(translate('RemotePlugin.RemoteTab', 'Serve on IP address:'))
        self.port_label.setText(translate('RemotePlugin.RemoteTab', 'Port number:'))
        self.remote_url_label.setText(translate('RemotePlugin.RemoteTab', 'Remote URL:'))
        self.stage_url_label.setText(translate('RemotePlugin.RemoteTab', 'Stage view URL:'))
        self.live_url_label.setText(translate('RemotePlugin.RemoteTab', 'Live view URL:'))
        self.chords_url_label.setText(translate('RemotePlugin.RemoteTab', 'Chords view URL:'))
        self.twelve_hour_check_box.setText(translate('RemotePlugin.RemoteTab', 'Display stage time in 12h format'))
        self.thumbnails_check_box.setText(translate('RemotePlugin.RemoteTab',
                                                    'Show thumbnails of non-text slides in remote and stage view.'))
        self.app_group_box.setTitle(translate('RemotePlugin.RemoteTab', 'Remote App'))
        self.app_qr_description_label.setText(
            translate('RemotePlugin.RemoteTab',
                      'Scan the QR code or click <a href="{qr}">download</a> to download an app for your mobile device'
                      ).format(qr='https://openlp.org/#mobile-app-downloads'))
        self.user_login_group_box.setTitle(translate('RemotePlugin.RemoteTab', 'User Authentication'))
        self.aa = UiStrings()
        self.update_site_group_box.setTitle(UiStrings().WebDownloadText)
        self.user_id_label.setText(translate('RemotePlugin.RemoteTab', 'User id:'))
        self.password_label.setText(translate('RemotePlugin.RemoteTab', 'Password:'))
        self.current_version_label.setText(translate('RemotePlugin.RemoteTab', 'Current Version number:'))
        self.master_version_label.setText(translate('RemotePlugin.RemoteTab', 'Latest Version number:'))

    def set_urls(self):
        """
        Update the display based on the data input on the screen
        """
        ip_address = self.get_ip_address(self.address_edit.text())
        http_url = 'http://{url}:{text}/'.format(url=ip_address, text=self.port_spin_box.text())
        self.remote_url.setText('<a href="{url}">{url}</a>'.format(url=http_url))
        http_url_temp = http_url + 'stage'
        self.stage_url.setText('<a href="{url}">{url}</a>'.format(url=http_url_temp))
        http_url_temp = http_url + 'chords'
        self.chords_url.setText('<a href="{url}">{url}</a>'.format(url=http_url_temp))
        http_url_temp = http_url + 'main'
        self.live_url.setText('<a href="{url}">{url}</a>'.format(url=http_url_temp))

    @staticmethod
    def get_ip_address(ip_address):
        """
        returns the IP address in dependency of the passed address
        ip_address == 0.0.0.0: return the IP address of the first valid interface
        else: return ip_address
        """
        if ip_address == ZERO_URL:
            # In case we have more than one interface
            ifaces = get_local_ip4()
            for key in iter(ifaces):
                ip_address = ifaces.get(key)['ip']
                # We only want the first interface returned
                break
        return ip_address

    def load(self):
        """
        Load the configuration and update the server configuration if necessary
        """
        self.port_spin_box.setText(str(Settings().value(self.settings_section + '/port')))
        self.address_edit.setText(Settings().value(self.settings_section + '/ip address'))
        self.twelve_hour = Settings().value(self.settings_section + '/twelve hour')
        self.twelve_hour_check_box.setChecked(self.twelve_hour)
        self.thumbnails = Settings().value(self.settings_section + '/thumbnails')
        self.thumbnails_check_box.setChecked(self.thumbnails)
        self.user_login_group_box.setChecked(Settings().value(self.settings_section + '/authentication enabled'))
        self.user_id.setText(Settings().value(self.settings_section + '/user id'))
        self.password.setText(Settings().value(self.settings_section + '/password'))
        self.current_version_value.setText(Settings().value('remotes/download version'))
        self.master_version_value.setText(Registry().get_flag('website_version'))
        if self.master_version_value.text() == self.current_version_value.text():
            self.update_site_group_box.setEnabled(False)
        self.set_urls()

    def save(self):
        """
        Save the configuration and update the server configuration if necessary
        """
        if Settings().value(self.settings_section + '/ip address') != self.address_edit.text():
            self.settings_form.register_post_process('remotes_config_updated')
        Settings().setValue(self.settings_section + '/ip address', self.address_edit.text())
        Settings().setValue(self.settings_section + '/twelve hour', self.twelve_hour)
        Settings().setValue(self.settings_section + '/thumbnails', self.thumbnails)
        Settings().setValue(self.settings_section + '/authentication enabled', self.user_login_group_box.isChecked())
        Settings().setValue(self.settings_section + '/user id', self.user_id.text())
        Settings().setValue(self.settings_section + '/password', self.password.text())
        self.generate_icon()
        if self.update_site_group_box.isChecked():
            self.settings_form.register_post_process('download_website')

    def on_twelve_hour_check_box_changed(self, check_state):
        """
        Toggle the 12 hour check box.
        """
        self.twelve_hour = False
        # we have a set value convert to True/False
        if check_state == QtCore.Qt.Checked:
            self.twelve_hour = True

    def on_thumbnails_check_box_changed(self, check_state):
        """
        Toggle the thumbnail check box.
        """
        self.thumbnails = False
        # we have a set value convert to True/False
        if check_state == QtCore.Qt.Checked:
            self.thumbnails = True
