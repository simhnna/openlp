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
from openlp.core.api.http import register_endpoint, requires_auth


log = logging.getLogger(__name__)

images_endpoint = Endpoint('images')
api_images_endpoint = Endpoint('api')


@images_endpoint.route('search')
@api_images_endpoint.route('images/search')
def images_search(request):
    """
    Handles requests for searching the images plugin

    :param request: The http request object.
    """
    return search(request, 'images', log)


@images_endpoint.route('live')
@api_images_endpoint.route('images/live')
@requires_auth
def images_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'images', log)


@images_endpoint.route('add')
@api_images_endpoint.route('images/add')
@requires_auth
def images_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'images', log)


@images_endpoint.route('thumbnails/{dimensions}/{file_name}/{slide}')
def images_thumbnails(request, dimensions, file_name, slide):
    """
    Return an image to a web page based on a URL
    :param request: Request object
    :param dimensions: the image size eg 88x88
    :param file_name: the file name of the image
    :param slide: the individual image name
    :return:
    """
    return display_thumbnails(request, 'images', log, dimensions, file_name, slide)


register_endpoint(images_endpoint)
register_endpoint(api_images_endpoint)
