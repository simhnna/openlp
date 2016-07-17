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
import os
import urllib.request
import urllib.error
import json

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http import register_endpoint, requires_auth
from openlp.core.common import Registry, AppLocation, Settings
from openlp.core.lib import ItemCapabilities, create_thumb

log = logging.getLogger(__name__)

controller_endpoint = Endpoint('controller')
api_controller_endpoint = Endpoint('api')


@api_controller_endpoint.route('controller/live/text')
@controller_endpoint.route('live/text')
def controller_text(request):
    """
    Perform an action on the slide controller.

    :param request: the http request - not used
    """
    log.debug("controller_text ")
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    data = []
    if current_item:
        for index, frame in enumerate(current_item.get_frames()):
            item = {}
            # Handle text (songs, custom, bibles)
            if current_item.is_text():
                if frame['verseTag']:
                    item['tag'] = str(frame['verseTag'])
                else:
                    item['tag'] = str(index + 1)
                item['text'] = str(frame['text'])
                item['html'] = str(frame['html'])
            # Handle images, unless a custom thumbnail is given or if thumbnails is disabled
            elif current_item.is_image() and not frame.get('image', '') and Settings().value('api/thumbnails'):
                item['tag'] = str(index + 1)
                thumbnail_path = os.path.join('images', 'thumbnails', frame['title'])
                full_thumbnail_path = os.path.join(AppLocation.get_data_path(), thumbnail_path)
                # Create thumbnail if it doesn't exists
                if not os.path.exists(full_thumbnail_path):
                    create_thumb(current_item.get_frame_path(index), full_thumbnail_path, False)
                Registry().get('image_manager').add_image(full_thumbnail_path, frame['title'], None, 88, 88)
                item['img'] = urllib.request.pathname2url(os.path.sep + thumbnail_path)
                item['text'] = str(frame['title'])
                item['html'] = str(frame['title'])
            else:
                # Handle presentation etc.
                item['tag'] = str(index + 1)
                if current_item.is_capable(ItemCapabilities.HasDisplayTitle):
                    item['title'] = str(frame['display_title'])
                if current_item.is_capable(ItemCapabilities.HasNotes):
                    item['slide_notes'] = str(frame['notes'])
                if current_item.is_capable(ItemCapabilities.HasThumbnails) and \
                        Settings().value('api/thumbnails'):
                    # If the file is under our app directory tree send the portion after the match
                    data_path = AppLocation.get_data_path()
                    if frame['image'][0:len(data_path)] == data_path:
                        item['img'] = urllib.request.pathname2url(frame['image'][len(data_path):])
                    Registry().get('image_manager').add_image(frame['image'], frame['title'], None, 88, 88)
                item['text'] = str(frame['title'])
                item['html'] = str(frame['title'])
            item['selected'] = (live_controller.selected_row == index)
            data.append(item)
    json_data = {'results': {'slides': data}}
    if current_item:
        json_data['results']['item'] = live_controller.service_item.unique_identifier
    return json_data


@api_controller_endpoint.route('controller/live/set')
@controller_endpoint.route('live/set')
@requires_auth
def controller_set(request):
    """
    Perform an action on the slide controller.

    :param request: The action to perform.
    """
    event = getattr(Registry().get('live_controller'), 'slidecontroller_live_set')
    try:
        json_data = request.GET.get('data')
        data = int(json.loads(json_data)['request']['id'])
        event.emit([data])
    except KeyError:
        log.error("Endpoint controller/live/set request id not found")
    return {'results': {'success': True}}


@api_controller_endpoint.route('/controller/{controller}/{action:next|previous}')
@controller_endpoint.route('/{controller}/{action:next|previous}')
@requires_auth
def controller_direction(request, controller, action):
    """
    Handles requests for setting service items in the slide controller
11
    :param request: The http request object.
    :param controller: the controller slides forward or backward.
    :param action: the controller slides forward or backward.
    """
    event = getattr(Registry().get('live_controller'), 'slidecontroller_{controller}_{action}'.
                    format(controller=controller, action=action))
    event.emit()
    return {'results': {'success': True}}

register_endpoint(controller_endpoint)
register_endpoint(api_controller_endpoint)
