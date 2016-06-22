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

import base64
from functools import wraps
from webob import Response

from openlp.core.common.settings import Settings
from openlp.core.api.http.wsgiapp import WSGIApplication
from .errors import NotFound, ServerError, HttpError

application = WSGIApplication('api')


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
    for url, view_func, method in end_point.routes:
        # Set the view functions
        route = _route_from_url(end_point.url_prefix, url)
        application.add_route(route, view_func, method)
        # Add a static route if necessary
        if end_point.static_dir:
            static_route = _route_from_url(end_point.url_prefix, 'static')
            static_route += '(.*)'
            application.add_static_route(static_route, end_point.static_dir)


def check_auth(auth):
    """
    This function is called to check if a username password combination is valid.

    :param auth: the authorisation object which needs to be tested
    :return Whether authentication have been successful
    """
    auth_code = "{user}:{password}".format(user=Settings().value('remotes/user id'),
                                           password=Settings().value('remotes/password'))
    try:
        auth_base = base64.b64encode(auth_code)
    except TypeError:
        auth_base = base64.b64encode(auth_code.encode()).decode()
    if auth[1] == auth_base:
        return True
    else:
        return False


def authenticate():
    """
    Sends a 401 response that enables basic auth to be triggered
    """
    resp = Response(status=401)
    resp.www_authenticate = 'Basic realm="OpenLP Login Required"'
    return resp


def requires_auth(f):
    """
    Decorates a function which needs to be authenticated before it can be used from the remote.

    :param f: The function which has been wrapped
    :return: the called function or a request to authenticate
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Settings().value('remotes/authentication enabled'):
            return f(*args, **kwargs)
        req = args[0]
        if not hasattr(req, 'authorization'):
            return authenticate()
        else:
            auth = req.authorization
            if auth and check_auth(auth):
                return f(*args, **kwargs)
            else:
                return authenticate()
    return decorated
