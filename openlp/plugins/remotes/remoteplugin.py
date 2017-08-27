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

import logging
import os
import time

from PyQt5 import QtCore, QtWidgets

from openlp.core.api.http import register_endpoint
from openlp.core.common import AppLocation, Registry, Settings, OpenLPMixin, UiStrings, check_directory_exists
from openlp.core.lib import Plugin, StringContent, translate, build_icon
from openlp.plugins.remotes.endpoint import remote_endpoint
from openlp.plugins.remotes.deploy import download_and_check, download_sha256

log = logging.getLogger(__name__)
__default_settings__ = {
    'remotes/download version': '0000_00_00'
}


class RemotesPlugin(Plugin, OpenLPMixin):
    log.info('Remotes Plugin loaded')

    def __init__(self):
        """
        remotes constructor
        """
        super(RemotesPlugin, self).__init__('remotes', __default_settings__, {})
        self.icon_path = ':/plugins/plugin_remote.png'
        self.icon = build_icon(self.icon_path)
        self.weight = -1
        register_endpoint(remote_endpoint)
        Registry().register_function('download_website', self.first_time)
        Registry().register_function('get_website_version', self.website_version)
        Registry().set_flag('website_version', '0001_01_01')

    def initialise(self):
        """
        Create the internal file structure if it does not exist
        :return:
        """
        check_directory_exists(AppLocation.get_section_data_path('remotes') / 'assets')
        check_directory_exists(AppLocation.get_section_data_path('remotes') / 'images')
        check_directory_exists(AppLocation.get_section_data_path('remotes') / 'static')
        check_directory_exists(AppLocation.get_section_data_path('remotes') / 'static', 'index')
        check_directory_exists(AppLocation.get_section_data_path('remotes') / 'templates')

    @staticmethod
    def about():
        """
        Information about this plugin
        """
        about_text = translate(
            'RemotePlugin',
            '<strong>Web Interface</strong>'
            '<br />The web interface plugin provides the ability to develop web based interfaces using OpenLP web '
            'services.\nPredefined interfaces can be download as well as custom developed interfaces.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('RemotePlugin', 'Web Interface', 'name singular'),
            'plural': translate('RemotePlugin', 'Web Interface', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('RemotePlugin', 'Web Remote', 'container title')
        }

    def first_time(self):
        """
        Import web site code if active
        """
        self.application.process_events()
        progress = Progress(self)
        progress.forceShow()
        self.application.process_events()
        time.sleep(1)
        download_and_check(progress)
        self.application.process_events()
        time.sleep(1)
        progress.close()
        self.application.process_events()
        Settings().setValue('remotes/download version', self.version)

    def website_version(self):
        """
        Download and save the website version and sha256
        :return: None
        """
        sha256, self.version = download_sha256()
        Registry().set_flag('website_sha256', sha256)
        Registry().set_flag('website_version', self.version)


class Progress(QtWidgets.QProgressDialog):
    """
    Local class to handle download display based and supporting httputils:get_web_page
    """
    def __init__(self, parent):
        super(Progress, self).__init__(parent.main_window)
        self.parent = parent
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowTitle(translate('RemotePlugin', 'Importing Website'))
        self.setLabelText(UiStrings().StartingImport)
        self.setCancelButton(None)
        self.setRange(0, 1)
        self.setMinimumDuration(0)
        self.was_cancelled = False
        self.previous_size = 0

    def _download_progress(self, count, block_size):
        """
        Calculate and display the download progress.
        """
        increment = (count * block_size) - self.previous_size
        self._increment_progress_bar(None, increment)
        self.previous_size = count * block_size

    def _increment_progress_bar(self, status_text, increment=1):
        """
        Update the wizard progress page.

        :param status_text: Current status information to display.
        :param increment: The value to increment the progress bar by.
        """
        if status_text:
            self.setText(status_text)
        if increment > 0:
            self.setValue(self.value() + increment)
        self.parent.application.process_events()
