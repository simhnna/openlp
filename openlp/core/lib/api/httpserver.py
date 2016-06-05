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
from waitress import serve

from PyQt5 import QtCore

from openlp.core.common import RegistryProperties, OpenLPMixin

log = logging.getLogger(__name__)


class HttpThread(QtCore.QThread):
    """
    A special Qt thread class to allow the HTTP server to run at the same time as the UI.
    """
    def __init__(self, server):
        """
        Constructor for the thread class.

        :param server: The http server class.
        """
        super(HttpThread, self).__init__(None)
        self.http_server = server

    def run(self):
        """
        Run the thread.
        """
        wsgiapp = object()
        serve(wsgiapp, host='0.0.0.0', port=4317)

    def stop(self):
        self.http_server.stop = True


class OpenLPHttpServer(RegistryProperties, OpenLPMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self, secure=False):
        """
        Initialise the http server, and start the server of the correct type http / https
        """
        super(OpenLPHttpServer, self).__init__()
        self.http_thread = HttpThread(self)
        self.http_thread.start()
