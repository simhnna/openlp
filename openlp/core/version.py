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
The :mod:`openlp.core.version` module downloads the version details for OpenLP.
"""
import logging
import platform
import sys
import time
from datetime import date
from distutils.version import LooseVersion
from subprocess import Popen, PIPE

import requests
from PyQt5 import QtCore

from openlp.core.common.applocation import AppLocation
from openlp.core.common.settings import Settings
from openlp.core.threading import ThreadWorker, run_thread

log = logging.getLogger(__name__)

APPLICATION_VERSION = {}
CONNECTION_TIMEOUT = 30
CONNECTION_RETRIES = 2


class VersionWorker(ThreadWorker):
    """
    A worker class to fetch the version of OpenLP from the website. This is run from within a thread so that it
    doesn't affect the loading time of OpenLP.
    """
    new_version = QtCore.pyqtSignal(dict)
    no_internet = QtCore.pyqtSignal()

    def __init__(self, last_check_date, current_version):
        """
        Constructor for the version check worker.

        :param string last_check_date: The last day we checked for a new version of OpenLP
        """
        log.debug('VersionWorker - Initialise')
        super(VersionWorker, self).__init__(None)
        self.last_check_date = last_check_date
        self.current_version = current_version

    def start(self):
        """
        Check the latest version of OpenLP against the version file on the OpenLP site.

        **Rules around versions and version files:**

        * If a version number has a build (i.e. -bzr1234), then it is a nightly.
        * If a version number's minor version is an odd number, it is a development release.
        * If a version number's minor version is an even number, it is a stable release.
        """
        log.debug('VersionWorker - Start')
        download_url = 'https://www.openlp.org/files/version.txt'
        if self.current_version['build']:
            download_url = 'https://www.openlp.org/files/nightly_version.txt'
        elif int(self.current_version['version'].split('.')[1]) % 2 != 0:
            download_url = 'https://www.openlp.org/files/dev_version.txt'
        headers = {
            'User-Agent': 'OpenLP/{version} {system}/{release}; '.format(version=self.current_version['full'],
                                                                         system=platform.system(),
                                                                         release=platform.release())
        }
        remote_version = None
        retries = 0
        while retries < 3:
            try:
                response = requests.get(download_url, headers=headers)
                remote_version = response.text.strip()
                log.debug('New version found: %s', remote_version)
                break
            except OSError:
                log.exception('Unable to connect to OpenLP server to download version file')
                retries += 1
        else:
            self.no_internet.emit()
        if remote_version and LooseVersion(remote_version) > LooseVersion(self.current_version['full']):
            self.new_version.emit(remote_version)
        self.quit.emit()


def update_check_date():
    """
    Save when we last checked for an update
    """
    Settings().setValue('core/last version test', date.today().strftime('%Y-%m-%d'))


def check_for_update(main_window):
    """
    Run a thread to download and check the version of OpenLP

    :param MainWindow main_window: The OpenLP main window.
    """
    last_check_date = Settings().value('core/last version test')
    if date.today().strftime('%Y-%m-%d') <= last_check_date:
        log.debug('Version check skipped, last checked today')
        return
    worker = VersionWorker(last_check_date, get_version())
    worker.new_version.connect(main_window.on_new_version)
    worker.quit.connect(update_check_date)
    # TODO: Use this to figure out if there's an Internet connection?
    # worker.no_internet.connect(parent.on_no_internet)
    run_thread(worker, 'version')


def get_version():
    """
    Returns the application version of the running instance of OpenLP::

        {'full': '1.9.4-bzr1249', 'version': '1.9.4', 'build': 'bzr1249'}
    """
    global APPLICATION_VERSION
    if APPLICATION_VERSION:
        return APPLICATION_VERSION
    file_path = AppLocation.get_directory(AppLocation.VersionDir) / '.version'
    try:
        full_version = file_path.read_text().rstrip()
    except OSError:
        log.exception('Error in version file.')
        full_version = '0.0.0-bzr000'
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
