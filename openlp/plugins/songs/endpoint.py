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
from openlp.core.api.http import requires_auth


log = logging.getLogger(__name__)

songs_endpoint = Endpoint('songs')
api_songs_endpoint = Endpoint('api')


@songs_endpoint.route('search')
@api_songs_endpoint.route('songs/search')
def songs_search(request):
    """
    Handles requests for searching the songs plugin

    :param request: The http request object.
    """
    return search(request, 'songs', log)


@songs_endpoint.route('live')
@api_songs_endpoint.route('songs/live')
@requires_auth
def songs_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'songs', log)


@songs_endpoint.route('add')
@api_songs_endpoint.route('songs/add')
@requires_auth
def songs_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'songs', log)
