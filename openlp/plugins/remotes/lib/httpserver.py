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

import asyncio
import ssl
import socket
import websockets
import os
import logging
import time

from PyQt5 import QtCore

from openlp.core.common import AppLocation, Settings, RegistryProperties, OpenLPMixin

from openlp.plugins.remotes.lib import HttpRouter, OpenLPPoll

from socketserver import BaseServer, ThreadingMixIn
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
    def __init__(self, websocket=False, secure=False):
        """
        Initialise the http server, and start the server of the correct type http / https
        """
        super(OpenLPServer, self).__init__()
        self.settings_section = 'remotes'
        self.secure = secure
        self.websocket = websocket
        self.http_thread = HttpThread(self)
        self.http_thread.start()

    def start_server(self):
        """
        Start the correct server and save the handler
        """
        address = Settings().value(self.settings_section + '/ip address')
        is_secure = Settings().value(self.settings_section + '/https enabled')
        # Try to start secure server but not enabled.
        if self.secure and not is_secure:
            return
        if self.secure:
            port = Settings().value(self.settings_section + '/https port')
        else:
            port = Settings().value(self.settings_section + '/port')
        if self.secure:
            self.start_server_instance(address, port, HTTPSServer)
        else:
            if self.websocket:
                self.start_websocket_instance(address, port)
            else:
                self.start_server_instance(address, port, ThreadingHTTPServer)
        # If HTTP server start listening
        if hasattr(self, 'httpd') and self.httpd:
            self.httpd.serve_forever()
        else:
            log.debug('Failed to start http server on port {port}'.format(port=port))
        # If web socket server start listening
        if hasattr(self, 'ws_server') and self.ws_server:
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            event_loop.run_until_complete(self.ws_server)
            event_loop.run_forever()
        else:
            log.debug('Failed to start ws server on port {port}'.format(port=port))

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

    def start_websocket_instance(self, address, port):
        """
        Start the server

        :param address: The server address
        :param port: The run port
        """
        loop = 1
        while loop < 4:
            try:
                self.ws_server = websockets.serve(self.handle_websocket, address, '4318')
                log.debug("Web Socket Server started for class {address} {port:d}".format(address=address, port=port))
                break
            except Exception as e:
                log.error('Failed to start ws server {why}'.format(why=e))
                loop += 1
                time.sleep(0.1)

    @staticmethod
    async def handle_websocket(request, path):
        """
        Handle web socket requests and return the poll information.
        Check ever 0.5 seconds to get the latest postion and send if changed.
        Only gets triggered when 1st client attaches
        :param request: request from client
        :param path: not used - future to register for a different end point
        :return:
        """
        log.debug("web socket handler registered with client")
        previous_poll = None
        if path == '/poll':
            while True:
                current_poll = OpenLPPoll().poll()
                if current_poll != previous_poll:
                    await request.send(current_poll)
                    previous_poll = current_poll
                await asyncio.sleep(0.2)

    def stop_server(self):
        """
        Stop the server
        """
        if self.http_thread.isRunning():
            self.http_thread.stop()
        self.httpd = None
        log.debug('Stopped the server.')


class HTTPSServer(HTTPServer):
    def __init__(self, address, handler):
        """
        Initialise the secure handlers for the SSL server if required.s
        """
        BaseServer.__init__(self, address, handler)
        self.socket = ssl.SSLSocket(
            sock=socket.socket(self.address_family, self.socket_type),
            certfile=get_cert_file('crt'),
            keyfile=get_cert_file('key'),
            server_side=True)
        self.server_bind()
        self.server_activate()


def get_cert_file(file_type):
    """
    Helper method to get certificate files
    :param file_type: file suffix key, cert or pem
    :return: full path to file
    """
    local_data = AppLocation.get_directory(AppLocation.DataDir)
    return os.path.join(local_data, 'remotes', 'openlp.{type}'.format(type=file_type))
