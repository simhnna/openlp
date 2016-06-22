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
import json
import urllib
from urllib.parse import urlparse

from openlp.core.common import Registry
from openlp.core.lib import PluginStatus


def search(request, plugin_name, log):
    """
    Handles requests for searching the plugins

    :param request: The http request object.
    :param plugin_name: The plugin name.
    :param log: The class log object.
    """
    try:
        json_data = request.GET.get('data')
        text = json.loads(json_data)['request']['text']
    except KeyError:
        log.error("Endpoint {text} search request text not found".format(text=plugin_name))
        text = ""
    text = urllib.parse.unquote(text)
    plugin = Registry().get('plugin_manager').get_plugin_by_name(plugin_name)
    if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
        results = plugin.media_item.search(text, False)
    else:
        results = []
    return {'results': {'items': results}}


def live(request, plugin_name, log):
    """
    Handles requests for making live of the plugins

    :param request: The http request object.
    :param plugin_name: The plugin name.
    :param log: The class log object.
    """
    try:
        json_data = request.GET.get('data')
        request_id = json.loads(json_data)['request']['id']
    except KeyError:
        log.error("Endpoint {text} search request text not found".format(text=plugin_name))
        return []
    plugin = Registry().get('plugin_manager').get_plugin_by_name(plugin_name)
    if plugin.status == PluginStatus.Active and plugin.media_item:
        getattr(plugin.media_item, '{name}_go_live'.format(name=plugin_name)).emit([request_id, True])
    return []


def service(request, plugin_name, log):
    """
    Handles requests for adding to a service of the plugins

    :param request: The http request object.
    :param plugin_name: The plugin name.
    :param log: The class log object.
    """
    try:
        json_data = request.GET.get('data')
        request_id = json.loads(json_data)['request']['id']
    except KeyError:
        log.error("Endpoint {plugin} search request text not found".format(plugin=plugin_name))
        return []
    plugin = Registry().get('plugin_manager').get_plugin_by_name(plugin_name)
    if plugin.status == PluginStatus.Active and plugin.media_item:
        item_id = plugin.media_item.create_item_from_id(request_id)
        getattr(plugin.media_item, '{name}_add_to_service'.format(name=plugin_name)).emit([item_id, True])
    return []
