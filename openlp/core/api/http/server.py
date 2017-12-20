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
The :mod:`http` module contains the API web server. This is a lightweight web server used by remotes to interact
with OpenLP. It uses JSON to communicate with the remotes.
"""
import logging
import time

from PyQt5 import QtCore, QtWidgets
from waitress import serve

from openlp.core.api.deploy import download_and_check, download_sha256
from openlp.core.api.endpoint.controller import controller_endpoint, api_controller_endpoint
from openlp.core.api.endpoint.core import chords_endpoint, stage_endpoint, blank_endpoint, main_endpoint
from openlp.core.api.endpoint.service import service_endpoint, api_service_endpoint
from openlp.core.api.endpoint.remote import remote_endpoint
from openlp.core.api.http import register_endpoint
from openlp.core.api.http import application
from openlp.core.api.poll import Poller
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import UiStrings
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.path import create_paths
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.common.settings import Settings
from openlp.core.threading import ThreadWorker, run_thread

log = logging.getLogger(__name__)


class HttpWorker(ThreadWorker):
    """
    A special Qt thread class to allow the HTTP server to run at the same time as the UI.
    """
    def start(self):
        """
        Run the thread.
        """
        address = Settings().value('api/ip address')
        port = Settings().value('api/port')
        Registry().execute('get_website_version')
        try:
            serve(application, host=address, port=port)
        except OSError:
            log.exception('An error occurred when serving the application.')
        self.quit.emit()


class HttpServer(RegistryBase, RegistryProperties, LogMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self, parent=None):
        """
        Initialise the http server, and start the http server
        """
        super(HttpServer, self).__init__(parent)
        if Registry().get_flag('no_web_server'):
            worker = HttpWorker()
            run_thread(worker, 'http_server')
            Registry().register_function('download_website', self.first_time)
            Registry().register_function('get_website_version', self.website_version)
        Registry().set_flag('website_version', '0.0')

    def bootstrap_post_set_up(self):
        """
        Register the poll return service and start the servers.
        """
        self.initialise()
        self.poller = Poller()
        Registry().register('poller', self.poller)
        application.initialise()
        register_endpoint(controller_endpoint)
        register_endpoint(api_controller_endpoint)
        register_endpoint(chords_endpoint)
        register_endpoint(stage_endpoint)
        register_endpoint(blank_endpoint)
        register_endpoint(main_endpoint)
        register_endpoint(service_endpoint)
        register_endpoint(api_service_endpoint)
        register_endpoint(remote_endpoint)

    @staticmethod
    def initialise():
        """
        Create the internal file structure if it does not exist
        :return:
        """
        create_paths(AppLocation.get_section_data_path('remotes') / 'assets',
                     AppLocation.get_section_data_path('remotes') / 'images',
                     AppLocation.get_section_data_path('remotes') / 'static',
                     AppLocation.get_section_data_path('remotes') / 'static' / 'index',
                     AppLocation.get_section_data_path('remotes') / 'templates')

    def first_time(self):
        """
        Import web site code if active
        """
        self.application.process_events()
        progress = DownloadProgressDialog(self)
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


class DownloadProgressDialog(QtWidgets.QProgressDialog):
    """
    Local class to handle download display based and supporting httputils:get_web_page
    """
    def __init__(self, parent):
        super(DownloadProgressDialog, self).__init__(parent.main_window)
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
