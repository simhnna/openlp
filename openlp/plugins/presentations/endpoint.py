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
from openlp.core.api.http.endpoint.pluginhelpers import search, live, service, display_thumbnails
from openlp.core.api.http import requires_auth


log = logging.getLogger(__name__)

presentations_endpoint = Endpoint('presentations')
api_presentations_endpoint = Endpoint('api')


@presentations_endpoint.route('search')
@api_presentations_endpoint.route('presentations/search')
def presentations_search(request):
    """
    Handles requests for searching the presentations plugin

    :param request: The http request object.
    """
    return search(request, 'presentations', log)


@presentations_endpoint.route('live')
@api_presentations_endpoint.route('presentations/live')
@requires_auth
def presentations_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'presentations', log)


@presentations_endpoint.route('add')
@api_presentations_endpoint.route('presentations/add')
@requires_auth
def presentations_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'presentations', log)


# /presentations/thumbnails88x88/PA%20Rota.pdf/slide5.png
@presentations_endpoint.route('thumbnails/{dimensions}/{file_name}/{slide}')
def presentations_thumbnails(request, dimensions, file_name, slide):
    """
    Return a presentation to a web page based on a URL
    :param request: Request object
    :param dimensions: the image size eg 88x88
    :param file_name: the file name of the image
    :param slide: the individual image name
    :return:
    """
    return display_thumbnails(request, 'presentations', log, dimensions, file_name, slide)
