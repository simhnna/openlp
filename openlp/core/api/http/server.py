# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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

from PyQt5 import QtCore
from waitress import serve

from openlp.core.api.http import register_endpoint
from openlp.core.api.http import application
from openlp.core.common import RegistryMixin, RegistryProperties, OpenLPMixin, Settings, Registry
from openlp.core.api.poll import Poller
from openlp.core.api.endpoint.controller import controller_endpoint, api_controller_endpoint
from openlp.core.api.endpoint.core import stage_endpoint, blank_endpoint, main_endpoint
from openlp.core.api.endpoint.service import service_endpoint, api_service_endpoint

log = logging.getLogger(__name__)


class HttpWorker(QtCore.QObject):
    """
    A special Qt thread class to allow the HTTP server to run at the same time as the UI.
    """
    def __init__(self):
        """
        Constructor for the thread class.

        :param server: The http server class.
        """
        super(HttpWorker, self).__init__()

    def run(self):
        """
        Run the thread.
        """
        address = Settings().value('api/ip address')
        port = Settings().value('api/port')
        serve(application, host=address, port=port)

    def stop(self):
        pass


class HttpServer(RegistryMixin, RegistryProperties, OpenLPMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self, parent=None):
        """
        Initialise the http server, and start the http server
        """
        super(HttpServer, self).__init__(parent)
        self.worker = HttpWorker()
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def bootstrap_post_set_up(self):
        """
        Register the poll return service and start the servers.
        """
        self.poller = Poller()
        Registry().register('poller', self.poller)
        register_endpoint(controller_endpoint)
        register_endpoint(api_controller_endpoint)
        register_endpoint(stage_endpoint)
        register_endpoint(blank_endpoint)
        register_endpoint(main_endpoint)
        register_endpoint(service_endpoint)
        register_endpoint(api_service_endpoint)
