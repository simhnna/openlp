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
from PyQt5 import QtCore, QtNetwork

from openlp.core.common.registry import Registry
from openlp.core.common.mixins import LogMixin


class Server(QtCore.QObject, LogMixin):
    """
    The local server to handle OpenLP running in more than one instance and allows file
    handles to be transferred from the new to the existing one.
    """
    def __init__(self):
        super(Server, self).__init__()
        self.out_socket = QtNetwork.QLocalSocket()
        self.server = None
        self.id = 'OpenLPDual'

    def is_another_instance_running(self):
        """
        Check the see if an other instance is running
        :return: True of False
        """
        # Is there another instance running?
        self.out_socket.connectToServer(self.id)
        return self.out_socket.waitForConnected()

    def post_to_server(self, args):
        """
        Post the file name to the over instance
        :param args: The passed arguments including maybe a file name
        """
        if 'OpenLP' in args:
            args.remove('OpenLP')
        # Yes, there is.
        self.out_stream = QtCore.QTextStream(self.out_socket)
        self.out_stream.setCodec('UTF-8')
        self.out_socket.write(str.encode("".join(args)))
        if not self.out_socket.waitForBytesWritten(10):
            raise Exception(str(self.out_socket.errorString()))
        self.out_socket.disconnectFromServer()

    def start_server(self):
        """
        Start the socket server to allow inter app communication
        :return:
        """
        self.out_socket = None
        self.out_stream = None
        self.in_socket = None
        self.in_stream = None
        self.server = QtNetwork.QLocalServer()
        self.server.listen(self._id)
        self.server.newConnection.connect(self._on_new_connection)
        return True

    def _on_new_connection(self):
        """
        Handle a new connection to the server
        :return:
        """
        if self.in_socket:
            self.in_socket.readyRead.disconnect(self._on_ready_read)
        self.in_socket = self.server.nextPendingConnection()
        if not self.in_socket:
            return
        self.in_stream = QtCore.QTextStream(self.in_socket)
        self.in_stream.setCodec('UTF-8')
        self.in_socket.readyRead.connect(self._on_ready_read)

    def _on_ready_read(self):
        """
        Read a record passed to the server and pass to the service manager to handle
        :return:
        """
        msg = self.in_stream.readLine()
        if msg:
            self.log_debug("socket msg = " + msg)
            Registry().get('service_manager').on_load_service_clicked(msg)

    def close_server(self):
        """
        Shutdown to local socket server and make sure the server is removed.
        :return:
        """
        if self.server:
            self.server.close()
        # Make sure the server file is removed.
        QtNetwork.QLocalServer.removeServer(self.id)
