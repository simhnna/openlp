# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4
# pylint: disable=logging-format-interpolation

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
import json
import logging
import os
import re

from webob import Request, Response
from webob.static import DirectoryApp

from openlp.core.api.http.errors import HttpError, NotFound, ServerError

ARGS_REGEX = re.compile(r'''\{(\w+)(?::([^}]+))?\}''', re.VERBOSE)

log = logging.getLogger(__name__)


def _route_to_regex(route):
    """
    Convert a route to a regular expression

    For example:

      'songs/{song_id}' becomes 'songs/(?P<song_id>[^/]+)'

    and

      'songs/{song_id:\d+}' becomes 'songs/(?P<song_id>\d+)'

    """
    route_regex = ''
    last_pos = 0
    for match in ARGS_REGEX.finditer(route):
        route_regex += re.escape(route[last_pos:match.start()])
        arg_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (arg_name, expr)
        route_regex += expr
        last_pos = match.end()
    route_regex += re.escape(route[last_pos:])
    route_regex = '^%s$' % route_regex
    return route_regex


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
        response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
        response.headers.add("Pragma", "no-cache")
        response.headers.add("Expires", "0")
        if len(view_result) >= 3:
            response.headers.update(view_result[2])
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
        self.static_routes = {}
        self.route_map = {}

    def add_route(self, route, view_func, method):
        """
        Add a route
        """
        route_regex = _route_to_regex(route)
        if route_regex not in self.route_map:
            self.route_map[route_regex] = {}
        self.route_map[route_regex][method.upper()] = view_func

    def add_static_route(self, route, static_dir):
        """
        Add a static directory as a route
        """
        if route not in self.static_routes:
            self.static_routes[route] = DirectoryApp(os.path.abspath(static_dir))

    def dispatch(self, request):
        """
        Find the appropriate URL and run the view function
        """
        # We are not interested in this so discard
        if 'favicon' in request.path:
            return
        # First look to see if this is a static file request
        for route, static_app in self.static_routes.items():
            if re.match(route, request.path):
                # Pop the path info twice in order to get rid of the "/<plugin>/static"
                # request.path_info_pop()
                request.path_info_pop()
                return request.get_response(static_app)
        # If not a static route, try the views
        for route, views in self.route_map.items():
            path = request.path
            match = re.match(route, path)
            if match and request.method.upper() in views:
                kwargs = match.groupdict()
                log.debug('Found {method} {url}'.format(method=request.method, url=request.path))
                view_func = views[request.method.upper()]
                return _make_response(view_func(request, **kwargs))
        log.error('Not Found url {url} '.format(url=request.path))
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
        response.headers.add("cache-control", "no-cache, no-store, must-revalidate")
        response.headers.add("pragma", "no-cache")
        response.headers.add("expires", "0")
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        """
        Shortcut for wsgi_app.
        """
        # We are not interested in this so discard
        if 'favicon' in environ["PATH_INFO"]:
            return
        return self.wsgi_app(environ, start_response)
