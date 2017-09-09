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
The :mod:`openlp.core.version` module downloads the version details for OpenLP.
"""
import logging
import os
import platform
import sys
from datetime import datetime
from distutils.version import LooseVersion
from subprocess import Popen, PIPE

import requests
from PyQt5 import QtCore

from openlp.core.common import AppLocation, Settings
from openlp.core.threading import run_thread

log = logging.getLogger(__name__)

APPLICATION_VERSION = {}
CONNECTION_TIMEOUT = 30
CONNECTION_RETRIES = 2


class VersionWorker(QtCore.QObject):
    """
    A worker class to fetch the version of OpenLP from the website. This is run from within a thread so that it
    doesn't affect the loading time of OpenLP.
    """
    new_version = QtCore.pyqtSignal(dict)
    no_internet = QtCore.pyqtSignal()
    quit = QtCore.pyqtSignal()

    def __init__(self, last_check_date):
        """
        Constructor for the version check worker.

        :param string last_check_date: The last day we checked for a new version of OpenLP
        """
        log.debug('VersionWorker - Initialise')
        super(VersionWorker, self).__init__(None)
        self.last_check_date = last_check_date

    def start(self):
        """
        Check the latest version of OpenLP against the version file on the OpenLP site.

        **Rules around versions and version files:**

        * If a version number has a build (i.e. -bzr1234), then it is a nightly.
        * If a version number's minor version is an odd number, it is a development release.
        * If a version number's minor version is an even number, it is a stable release.
        """
        log.debug('VersionWorker - Start')
        # I'm not entirely sure why this was here, I'm commenting it out until I hit the same scenario
        # time.sleep(1)
        current_version = get_version()
        download_url = 'http://www.openlp.org/files/version.txt'
        if current_version['build']:
            download_url = 'http://www.openlp.org/files/nightly_version.txt'
        elif int(current_version['version'].split('.')[1]) % 2 != 0:
            download_url = 'http://www.openlp.org/files/dev_version.txt'
        headers = {
            'User-Agent', 'OpenLP/{version} {system}/{release}; '.format(version=current_version['full'],
                                                                         system=platform.system(),
                                                                         release=platform.release())
        }
        remote_version = None
        retries = 0
        while retries < 3:
            try:
                response = requests.get(download_url, headers=headers)
                remote_version = response.text
                log.debug('New version found: %s', remote_version)
                break
            except requests.exceptions.ConnectionError:
                log.exception('Unable to connect to OpenLP server to download version file')
                self.no_internet.emit()
                retries += 1
            except requests.exceptions.RequestException:
                log.exception('Error occurred while connecting to OpenLP server to download version file')
                retries += 1
        if remote_version and LooseVersion(remote_version) > LooseVersion(current_version['full']):
            self.new_version.emit(remote_version)
        self.quit.emit()


def check_for_update(parent):
    """
    Run a thread to download and check the version of OpenLP

    :param MainWindow parent: The parent object for the thread. Usually the OpenLP main window.
    """
    last_check_date = Settings().value('core/last version test')
    if datetime.date().strftime('%Y-%m-%d') <= last_check_date:
        log.debug('Version check skipped, last checked today')
        return
    worker = VersionWorker(last_check_date)
    worker.new_version.connect(parent.on_new_version)
    # TODO: Use this to figure out if there's an Internet connection?
    # worker.no_internet.connect(parent.on_no_internet)
    run_thread(parent, worker, 'version')


def get_version():
    """
    Returns the application version of the running instance of OpenLP::

        {'full': '1.9.4-bzr1249', 'version': '1.9.4', 'build': 'bzr1249'}
    """
    global APPLICATION_VERSION
    if APPLICATION_VERSION:
        return APPLICATION_VERSION
    if '--dev-version' in sys.argv or '-d' in sys.argv:
        # NOTE: The following code is a duplicate of the code in setup.py. Any fix applied here should also be applied
        # there.

        # Get the revision of this tree.
        bzr = Popen(('bzr', 'revno'), stdout=PIPE)
        tree_revision, error = bzr.communicate()
        tree_revision = tree_revision.decode()
        code = bzr.wait()
        if code != 0:
            raise Exception('Error running bzr log')

        # Get all tags.
        bzr = Popen(('bzr', 'tags'), stdout=PIPE)
        output, error = bzr.communicate()
        code = bzr.wait()
        if code != 0:
            raise Exception('Error running bzr tags')
        tags = list(map(bytes.decode, output.splitlines()))
        if not tags:
            tag_version = '0.0.0'
            tag_revision = '0'
        else:
            # Remove any tag that has "?" as revision number. A "?" as revision number indicates, that this tag is from
            # another series.
            tags = [tag for tag in tags if tag.split()[-1].strip() != '?']
            # Get the last tag and split it in a revision and tag name.
            tag_version, tag_revision = tags[-1].split()
        # If they are equal, then this tree is tarball with the source for the release. We do not want the revision
        # number in the full version.
        if tree_revision == tag_revision:
            full_version = tag_version.strip()
        else:
            full_version = '{tag}-bzr{tree}'.format(tag=tag_version.strip(), tree=tree_revision.strip())
    else:
        # We're not running the development version, let's use the file.
        file_path = str(AppLocation.get_directory(AppLocation.VersionDir))
        file_path = os.path.join(file_path, '.version')
        version_file = None
        try:
            version_file = open(file_path, 'r')
            full_version = str(version_file.read()).rstrip()
        except IOError:
            log.exception('Error in version file.')
            full_version = '0.0.0-bzr000'
        finally:
            if version_file:
                version_file.close()
    bits = full_version.split('-')
    APPLICATION_VERSION = {
        'full': full_version,
        'version': bits[0],
        'build': bits[1] if len(bits) > 1 else None
    }
    if APPLICATION_VERSION['build']:
        log.info('Openlp version {version} build {build}'.format(version=APPLICATION_VERSION['version'],
                                                                 build=APPLICATION_VERSION['build']))
    else:
        log.info('Openlp version {version}'.format(version=APPLICATION_VERSION['version']))
    return APPLICATION_VERSION
