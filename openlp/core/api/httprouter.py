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
App stuff
"""
import logging
import json
import re

from webob import Request, Response

from .errors import HttpError, NotFound, ServerError

log = logging.getLogger(__name__)


def _make_response(view_result):
    """
    Create a Response object from response
    """
    if isinstance(view_result, Response):
        return view_result
    elif isinstance(view_result, tuple):
        content_type = 'text/html'
        body = view_result[0]
        if isinstance(body, dict):
            content_type = 'application/json'
            body = json.dumps(body)
        response = Response(body=body, status=view_result[1],
                            content_type=content_type, charset='utf8')
        if len(view_result) >= 3:
            response.headers = view_result[2]
        return response
    elif isinstance(view_result, dict):
        return Response(body=json.dumps(view_result), status=200,
                        content_type='application/json', charset='utf8')
    elif isinstance(view_result, str):
        return Response(body=view_result, status=200,
                        content_type='text/html', charset='utf8')


def _handle_exception(error):
    """
    Handle exceptions
    """
    log.exception(error)
    if isinstance(error, HttpError):
        return error.to_response()
    else:
        return ServerError().to_response()


class WSGIApplication(object):
    """
    This is the core of the API, the WSGI app
    """
    def __init__(self, name):
        """
        Create the app object
        """
        self.name = name
        self.route_map = {}

    def add_route(self, route, view_func, method, secure):
        """
        Add a route
        """
        if route not in self.route_map:
            self.route_map[route] = {}
        self.route_map[route][method.upper()] = {'function': view_func, 'secure': secure}

    def dispatch(self, request):
        """
        Find the appropriate URL and run the view function
        """
        print(request.path)
        print(self.route_map.items())
        for route, views in self.route_map.items():
            if re.match(route, request.path):
                if request.method.upper() in views:
                    log.debug('Found {method} {url}'.format(method=request.method, url=request.path))
                    view_func = views[request.method.upper()]['function']
                    return _make_response(view_func(request))
        raise NotFound()

    def wsgi_app(self, environ, start_response):
        """
        The actual WSGI application.
        """
        request = Request(environ)
        try:
            response = self.dispatch(request)
        except Exception as e:
            response = _make_response(_handle_exception(e))
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        """
        Shortcut for wsgi_app.
        """
        return self.wsgi_app(environ, start_response)

