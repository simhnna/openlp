# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
import hashlib
import logging
import platform
import socket
import sys
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPException
from random import randint

from openlp.core.common import Registry, trace_error_handler

log = logging.getLogger(__name__ + '.__init__')

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


def get_user_agent():
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
        user_agent = get_user_agent()
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
            log.debug('Downloaded page {text}'.format(text=page.geturl()))
            break
        except urllib.error.URLError as err:
            log.exception('URLError on {text}'.format(text=url))
            log.exception('URLError: {text}'.format(text=err.reason))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except socket.timeout:
            log.exception('Socket timeout: {text}'.format(text=url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except socket.gaierror:
            log.exception('Socket gaierror: {text}'.format(text=url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except ConnectionRefusedError:
            log.exception('ConnectionRefused: {text}'.format(text=url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
            break
        except ConnectionError:
            log.exception('Connection error: {text}'.format(text=url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except HTTPException:
            log.exception('HTTPException error: {text}'.format(text=url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except:
            # Don't know what's happening, so reraise the original
            raise
    if update_openlp:
        Registry().get('application').process_events()
    if not page:
        log.exception('{text} could not be downloaded'.format(text=url))
        return None
    log.debug(page)
    return page


def get_url_file_size(url):
    """
    Get the size of a file.

    :param url: The URL of the file we want to download.
    """
    retries = 0
    while True:
        try:
            site = urllib.request.urlopen(url, timeout=CONNECTION_TIMEOUT)
            meta = site.info()
            return int(meta.get("Content-Length"))
        except urllib.error.URLError:
            if retries > CONNECTION_RETRIES:
                raise
            else:
                retries += 1
                time.sleep(0.1)
                continue


def url_get_file(callback, url, f_path, sha256=None):
    """"
    Download a file given a URL.  The file is retrieved in chunks, giving the ability to cancel the download at any
    point. Returns False on download error.

    :param callback: the class which needs to be updated
    :param url: URL to download
    :param openlp.core.common.path.Path f_path: Destination file
    :param sha256: The check sum value to be checked against the download value
    """
    block_count = 0
    block_size = 4096
    retries = 0
    log.debug("url_get_file: " + url)
    while True:
        try:
            if sha256:
                hasher = hashlib.sha256()
            with f_path.open('wb') as file:
                url_file = urllib.request.urlopen(url, timeout=CONNECTION_TIMEOUT)
                # Download until finished or canceled.
                while not callback.was_cancelled:
                    data = url_file.read(block_size)
                    if not data:
                        break
                    file.write(data)
                    if sha256:
                        hasher.update(data)
                    block_count += 1
                    callback._download_progress(block_count, block_size)
        except (urllib.error.URLError, socket.timeout):
            trace_error_handler(log)
            f_path.unlink()
            if retries > CONNECTION_RETRIES:
                return False
            else:
                retries += 1
                time.sleep(0.1)
                continue
        break
    # Delete file if cancelled, it may be a partial file.
    if sha256 and hasher.hexdigest() != sha256:
        log.error('sha256 sums did not match for file: {file}'.format(file=f_path))
        f_path.unlink()
        return False
    if callback.was_cancelled:
        f_path.unlink()
    return True


def ping(host):
    """
    Returns True if host responds to a ping request
    """
    # Ping parameters as function of OS
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    args = "ping " + " " + ping_str + " " + host
    need_sh = False if platform.system().lower() == "windows" else True

    # Ping
    return subprocess.call(args, shell=need_sh) == 0


__all__ = ['get_web_page']
