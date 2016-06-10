import logging
import os

from openlp.core.api import Endpoint, register_endpoint

log = logging.getLogger(__name__)

stage_endpoint = Endpoint('')


@stage_endpoint.route('$')
@stage_endpoint.route('(stage)$')
@stage_endpoint.route('(main)$')
def file_access(request):
    """
    Get a list of songs`
    """
    #songs = db.query(Song).get()
    #return {'songs': [dictify(song) for song in songs]}
    print("AAA")


@stage_endpoint.route('(stage)/(.*)$')
def bespoke_file_access(request):
    """
    Allow Stage view to be delivered with custom views.

    :param url_path: base path of the URL. Not used but passed by caller
    :param file_name: file name with path
    :return:
    """
    pass
    # log.debug('serve file request {name}'.format(name=file_name))
    # parts = file_name.split('/')
    # if len(parts) == 1:
    #     file_name = os.path.join(parts[0], 'stage.html')
    # elif len(parts) == 3:
    #     file_name = os.path.join(parts[1], parts[2])
    # path = os.path.normpath(os.path.join(self.config_dir, file_name))
    # if not path.startswith(self.config_dir):
    #     return self.do_not_found()
    # return _process_file(path)


@stage_endpoint.route('main/image$')
def main_image(request):
    """
    Return the latest display image as a byte stream.
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
    """
    # songs = db.query(Song).get()
    # return {'songs': [dictify(song) for song in songs]}
    print("AAA")


def _process_file(self, path):
    """
    Common file processing code

    :param path: path to file to be loaded
    :return: web resource to be loaded
    """
    # content = None
    # ext, content_type = self.get_content_type(path)
    # file_handle = None
    # try:
    #     if ext == '.html':
    #         variables = self.template_vars
    #         content = Template(filename=path, input_encoding='utf-8', output_encoding='utf-8').render(**variables)
    #     else:
    #         file_handle = open(path, 'rb')
    #         log.debug('Opened {path}'.format(path=path))
    #         content = file_handle.read()
    # except IOError:
    #     log.exception('Failed to open {path}'.format(path=path))
    #     return self.do_not_found()
    # finally:
    #     if file_handle:
    #         file_handle.close()
    # self.send_response(200)
    # self.send_header('Content-type', content_type)
    # self.end_headers()
    # return content
    pass

register_endpoint(stage_endpoint)
