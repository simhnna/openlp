import logging
import os

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http import register_endpoint, requires_auth
from openlp.core.common import Registry, AppLocation, UiStrings, translate
from openlp.core.lib import image_to_byte, PluginStatus, StringContent


template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')


log = logging.getLogger(__name__)

stage_endpoint = Endpoint('stage', template_dir=template_dir, static_dir=static_dir)
main_endpoint = Endpoint('main', template_dir=template_dir, static_dir=static_dir)
blank_endpoint = Endpoint('', template_dir=template_dir, static_dir=static_dir)

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

TRANSLATED_STRINGS = {
    'app_title': "{main} {remote}".format(main=UiStrings().OLPV2x, remote=remote),
    'stage_title': "{main} {stage}".format(main=UiStrings().OLPV2x, stage=stage),
    'live_title': "{main} {live}".format(main=UiStrings().OLPV2x, live=live),
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


@blank_endpoint.route('poll')
def poll(request):
    """
    Deliver the page for the /poll url
    :param request:
    """
    return Registry().get('poller').raw_poll()


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


@blank_endpoint.route('api/plugin/{search:search}')
@blank_endpoint.route('plugin/{search:search}')
def plugin_search(request, search):
    """
    Deliver the functions for the /display url
    :param request: the http request - not used
    :param search: the display function to be triggered
    """
    searches = []
    for plugin in Registry().get('plugin_manager').plugins:
        if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
            searches.append([plugin.name, str(plugin.text_strings[StringContent.Name]['plural'])])
    return {'results': {'items': searches}}


@stage_endpoint.route('{local_path}')
def bespoke_file_access(request, local_path):
    """
    Allow Stage view to be delivered with custom views.

    :param request: base path of the URL. Not used but passed by caller
    :param local_path: path within the stages config directory
    :return:
    """
    config_dir = os.path.join(AppLocation.get_data_path(), 'stages')
    log.debug('serve file request {name}'.format(name=local_path))
    parts = local_path.split('/')
    if len(parts) == 1:
        file_name = os.path.join(parts[0], 'stage.mako')
    elif len(parts) == 3:
        file_name = os.path.join(parts[1], parts[2])
    path = os.path.normpath(os.path.join(config_dir, file_name))
    #return _process_file(path)


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


def get_content_type(file_name):
    """
    Examines the extension of the file and determines what the content_type should be, defaults to text/plain
    Returns the extension and the content_type

    :param file_name: name of file
    """
    ext = os.path.splitext(file_name)[1]
    content_type = FILE_TYPES.get(ext, 'text/plain')
    return ext, content_type

register_endpoint(stage_endpoint)
register_endpoint(blank_endpoint)
register_endpoint(main_endpoint)
