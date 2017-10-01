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
Download and "install" the remote web client
"""
import os
from zipfile import ZipFile

from openlp.core.common import AppLocation, Registry
from openlp.core.common.httputils import url_get_file, get_web_page, get_url_file_size


def deploy_zipfile(app_root, zip_name):
    """
    Process the downloaded zip file and add to the correct directory

    :param zip_name: the zip file to be processed
    :param app_root: the directory where the zip get expanded to

    :return: None
    """
    zip_file = os.path.join(app_root, zip_name)
    web_zip = ZipFile(zip_file)
    web_zip.extractall(app_root)


def download_sha256():
    """
    Download the config file to extract the sha256 and version number
    """
    user_agent = 'OpenLP/' + Registry().get('application').applicationVersion()
    try:
        web_config = get_web_page('https://get.openlp.org/webclient/download.cfg', headers={'User-Agent': user_agent})
    except ConnectionError:
        return False
    file_bits = web_config.split()
    return file_bits[0], file_bits[2]


def download_and_check(callback=None):
    """
    Download the web site and deploy it.
    """
    sha256, version = download_sha256()
    file_size = get_url_file_size('https://get.openlp.org/webclient/site.zip')
    callback.setRange(0, file_size)
    if url_get_file(callback, 'https://get.openlp.org/webclient/site.zip',
                    AppLocation.get_section_data_path('remotes') / 'site.zip',
                    sha256=sha256):
        deploy_zipfile(str(AppLocation.get_section_data_path('remotes')), 'site.zip')
