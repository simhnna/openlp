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
import logging

from openlp.core.api.http import register_endpoint
from openlp.core.api.http.server import HttpServer
from openlp.core.api.http.endpoint.controller import controller_endpoint, api_controller_endpoint
from openlp.core.api.http.endpoint.core import stage_endpoint, blank_endpoint, main_endpoint
from openlp.core.api.http.endpoint.service import service_endpoint, api_service_endpoint
from openlp.core.api.websockets import WebSocketServer
from openlp.core.api.poll import Poller
from openlp.core.common import OpenLPMixin, Registry, RegistryMixin, RegistryProperties

log = logging.getLogger(__name__)


class ApiController(RegistryMixin, OpenLPMixin, RegistryProperties):
    """
    The APIController handles the starting of the API middleware.
    The HTTP and Websocket servers are started
    The core endpoints are generated (just by their declaration).
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ApiController, self).__init__(parent)
        register_endpoint(controller_endpoint)
        register_endpoint(api_controller_endpoint)
        register_endpoint(stage_endpoint)
        register_endpoint(blank_endpoint)
        register_endpoint(main_endpoint)
        register_endpoint(service_endpoint)
        register_endpoint(api_service_endpoint)

    def bootstrap_post_set_up(self):
        """
        Register the poll return service and start the servers.
        """
        self.poller = Poller()
        Registry().register('poller', self.poller)
        self.ws_server = WebSocketServer()
        self.http_server = HttpServer()
