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

bibles_endpoint = Endpoint('bibles')
api_bibles_endpoint = Endpoint('api')


@bibles_endpoint.route('search')
@api_bibles_endpoint.route('bibles/search')
def bibles_search(request):
    """
    Handles requests for searching the bibles plugin

    :param request: The http request object.
    """
    return search(request, 'bibles', log)


@bibles_endpoint.route('live')
@api_bibles_endpoint.route('bibles/live')
@requires_auth
def bibles_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'bibles', log)


@bibles_endpoint.route('add')
@api_bibles_endpoint.route('bibles/add')
@requires_auth
def bibles_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'bibles', log)

register_endpoint(bibles_endpoint)
register_endpoint(api_bibles_endpoint)
