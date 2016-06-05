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
import time

from PyQt5 import QtCore

from openlp.core.common import Settings, RegistryProperties, OpenLPMixin

from openlp.plugins.remotes.lib import HttpRouter

from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

log = logging.getLogger(__name__)


class WebHandler(BaseHTTPRequestHandler, HttpRouter):
    """
    Stateless session handler to handle the HTTP request and process it.
    This class handles just the overrides to the base methods and the logic to invoke the methods within the HttpRouter
    class.
    DO not try change the structure as this is as per the documentation.
    """

    def do_POST(self):
        """
        Present pages / data and invoke URL level user authentication.
        """
        self.do_post_processor()

    def do_GET(self):
        """
        Present pages / data and invoke URL level user authentication.
        """
        self.do_post_processor()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


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
        self.http_server.start_server()

    def stop(self):
        self.http_server.stop = True


class OpenLPServer(RegistryProperties, OpenLPMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self, secure=False):
        """
        Initialise the http server, and start the server of the correct type http / https
        """
        super(OpenLPServer, self).__init__()
        self.settings_section = 'remotes'
        self.secure = secure
        self.http_thread = HttpThread(self)
        self.http_thread.start()

    def start_server(self):
        """
        Start the correct server and save the handler
        """
        address = Settings().value(self.settings_section + '/ip address')
        # Try to start secure server but not enabled.
        port = Settings().value(self.settings_section + '/port')
        self.start_server_instance(address, port, ThreadingHTTPServer)
        # If HTTP server start listening
        if hasattr(self, 'httpd') and self.httpd:
            self.httpd.serve_forever()
        else:
            log.debug('Failed to start http server on port {port}'.format(port=port))

    def start_server_instance(self, address, port, server_class):
        """
        Start the server

        :param address: The server address
        :param port: The run port
        :param server_class: the class to start
        """
        loop = 1
        while loop < 4:
            try:
                self.httpd = server_class((address, port), WebHandler)
                log.debug("Server started for class {name} {address} {port:d}".format(name=server_class,
                                                                                      address=address,
                                                                                      port=port))
                break
            except OSError:
                log.debug("failed to start http server thread state "
                          "{loop:d} {running}".format(loop=loop, running=self.http_thread.isRunning()))
                loop += 1
                time.sleep(0.1)
            except Exception as e:
                log.error('Failed to start http server {why}'.format(why=e))
                loop += 1
                time.sleep(0.1)

    def stop_server(self):
        """
        Stop the server
        """
        if self.http_thread.isRunning():
            self.http_thread.stop()
        self.httpd = None
        log.debug('Stopped the server.')
