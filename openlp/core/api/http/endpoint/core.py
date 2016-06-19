import logging
import os

from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http import register_endpoint
from openlp.core.common import Registry, AppLocation, UiStrings, translate
from openlp.core.lib import image_to_byte

template_dir = static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
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
    #file_name = request.path
    #html_dir = os.path.join(AppLocation.get_directory(AppLocation.AppDir), 'core', 'api', 'html')
    #log.debug('serve file request {name}'.format(name=file_name))
    #if file_name.startswith('/'):
    #    file_name = file_name[1:]
    #if not file_name:
    #    file_name = 'index.mako'
    #if '.' not in file_name:
    #    file_name += '.html'
    #if file_name.startswith('/'):
    #    file_name = file_name[1:]
    #path = os.path.normpath(os.path.join(html_dir, file_name))
    return stage_endpoint.render_template('stage.mako', **TRANSLATED_STRINGS, static_url=static_dir)


@main_endpoint.route('')
def main_index(request):
    """
    Deliver the page for the /main url
    """
    return stage_endpoint.render_template('main.mako', **TRANSLATED_STRINGS)


@blank_endpoint.route('')
def static_file_loader(request):
    """
    Dummy endpoint to trigger endpoint creation
    :param request:
    """
    pass


# @stage_endpoint.route('(stage)/(.*)$')
# def bespoke_file_access(request):
#     """
#     Allow Stage view to be delivered with custom views.
#
#     :param request: base path of the URL. Not used but passed by caller
#     :return:
#     """
#     file_name = request.path
#     config_dir = os.path.join(AppLocation.get_data_path(), 'stages')
#     log.debug('serve file request {name}'.format(name=file_name))
#     parts = file_name.split('/')
#     if len(parts) == 1:
#         file_name = os.path.join(parts[0], 'stage.mako')
#     elif len(parts) == 3:
#         file_name = os.path.join(parts[1], parts[2])
#     path = os.path.normpath(os.path.join(config_dir, file_name))
#     #return _process_file(path)
#     pass


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

# @stage_endpoint.route(r'^/(\w+)/thumbnails([^/]+)?/(.*)$')
# def main_image(request):
#     """
#     Get a list of songs
#     :param request: base path of the URL. Not used but passed by caller
#     :return:
#     """
#     # songs = db.query(Song).get()
#     # return {'songs': [dictify(song) for song in songs]}
#     print("AAA")


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