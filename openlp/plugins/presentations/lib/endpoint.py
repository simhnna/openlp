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
@api_presentations_endpoint.route('presentations/thumbnails88x88/{file_name}/{slide}')
@presentations_endpoint.route('thumbnails88x88/{file_name}/{slide}')
def presentations_thumbnails(request, file_name, slide):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    controller_name = 'presentations'
    dimensions = '88x88'
    import os
    import time
    import urllib
    from urllib.parse import urlparse
    from webob import Response
    from openlp.core.common import Registry, AppLocation

    log.debug('serve thumbnail {cname}/thumbnails{dim}/{fname}'.format(cname=controller_name,
                                                                       dim=dimensions,
                                                                       fname=file_name))
    content = None
    if controller_name and file_name:
        file_name = urllib.parse.unquote(file_name)
        if '..' not in file_name:  # no hacking please
            full_path = os.path.normpath(os.path.join(AppLocation.get_section_data_path(controller_name),
                                                      'thumbnails/', file_name, slide))
            if os.path.exists(full_path):
                image_manager = Registry().get("image_manager")
                i = 0
                while i < 4 and content is None:
                    content = image_manager.get_image_bytes(full_path, file_name, 88, 88)
                    time.sleep(0.1)
                    i += 1
    return Response(body=content, status=200, content_type='data:image/png;base64', charset='utf8')


register_endpoint(presentations_endpoint)
register_endpoint(api_presentations_endpoint)
