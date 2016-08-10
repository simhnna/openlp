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
The Endpoint class, which provides plugins with a way to serve their own portion of the API
"""

import os

from mako.template import Template


class Endpoint(object):
    """
    This is an endpoint for the HTTP API
    """
    def __init__(self, url_prefix, template_dir=None, static_dir=None, assets_dir=None):
        """
        Create an endpoint with a URL prefix
        """
        self.url_prefix = url_prefix
        self.static_dir = static_dir
        self.template_dir = template_dir
        if assets_dir:
            self.assets_dir = assets_dir
        else:
            self.assets_dir = os.path.dirname(os.path.realpath(__file__))
        self.routes = []

    def add_url_route(self, url, view_func, method):
        """
        Add a url route to the list of routes
        """
        self.routes.append((url, view_func, method))

    def route(self, rule, method='GET'):
        """
        Set up a URL route
        """
        def decorator(func):
            """
            Make this a decorator
            """
            self.add_url_route(rule, func, method)
            return func
        return decorator

    def render_template(self, filename, **kwargs):
        """
        Render a mako template
        """
        if not self.template_dir:
            raise Exception('No template directory specified')
        path = os.path.abspath(os.path.join(self.template_dir, filename))
        if self.static_dir:
            kwargs['static_url'] = '/{prefix}/static'.format(prefix=self.url_prefix)
            kwargs['static_url'] = kwargs['static_url'].replace('//', '/')
        kwargs['assets_url'] = '/assets'
        return Template(filename=path, input_encoding='utf-8').render(**kwargs)

from .pluginhelpers import search, live, service
