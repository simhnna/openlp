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
import logging

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http.endpoint.pluginhelpers import search, live, service
from openlp.core.api.http import register_endpoint, requires_auth


log = logging.getLogger(__name__)

custom_endpoint = Endpoint('custom')
api_custom_endpoint = Endpoint('api')


@custom_endpoint.route('search')
@api_custom_endpoint.route('custom/search')
def custom_search(request):
    """
    Handles requests for searching the custom plugin

    :param request: The http request object.
    """
    return search(request, 'custom', log)


@custom_endpoint.route('live')
@api_custom_endpoint.route('custom/live')
@requires_auth
def custom_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'custom', log)


@custom_endpoint.route('add')
@api_custom_endpoint.route('custom/add')
@requires_auth
def custom_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'custom', log)

register_endpoint(custom_endpoint)
register_endpoint(api_custom_endpoint)
