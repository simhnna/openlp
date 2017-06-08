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

from openlp.core.api.http import register_endpoint
from openlp.core.common import AppLocation, Registry, OpenLPMixin, check_directory_exists
from openlp.core.lib import Plugin, StringContent, translate, build_icon
from openlp.plugins.remotes.endpoint import remote_endpoint
from openlp.plugins.remotes.deploy import download_and_check

log = logging.getLogger(__name__)


class RemotesPlugin(Plugin, OpenLPMixin):
    log.info('Remotes Plugin loaded')

    def __init__(self):
        """
        remotes constructor
        """
        super(RemotesPlugin, self).__init__('remotes', {})
        self.icon_path = ':/plugins/plugin_remote.png'
        self.icon = build_icon(self.icon_path)
        self.weight = -1
        register_endpoint(remote_endpoint)
        Registry().register_function('download_website', self.first_time)

    def initialise(self):
        """
        Create the internal file structure if it does not exist
        :return:
        """
        check_directory_exists(os.path.join(AppLocation.get_section_data_path('remotes'), 'assets'))
        check_directory_exists(os.path.join(AppLocation.get_section_data_path('remotes'), 'images'))
        check_directory_exists(os.path.join(AppLocation.get_section_data_path('remotes'), 'static'))
        check_directory_exists(os.path.join(AppLocation.get_section_data_path('remotes'), 'templates'))

    @staticmethod
    def about():
        """
        Information about this plugin
        """
        about_text = translate('RemotePlugin', '<strong>Web Interface</strong>'
                                               '<br />The web interface plugin provides the ability develop web based '
                                               'interfaces using openlp web services. \nPredefined interfaces can be '
                                               'download as well as custom developed interfaces')
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
        download_and_check()
        self.application.process_events()
