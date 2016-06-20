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
import json

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http import register_endpoint, requires_auth
from openlp.core.common import Registry


log = logging.getLogger(__name__)

service_endpoint = Endpoint('service')


@service_endpoint.route('list')
def list_service(request):
    """
    Handles requests for service items in the service manager

    :param request: The http request object.
    """
    return {'results': {'items': get_service_items()}}


@service_endpoint.route('set')
@requires_auth
def service_set(request):
    """
    Handles requests for setting service items in the service manager

    :param request: The http request object.
    """
    event = getattr(Registry().get('service_manager'), 'servicemanager_set_item')
    try:
        json_data = request.GET.get('data')
        data = int(json.loads(json_data)['request']['id'])
        event.emit(data)
    except KeyError:
        log.error("Endpoint service/set request id not found")
    return {'results': {'success': True}}


def get_service_items():
    """
    Read the service item in use and return the data as a json object
    """
    live_controller = Registry().get('live_controller')
    service_items = []
    if live_controller.service_item:
        current_unique_identifier = live_controller.service_item.unique_identifier
    else:
        current_unique_identifier = None
    for item in Registry().get('service_manager').service_items:
        service_item = item['service_item']
        service_items.append({
            'id': str(service_item.unique_identifier),
            'title': str(service_item.get_display_title()),
            'plugin': str(service_item.name),
            'notes': str(service_item.notes),
            'selected': (service_item.unique_identifier == current_unique_identifier)
        })
    return service_items

register_endpoint(service_endpoint)
