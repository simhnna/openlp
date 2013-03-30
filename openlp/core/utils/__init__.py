# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2013 Raoul Snyman                                        #
# Portions copyright (c) 2008-2013 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
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
from datetime import datetime
from distutils.version import LooseVersion
import logging
import locale
import os
import re
from subprocess import Popen, PIPE
import sys
import urllib2
import icu

from PyQt4 import QtGui, QtCore

from openlp.core.lib import Registry, Settings


if sys.platform != u'win32' and sys.platform != u'darwin':
    try:
        from xdg import BaseDirectory
        XDG_BASE_AVAILABLE = True
    except ImportError:
        XDG_BASE_AVAILABLE = False

from openlp.core.lib import translate

log = logging.getLogger(__name__)
APPLICATION_VERSION = {}
IMAGES_FILTER = None
ICU_COLLATOR = None
UNO_CONNECTION_TYPE = u'pipe'
#UNO_CONNECTION_TYPE = u'socket'
CONTROL_CHARS = re.compile(r'[\x00-\x1F\x7F-\x9F]', re.UNICODE)
INVALID_FILE_CHARS = re.compile(r'[\\/:\*\?"<>\|\+\[\]%]', re.UNICODE)


class VersionThread(QtCore.QThread):
    """
    A special Qt thread class to fetch the version of OpenLP from the website.
    This is threaded so that it doesn't affect the loading time of OpenLP.
    """
    def run(self):
        """
        Run the thread.
        """
        self.sleep(1)
        log.debug(u'Version thread - run')
        app_version = get_application_version()
        version = check_latest_version(app_version)
        if LooseVersion(str(version)) > LooseVersion(str(app_version[u'full'])):
            Registry().execute(u'openlp_version_check', u'%s' % version)


def _get_frozen_path(frozen_option, non_frozen_option):
    """
    Return a path based on the system status.
    """
    if hasattr(sys, u'frozen') and sys.frozen == 1:
        return frozen_option
    return non_frozen_option


def get_application_version():
    """
    Returns the application version of the running instance of OpenLP::

        {u'full': u'1.9.4-bzr1249', u'version': u'1.9.4', u'build': u'bzr1249'}
    """
    global APPLICATION_VERSION
    if APPLICATION_VERSION:
        return APPLICATION_VERSION
    if u'--dev-version' in sys.argv or u'-d' in sys.argv:
        # If we're running the dev version, let's use bzr to get the version.
        try:
            # If bzrlib is available, use it.
            from bzrlib.branch import Branch
            b = Branch.open_containing('.')[0]
            b.lock_read()
            try:
                # Get the branch's latest revision number.
                revno = b.revno()
                # Convert said revision number into a bzr revision id.
                revision_id = b.dotted_revno_to_revision_id((revno,))
                # Get a dict of tags, with the revision id as the key.
                tags = b.tags.get_reverse_tag_dict()
                # Check if the latest
                if revision_id in tags:
                    full_version = u'%s' % tags[revision_id][0]
                else:
                    full_version = '%s-bzr%s' % (sorted(b.tags.get_tag_dict().keys())[-1], revno)
            finally:
                b.unlock()
        except:
            # Otherwise run the command line bzr client.
            bzr = Popen((u'bzr', u'tags', u'--sort', u'time'), stdout=PIPE)
            output, error = bzr.communicate()
            code = bzr.wait()
            if code != 0:
                raise Exception(u'Error running bzr tags')
            lines = output.splitlines()
            if not lines:
                tag = u'0.0.0'
                revision = u'0'
            else:
                tag, revision = lines[-1].split()
            bzr = Popen((u'bzr', u'log', u'--line', u'-r', u'-1'), stdout=PIPE)
            output, error = bzr.communicate()
            code = bzr.wait()
            if code != 0:
                raise Exception(u'Error running bzr log')
            latest = output.split(u':')[0]
            full_version = latest == revision and tag or u'%s-bzr%s' % (tag, latest)
    else:
        # We're not running the development version, let's use the file.
        filepath = AppLocation.get_directory(AppLocation.VersionDir)
        filepath = os.path.join(filepath, u'.version')
        fversion = None
        try:
            fversion = open(filepath, u'r')
            full_version = unicode(fversion.read()).rstrip()
        except IOError:
            log.exception('Error in version file.')
            full_version = u'0.0.0-bzr000'
        finally:
            if fversion:
                fversion.close()
    bits = full_version.split(u'-')
    APPLICATION_VERSION = {
        u'full': full_version,
        u'version': bits[0],
        u'build': bits[1] if len(bits) > 1 else None
    }
    if APPLICATION_VERSION[u'build']:
        log.info(u'Openlp version %s build %s', APPLICATION_VERSION[u'version'], APPLICATION_VERSION[u'build'])
    else:
        log.info(u'Openlp version %s' % APPLICATION_VERSION[u'version'])
    return APPLICATION_VERSION


def check_latest_version(current_version):
    """
    Check the latest version of OpenLP against the version file on the OpenLP
    site.

    ``current_version``
        The current version of OpenLP.

    **Rules around versions and version files:**

    * If a version number has a build (i.e. -bzr1234), then it is a nightly.
    * If a version number's minor version is an odd number, it is a development release.
    * If a version number's minor version is an even number, it is a stable release.
    """
    version_string = current_version[u'full']
    # set to prod in the distribution config file.
    settings = Settings()
    settings.beginGroup(u'general')
    last_test = settings.value(u'last version test')
    this_test = datetime.now().date()
    settings.setValue(u'last version test', this_test)
    settings.endGroup()
    # Tell the main window whether there will ever be data to display
    Registry().get(u'main_window').version_update_running = last_test != this_test
    if last_test != this_test:
        if current_version[u'build']:
            req = urllib2.Request(u'http://www.openlp.org/files/nightly_version.txt')
        else:
            version_parts = current_version[u'version'].split(u'.')
            if int(version_parts[1]) % 2 != 0:
                req = urllib2.Request(u'http://www.openlp.org/files/dev_version.txt')
            else:
                req = urllib2.Request(u'http://www.openlp.org/files/version.txt')
        req.add_header(u'User-Agent', u'OpenLP/%s' % current_version[u'full'])
        remote_version = None
        try:
            remote_version = unicode(urllib2.urlopen(req, None).read()).strip()
        except IOError:
            log.exception(u'Failed to download the latest OpenLP version file')
        if remote_version:
            version_string = remote_version
    return version_string


def add_actions(target, actions):
    """
    Adds multiple actions to a menu or toolbar in one command.

    ``target``
        The menu or toolbar to add actions to.

    ``actions``
        The actions to be added. An action consisting of the keyword ``None``
        will result in a separator being inserted into the target.
    """
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)


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
        log.debug(u'Generating images filter.')
        formats = [unicode(fmt)
            for fmt in QtGui.QImageReader.supportedImageFormats()]
        visible_formats = u'(*.%s)' % u'; *.'.join(formats)
        actual_formats = u'(*.%s)' % u' *.'.join(formats)
        IMAGES_FILTER = u'%s %s %s' % (translate('OpenLP', 'Image Files'), visible_formats, actual_formats)
    return IMAGES_FILTER


def split_filename(path):
    """
    Return a list of the parts in a given path.
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return path, u''
    else:
        return os.path.split(path)


def clean_filename(filename):
    """
    Removes invalid characters from the given ``filename``.

    ``filename``
        The "dirty" file name to clean.
    """
    if not isinstance(filename, unicode):
        filename = unicode(filename, u'utf-8')
    return INVALID_FILE_CHARS.sub(u'_', CONTROL_CHARS.sub(u'', filename))


def delete_file(file_path_name):
    """
    Deletes a file from the system.

    ``file_path_name``
        The file, including path, to delete.
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


def get_web_page(url, header=None, update_openlp=False):
    """
    Attempts to download the webpage at url and returns that page or None.

    ``url``
        The URL to be downloaded.

    ``header``
        An optional HTTP header to pass in the request to the web server.

    ``update_openlp``
        Tells OpenLP to update itself if the page is successfully downloaded.
        Defaults to False.
    """
    # TODO: Add proxy usage. Get proxy info from OpenLP settings, add to a
    # proxy_handler, build into an opener and install the opener into urllib2.
    # http://docs.python.org/library/urllib2.html
    if not url:
        return None
    req = urllib2.Request(url)
    if header:
        req.add_header(header[0], header[1])
    page = None
    log.debug(u'Downloading URL = %s' % url)
    try:
        page = urllib2.urlopen(req)
        log.debug(u'Downloaded URL = %s' % page.geturl())
    except urllib2.URLError:
        log.exception(u'The web page could not be downloaded')
    if not page:
        return None
    if update_openlp:
        Registry().get(u'application').process_events()
    log.debug(page)
    return page


def get_uno_command():
    """
    Returns the UNO command to launch an openoffice.org instance.
    """
    COMMAND = u'soffice'
    OPTIONS = u'--nologo --norestore --minimized --nodefault --nofirststartwizard'
    if UNO_CONNECTION_TYPE == u'pipe':
        CONNECTION = u'"--accept=pipe,name=openlp_pipe;urp;"'
    else:
        CONNECTION = u'"--accept=socket,host=localhost,port=2002;urp;"'
    return u'%s %s %s' % (COMMAND, OPTIONS, CONNECTION)


def get_uno_instance(resolver):
    """
    Returns a running openoffice.org instance.

    ``resolver``
        The UNO resolver to use to find a running instance.
    """
    log.debug(u'get UNO Desktop Openoffice - resolve')
    if UNO_CONNECTION_TYPE == u'pipe':
        return resolver.resolve(u'uno:pipe,name=openlp_pipe; urp;StarOffice.ComponentContext')
    else:
        return resolver.resolve(u'uno:socket,host=localhost,port=2002; urp;StarOffice.ComponentContext')


def format_time(text, local_time):
    """
    Workaround for Python built-in time formatting function time.strftime().

    time.strftime() accepts only ascii characters. This function accepts
    unicode string and passes individual % placeholders to time.strftime().
    This ensures only ascii characters are passed to time.strftime().

    ``text``
        The text to be processed.

    ``local_time``
        The time to be used to add to the string.  This is a time object
    """
    def match_formatting(match):
        """
        Format the match
        """
        return local_time.strftime(match.group())
    return re.sub('\%[a-zA-Z]', match_formatting, text)


def get_local_key(string):
    """
    Creates a key for case insensitive, locale aware string sorting.
    """
    string = string.lower()
    # For Python 3 on platforms other than Windows ICU is not necessary. In those cases locale.strxfrm(str) can be used.
    global ICU_COLLATOR
    if ICU_COLLATOR is None:
        from languagemanager import LanguageManager
        locale = LanguageManager.get_language()
        icu_locale = icu.Locale(locale)
        ICU_COLLATOR = icu.Collator.createInstance(icu_locale)
    return ICU_COLLATOR.getSortKey(string)


def get_natural_key(string):
    """
    Generate a key for locale aware natural string sorting. Returns a list of strings and integers.

    ``string``
        A string, list or tuple which represents the item string.
    """
    if isinstance(string, basestring):
        string = re.findall(r'(\d+|\D+)', string)
        if len(string) == 1:
            return list(get_local_key(string[0]))
    elif isinstance(string, tuple):
        string = list(string)
    if isinstance(string, list):
        for index, part in enumerate(string):
            if isinstance(part, basestring):
                if part.isdigit():
                    string[index] = int(part)
                else:
                    string[index] = get_local_key(part)
    return string


from applocation import AppLocation
from languagemanager import LanguageManager
from actions import ActionList


__all__ = [u'AppLocation', u'ActionList', u'LanguageManager', u'get_application_version', u'check_latest_version',
    u'add_actions', u'get_filesystem_encoding', u'get_web_page', u'get_uno_command', u'get_uno_instance',
    u'delete_file', u'clean_filename', u'format_time', u'get_local_key', u'get_natural_key']
