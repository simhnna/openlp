import logging
import os

from openlp.core.api import Endpoint, register_endpoint
from openlp.core.common import AppLocation, UiStrings, translate


from mako.template import Template


log = logging.getLogger(__name__)

stage_endpoint = Endpoint('')

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

template_vars = {
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


@stage_endpoint.route('$')
@stage_endpoint.route('(stage)$')
@stage_endpoint.route('(main)$')
@stage_endpoint.route('(css)')
@stage_endpoint.route('(js)')
@stage_endpoint.route('(assets)')
def file_access(request):
    """
    Get a list of songs`
    """
    file_name = request.path
    html_dir = os.path.join(AppLocation.get_directory(AppLocation.AppDir), 'core', 'api', 'html')
    log.debug('serve file request {name}'.format(name=file_name))
    if file_name.startswith('/'):
        file_name = file_name[1:]
    if not file_name:
        file_name = 'index.html'
    if '.' not in file_name:
        file_name += '.html'
    if file_name.startswith('/'):
        file_name = file_name[1:]
    path = os.path.normpath(os.path.join(html_dir, file_name))
    return _process_file(path)


@stage_endpoint.route('(stage)/(.*)$')
def bespoke_file_access(request):
    """
    Allow Stage view to be delivered with custom views.

    :param request: base path of the URL. Not used but passed by caller
    :return:
    """
    file_name = request.path
    config_dir = os.path.join(AppLocation.get_data_path(), 'stages')
    log.debug('serve file request {name}'.format(name=file_name))
    parts = file_name.split('/')
    if len(parts) == 1:
        file_name = os.path.join(parts[0], 'stage.html')
    elif len(parts) == 3:
        file_name = os.path.join(parts[1], parts[2])
    path = os.path.normpath(os.path.join(config_dir, file_name))
    return _process_file(path)


@stage_endpoint.route('main/image$')
def main_image(request):
    """
    Return the latest display image as a byte stream.
    :param request: base path of the URL. Not used but passed by caller
    :return:
    """
    # result = {
    #     'slide_image': 'data:image/png;base64,' + str(image_to_byte(self.live_controller.slide_image))
    # }
    # self.do_json_header()
    # return json.dumps({'results': result}).encode()
    pass


@stage_endpoint.route(r'^/(\w+)/thumbnails([^/]+)?/(.*)$')
def main_image(request):
    """
    Get a list of songs
    :param request: base path of the URL. Not used but passed by caller
    :return:
    """
    # songs = db.query(Song).get()
    # return {'songs': [dictify(song) for song in songs]}
    print("AAA")


def _process_file(path):
    """
    Common file processing code

    :param path: path to file to be loaded
    :return: web resource to be loaded
    """
    ext, content_type = get_content_type(path)
    file_handle = None
    try:
        if ext == '.html':
            variables = template_vars
            content = Template(filename=path, input_encoding='utf-8').render(**variables)
        else:
            file_handle = open(path, 'rb')
            log.debug('Opened {path}'.format(path=path))
            content = file_handle.read().decode("utf-8")
    except IOError:
        log.exception('Failed to open {path}'.format(path=path))
        return None
    finally:
        if file_handle:
            file_handle.close()
    return content


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
