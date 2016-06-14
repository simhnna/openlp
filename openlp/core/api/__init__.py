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

from .errors import NotFound, ServerError, HttpError
from .http import WSGIApplication, application


def _route_from_url(url_prefix, url):
    """
    Create a route from the URL
    """
    url_prefix = '/{prefix}/'.format(prefix=url_prefix.strip('/'))
    if not url:
        url = url_prefix[:-1]
    else:
        url = url_prefix + url
    url = url.replace('//', '/')
    return url


def register_endpoint(end_point):
    """
    Register an endpoint with the app
    """
    for url, view_func, method, secure in end_point.routes:
        route = _route_from_url(end_point.url_prefix, url)
        application.add_route(route, view_func, method, secure)

from .endpoint import Endpoint
from .apitab import ApiTab
from .websockets import WebSocketServer, Poll
from .http import HttpServer
from .apicontroller import ApiController

__all__ = ['Poll', 'ApiController', 'HttpServer', 'application']
