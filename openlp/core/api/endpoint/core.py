# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
"""
The :mod:`~openlp.core.api.endpoint.core` module contains the core API endpoints
"""
import logging
import os

from openlp.core.api.http import requires_auth
from openlp.core.api.http.endpoint import Endpoint
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.registry import Registry
from openlp.core.lib import PluginStatus, StringContent, image_to_byte

template_dir = 'templates'
static_dir = 'static'
blank_dir = os.path.join(static_dir, 'index')


log = logging.getLogger(__name__)

chords_endpoint = Endpoint('chords', template_dir=template_dir, static_dir=static_dir)
stage_endpoint = Endpoint('stage', template_dir=template_dir, static_dir=static_dir)
main_endpoint = Endpoint('main', template_dir=template_dir, static_dir=static_dir)
blank_endpoint = Endpoint('', template_dir=template_dir, static_dir=blank_dir)

FILE_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.png': 'image/png'
}

remote = translate('RemotePlugin.Mobile', 'Remote')
stage = translate('RemotePlugin.Mobile', 'Stage View')
live = translate('RemotePlugin.Mobile', 'Live View')
chords = translate('RemotePlugin.Mobile', 'Chords View')

TRANSLATED_STRINGS = {
    'app_title': "{main} {remote}".format(main=UiStrings().OpenLP, remote=remote),
    'stage_title': "{main} {stage}".format(main=UiStrings().OpenLP, stage=stage),
    'live_title': "{main} {live}".format(main=UiStrings().OpenLP, live=live),
    'chords_title': "{main} {chords}".format(main=UiStrings().OpenLP, chords=chords),
    'service_manager': translate('RemotePlugin.Mobile', 'Service Manager'),
    'slide_controller': translate('RemotePlugin.Mobile', 'Slide Controller'),
    'alerts': translate('RemotePlugin.Mobile', 'Alerts'),
    'search': translate('RemotePlugin.Mobile', 'Search'),
    'home': translate('RemotePlugin.Mobile', 'Home'),
    'refresh': translate('RemotePlugin.Mobile', 'Refresh'),
    'blank': translate('RemotePlugin.Mobile', 'Blank'),
    'theme': translate('RemotePlugin.Mobile', 'Theme'),
    'desktop': translate('RemotePlugin.Mobile', 'Desktop'),
    'show': translate('RemotePlugin.Mobile', 'Show'),
    'prev': translate('RemotePlugin.Mobile', 'Prev'),
    'next': translate('RemotePlugin.Mobile', 'Next'),
    'text': translate('RemotePlugin.Mobile', 'Text'),
    'show_alert': translate('RemotePlugin.Mobile', 'Show Alert'),
    'go_live': translate('RemotePlugin.Mobile', 'Go Live'),
    'add_to_service': translate('RemotePlugin.Mobile', 'Add to Service'),
    'add_and_go_to_service': translate('RemotePlugin.Mobile', 'Add &amp; Go to Service'),
    'no_results': translate('RemotePlugin.Mobile', 'No Results'),
    'options': translate('RemotePlugin.Mobile', 'Options'),
    'service': translate('RemotePlugin.Mobile', 'Service'),
    'slides': translate('RemotePlugin.Mobile', 'Slides'),
    'settings': translate('RemotePlugin.Mobile', 'Settings'),
}


@stage_endpoint.route('')
def stage_index(request):
    """
    Deliver the page for the /stage url
    """
    return stage_endpoint.render_template('stage.mako', **TRANSLATED_STRINGS)


@chords_endpoint.route('')
def chords_index(request):
    """
    Deliver the page for the /chords url
    """
    return chords_endpoint.render_template('chords.mako', **TRANSLATED_STRINGS)


@main_endpoint.route('')
def main_index(request):
    """
    Deliver the page for the /main url
    """
    return main_endpoint.render_template('main.mako', **TRANSLATED_STRINGS)


@blank_endpoint.route('')
def index(request):
    """
    Deliver the page for the / url
    :param request:
    """
    return blank_endpoint.render_template('index.mako', **TRANSLATED_STRINGS)


@blank_endpoint.route('api/poll')
@blank_endpoint.route('poll')
def poll(request):
    """
    Deliver the page for the /poll url

    :param request:
    """
    return Registry().get('poller').poll()


@blank_endpoint.route('api/display/{display:hide|show|blank|theme|desktop}')
@blank_endpoint.route('display/{display:hide|show|blank|theme|desktop}')
@requires_auth
def toggle_display(request, display):
    """
    Deliver the functions for the /display url
    :param request: the http request - not used
    :param display: the display function to be triggered
    """
    Registry().get('live_controller').slidecontroller_toggle_display.emit(display)
    return {'results': {'success': True}}


@blank_endpoint.route('api/plugin/search')
@blank_endpoint.route('plugin/search')
def plugin_search_list(request):
    """
    Deliver a list of active plugins that support search
    :param request: the http request - not used
    """
    searches = []
    for plugin in Registry().get('plugin_manager').plugins:
        if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
            searches.append([plugin.name, str(plugin.text_strings[StringContent.Name]['plural'])])
    return {'results': {'items': searches}}


@main_endpoint.route('image')
def main_image(request):
    """
    Return the latest display image as a byte stream.
    :param request: base path of the URL. Not used but passed by caller
    :return:
    """
    live_controller = Registry().get('live_controller')
    result = {
        'slide_image': 'data:image/png;base64,' + str(image_to_byte(live_controller.slide_image))
    }
    return {'results': result}
