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


from PyQt5 import QtCore
from PyQt5 import QtNetwork

from openlp.core.common.mixins import LogMixin


class Server(QtCore.QObject, LogMixin):
    """
    The local server to handle OpenLP running in more than one instance and allows file
    handles to be transferred from the new to the existing one.
    """

    def is_another_instance_running(self):
        self._id = 'OpenLPDual'
        # Is there another instance running?
        self._outSocket = QtNetwork.QLocalSocket()
        self._outSocket.connectToServer(self._id)
        return self._outSocket.waitForConnected()

    def post_to_server(self, args):
        print(args)
        if 'OpenLP' in args:
            print("remove1")
            args.remove('OpenLP')
        # Yes, there is.
        print("isRunning")
        self._outStream = QtCore.QTextStream(self._outSocket)
        self._outStream.setCodec('UTF-8')
        self._outSocket.write(str.encode("".join(args)))
        if not self._outSocket.waitForBytesWritten(10):
            raise Exception(str(self._outSocket.errorString()))
        self._outSocket.disconnectFromServer()
        return False

    def start_server(self):
            # No, there isn't.
            print("No it is not")
            self._outSocket = None
            self._outStream = None
            self._inSocket = None
            self._inStream = None
            self._server = QtNetwork.QLocalServer()
            self._server.listen(self._id)
            self._server.newConnection.connect(self._on_new_connection)
            return True

    def _on_new_connection(self):
        """
        Handle a new connection to the server
        :return:
        """
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._on_ready_read)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QtCore.QTextStream(self._inSocket)
        self._inStream.setCodec('UTF-8')
        self._inSocket.readyRead.connect(self._on_ready_read)

    def _on_ready_read(self):
        """
        Read a record passed to the server and load a service
        :return:
        """
        while True:
            msg = self._inStream.readLine()
            if msg:
                self.log_debug("socket msg = " + msg)
                Registry().get('service_manager').on_load_service_clicked(msg)

    def close_server(self):
        """
        Shutdown to local socket server
        :return:
        """
        if self._server:
            self._server.close()