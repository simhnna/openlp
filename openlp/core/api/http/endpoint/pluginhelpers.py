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


def display_thumbnails(request, controller_name, log, dimensions, file_name, slide):
    """
    Handles requests for adding a song to the service

    Return an image to a web page based on a URL
    :param request: Request object
    :param controller_name: which controller is requesting the image
    :param log: the logger object
    :param dimensions: the image size eg 88x88
    :param file_name: the file name of the image
    :param slide: the individual image name
    :return:
    """
    import os
    import re
    import urllib
    from urllib.parse import urlparse
    from webob import Response
    from openlp.core.common import Registry, AppLocation
    from openlp.core.lib import image_to_byte

    log.debug('serve thumbnail {cname}/thumbnails{dim}/{fname}/{slide}'.format(cname=controller_name,
                                                                               dim=dimensions,
                                                                               fname=file_name,
                                                                               slide=slide))
    # -1 means use the default dimension in ImageManager
    width = -1
    height = -1
    image = None
    if dimensions:
        match = re.search('(\d+)x(\d+)', dimensions)
        if match:
            # let's make sure that the dimensions are within reason
            width = sorted([10, int(match.group(1)), 1000])[1]
            height = sorted([10, int(match.group(2)), 1000])[1]
    if controller_name and file_name:
        file_name = urllib.parse.unquote(file_name)
        if '..' not in file_name:  # no hacking please
            full_path = os.path.normpath(os.path.join(AppLocation.get_section_data_path(controller_name),
                                                      'thumbnails', file_name, slide))
            if os.path.exists(full_path):
                path, just_file_name = os.path.split(full_path)
                Registry().get('image_manager').add_image(full_path, just_file_name, None, width, height)
                image = Registry().get('image_manager').get_image(full_path, just_file_name, width, height)
    return Response(body=image_to_byte(image, False), status=200, content_type='image/png', charset='utf8')
