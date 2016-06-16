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
HTTP Error classes
"""


class HttpError(Exception):
    """
    A base HTTP error (aka status code)
    """
    def __init__(self, status, message):
        """
        Initialise the exception
        """
        super(HttpError, self).__init__(message)
        self.status = status
        self.message = message

    def to_response(self):
        """
        Convert this exception to a Response object
        """
        return self.message, self.status


class NotFound(HttpError):
    """
    A 404
    """
    def __init__(self):
        """
        Make this a 404
        """
        super(NotFound, self).__init__(404, 'Not Found')


class ServerError(HttpError):
    """
    A 500
    """
    def __init__(self):
        """
        Make this a 500
        """
        super(ServerError, self).__init__(500, 'Server Error')


