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
import urllib
from urllib.parse import urlparse

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http import register_endpoint, requires_auth
from openlp.core.common import Registry
from openlp.core.lib import PluginStatus


log = logging.getLogger(__name__)

alert_endpoint = Endpoint('alert')
api_alert_endpoint = Endpoint('api')


@alert_endpoint.route('')
@api_alert_endpoint.route('alert')
@requires_auth
def alert(request):
    """
    Handles requests for setting service items in the service manager

    :param request: The http request object.
    """
    plugin = Registry().get('plugin_manager').get_plugin_by_name("alerts")
    if plugin.status == PluginStatus.Active:
        try:
            json_data = request.GET.get('data')
            text = json.loads(json_data)['request']['text']
        except KeyError:
            log.error("Endpoint alerts request text not found")
            text = urllib.parse.unquote(text)
        Registry().get('alerts_manager').alerts_text.emit([text])
        success = True
    else:
        success = False
    return {'results': {'success': success}}

register_endpoint(alert_endpoint)
register_endpoint(api_alert_endpoint)
