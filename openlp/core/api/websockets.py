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
The :mod:`http` module contains the API web server. This is a lightweight web server used by remotes to interact
with OpenLP. It uses JSON to communicate with the remotes.
"""
import asyncio
import json
import logging
import time

from websockets import serve

from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.threading import ThreadWorker, run_thread

log = logging.getLogger(__name__)


async def handle_websocket(request, path):
    """
    Handle web socket requests and return the poll information.
    Check ever 0.2 seconds to get the latest position and send if changed.
    Only gets triggered when 1st client attaches

    :param request: request from client
    :param path: determines the endpoints supported
    :return:
    """
    log.debug('WebSocket handler registered with client')
    previous_poll = None
    previous_main_poll = None
    poller = Registry().get('poller')
    if path == '/state':
        while True:
            current_poll = poller.poll()
            if current_poll != previous_poll:
                await request.send(json.dumps(current_poll).encode())
                previous_poll = current_poll
            await asyncio.sleep(0.2)
    elif path == '/live_changed':
        while True:
            main_poll = poller.main_poll()
            if main_poll != previous_main_poll:
                await request.send(main_poll)
                previous_main_poll = main_poll
            await asyncio.sleep(0.2)


class WebSocketWorker(ThreadWorker, RegistryProperties, LogMixin):
    """
    A special Qt thread class to allow the WebSockets server to run at the same time as the UI.
    """
    def start(self):
        """
        Run the worker.
        """
        address = Settings().value('api/ip address')
        port = Settings().value('api/websocket port')
        # Start the event loop
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        # Create the websocker server
        loop = 1
        self.server = None
        while not self.server:
            try:
                self.server = serve(handle_websocket, address, port)
                log.debug('WebSocket server started on {addr}:{port}'.format(addr=address, port=port))
            except Exception as e:
                log.exception('Failed to start WebSocket server')
                loop += 1
                time.sleep(0.1)
            if not self.server and loop > 3:
                log.error('Unable to start WebSocket server {addr}:{port}, giving up'.format(addr=address, port=port))
        if self.server:
            # If the websocket server exists, start listening
            event_loop.run_until_complete(self.server)
            event_loop.run_forever()
        self.quit.emit()

    def stop(self):
        """
        Stop the websocket server
        """
        if hasattr(self.server, 'ws_server'):
            self.server.ws_server.close()
        elif hasattr(self.server, 'server'):
            self.server.server.close()


class WebSocketServer(RegistryProperties, LogMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self):
        """
        Initialise and start the WebSockets server
        """
        super(WebSocketServer, self).__init__()
        if Registry().get_flag('no_web_server'):
            worker = WebSocketWorker()
            run_thread(worker, 'websocket_server')
