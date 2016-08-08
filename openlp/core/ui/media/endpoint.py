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
from openlp.core.api.http import register_endpoint, requires_auth
from openlp.core.common import Registry


log = logging.getLogger(__name__)

media_endpoint = Endpoint('media')


@media_endpoint.route('play')
@requires_auth
def media_play(request):
    """
    Handles requests for playing media

    :param request: The http request object.
    """
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    status = media.media_play(live, False)
    return {'results': {'success': status}}


@media_endpoint.route('pause')
@requires_auth
def media_pause(request):
    """
    Handles requests for pausing media

    :param request: The http request object.
    """
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    status = media.media_pause(live)
    return {'results': {'success': status}}


@media_endpoint.route('stop')
@requires_auth
def media_stop(request):
    """
    Handles requests for stopping

    :param request: The http request object.
    """
    event = getattr(Registry().get('live_controller'), 'mediacontroller_live_stop')
    event.emit()
    return {'results': {'success': True}}

register_endpoint(media_endpoint)
