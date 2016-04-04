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
"""
The :mod:`openlp.core.utils` module provides the utility libraries for OpenLP.
"""
import logging
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPException
from random import randint
from shutil import which
from subprocess import Popen, PIPE

from PyQt5 import QtGui, QtCore

from openlp.core.common import Registry, AppLocation, Settings, is_win, is_macosx

if not is_win() and not is_macosx():
    try:
        from xdg import BaseDirectory
        XDG_BASE_AVAILABLE = True
    except ImportError:
        BaseDirectory = None
        XDG_BASE_AVAILABLE = False

from openlp.core.common import translate

log = logging.getLogger(__name__ + '.__init__')

APPLICATION_VERSION = {}
IMAGES_FILTER = None
ICU_COLLATOR = None
CONTROL_CHARS = re.compile(r'[\x00-\x1F\x7F-\x9F]', re.UNICODE)
INVALID_FILE_CHARS = re.compile(r'[\\/:\*\?"<>\|\+\[\]%]', re.UNICODE)
DIGITS_OR_NONDIGITS = re.compile(r'\d+|\D+', re.UNICODE)
USER_AGENTS = {
    'win32': [
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36'
    ],
    'darwin': [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) '
        'Chrome/26.0.1410.43 Safari/537.31',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.57 Safari/536.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.47 Safari/536.11',
    ],
    'linux2': [
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 '
        'Chrome/25.0.1364.160 Safari/537.22',
        'Mozilla/5.0 (X11; CrOS armv7l 2913.260.0) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.99 '
        'Safari/537.11',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.27 (KHTML, like Gecko) Chrome/26.0.1389.0 Safari/537.27'
    ],
    'default': [
        'Mozilla/5.0 (X11; NetBSD amd64; rv:18.0) Gecko/20130120 Firefox/18.0'
    ]
}
CONNECTION_TIMEOUT = 30
CONNECTION_RETRIES = 2


class HTTPRedirectHandlerFixed(urllib.request.HTTPRedirectHandler):
    """
    Special HTTPRedirectHandler used to work around http://bugs.python.org/issue22248
    (Redirecting to urls with special chars)
    """
    def redirect_request(self, req, fp, code, msg, headers, new_url):
        #
        """
        Test if the new_url can be decoded to ascii

        :param req:
        :param fp:
        :param code:
        :param msg:
        :param headers:
        :param new_url:
        :return:
        """
        try:
            new_url.encode('latin1').decode('ascii')
            fixed_url = new_url
        except Exception:
            # The url could not be decoded to ascii, so we do some url encoding
            fixed_url = urllib.parse.quote(new_url.encode('latin1').decode('utf-8', 'replace'), safe='/:')
        return super(HTTPRedirectHandlerFixed, self).redirect_request(req, fp, code, msg, headers, fixed_url)


def get_filesystem_encoding():
    """
    Returns the name of the encoding used to convert Unicode filenames into system file names.
    """
    encoding = sys.getfilesystemencoding()
    if encoding is None:
        encoding = sys.getdefaultencoding()
    return encoding


def get_images_filter():
    """
    Returns a filter string for a file dialog containing all the supported image formats.
    """
    global IMAGES_FILTER
    if not IMAGES_FILTER:
        log.debug('Generating images filter.')
        formats = list(map(bytes.decode, list(map(bytes, QtGui.QImageReader.supportedImageFormats()))))
        visible_formats = '(*.%s)' % '; *.'.join(formats)
        actual_formats = '(*.%s)' % ' *.'.join(formats)
        IMAGES_FILTER = '%s %s %s' % (translate('OpenLP', 'Image Files'), visible_formats, actual_formats)
    return IMAGES_FILTER


def is_not_image_file(file_name):
    """
    Validate that the file is not an image file.

    :param file_name: File name to be checked.
    """
    if not file_name:
        return True
    else:
        formats = [bytes(fmt).decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()]
        file_part, file_extension = os.path.splitext(str(file_name))
        if file_extension[1:].lower() in formats and os.path.exists(file_name):
            return False
        return True


def split_filename(path):
    """
    Return a list of the parts in a given path.
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return path, ''
    else:
        return os.path.split(path)


def clean_filename(filename):
    """
    Removes invalid characters from the given ``filename``.

    :param filename:  The "dirty" file name to clean.
    """
    if not isinstance(filename, str):
        filename = str(filename, 'utf-8')
    return INVALID_FILE_CHARS.sub('_', CONTROL_CHARS.sub('', filename))


def delete_file(file_path_name):
    """
    Deletes a file from the system.

    :param file_path_name: The file, including path, to delete.
    """
    if not file_path_name:
        return False
    try:
        if os.path.exists(file_path_name):
            os.remove(file_path_name)
        return True
    except (IOError, OSError):
        log.exception("Unable to delete file %s" % file_path_name)
        return False


def _get_user_agent():
    """
    Return a user agent customised for the platform the user is on.
    """
    browser_list = USER_AGENTS.get(sys.platform, None)
    if not browser_list:
        browser_list = USER_AGENTS['default']
    random_index = randint(0, len(browser_list) - 1)
    return browser_list[random_index]


def get_web_page(url, header=None, update_openlp=False):
    """
    Attempts to download the webpage at url and returns that page or None.

    :param url: The URL to be downloaded.
    :param header:  An optional HTTP header to pass in the request to the web server.
    :param update_openlp: Tells OpenLP to update itself if the page is successfully downloaded.
        Defaults to False.
    """
    # TODO: Add proxy usage. Get proxy info from OpenLP settings, add to a
    # proxy_handler, build into an opener and install the opener into urllib2.
    # http://docs.python.org/library/urllib2.html
    if not url:
        return None
    # This is needed to work around http://bugs.python.org/issue22248 and https://bugs.launchpad.net/openlp/+bug/1251437
    opener = urllib.request.build_opener(HTTPRedirectHandlerFixed())
    urllib.request.install_opener(opener)
    req = urllib.request.Request(url)
    if not header or header[0].lower() != 'user-agent':
        user_agent = _get_user_agent()
        req.add_header('User-Agent', user_agent)
    if header:
        req.add_header(header[0], header[1])
    log.debug('Downloading URL = %s' % url)
    retries = 0
    while retries <= CONNECTION_RETRIES:
        retries += 1
        time.sleep(0.1)
        try:
            page = urllib.request.urlopen(req, timeout=CONNECTION_TIMEOUT)
            log.debug('Downloaded page {}'.format(page.geturl()))
            break
        except urllib.error.URLError as err:
            log.exception('URLError on {}'.format(url))
            log.exception('URLError: {}'.format(err.reason))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except socket.timeout:
            log.exception('Socket timeout: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except socket.gaierror:
            log.exception('Socket gaierror: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except ConnectionRefusedError:
            log.exception('ConnectionRefused: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
            break
        except ConnectionError:
            log.exception('Connection error: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except HTTPException:
            log.exception('HTTPException error: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except:
            # Don't know what's happening, so reraise the original
            raise
    if update_openlp:
        Registry().get('application').process_events()
    if not page:
        log.exception('{} could not be downloaded'.format(url))
        return None
    log.debug(page)
    return page


def get_uno_command(connection_type='pipe'):
    """
    Returns the UNO command to launch an libreoffice.org instance.
    """
    for command in ['libreoffice', 'soffice']:
        if which(command):
            break
    else:
        raise FileNotFoundError('Command not found')

    OPTIONS = '--nologo --norestore --minimized --nodefault --nofirststartwizard'
    if connection_type == 'pipe':
        CONNECTION = '"--accept=pipe,name=openlp_pipe;urp;"'
    else:
        CONNECTION = '"--accept=socket,host=localhost,port=2002;urp;"'
    return '%s %s %s' % (command, OPTIONS, CONNECTION)


def get_uno_instance(resolver, connection_type='pipe'):
    """
    Returns a running libreoffice.org instance.

    :param resolver: The UNO resolver to use to find a running instance.
    """
    log.debug('get UNO Desktop Openoffice - resolve')
    if connection_type == 'pipe':
        return resolver.resolve('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext')
    else:
        return resolver.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext')

__all__ = ['get_application_version', 'check_latest_version',
           'get_filesystem_encoding', 'get_web_page', 'get_uno_command', 'get_uno_instance',
           'delete_file', 'clean_filename']
