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

import os
import zipfile

from openlp.core.common.httputils import url_get_file


def deploy_zipfile(zip_file, app_root):
    """
    Process the downloaded zip file and add to the correct directory

    :param zip_file: the zip file to be processed
    :param app_root: the directory where the zip get expanded to

    :return: None
    """
    web_zip = zipfile.ZipFile(zip_file)
    for web_file in web_zip.namelist():
        (dir_name, filename) = os.path.split(web_file)
        real_path = os.path.join(app_root, web_file[4:])
        if filename == '':
            if not os.path.exists(real_path):
                os.makedirs(real_path)
        else:
            file_web = web_zip.read(web_file)
            out_file = open(real_path, 'w')
            # extract the file from the zip.  If an image then the exception will be used.
            try:
                out_file.write(file_web.decode("utf-8"))
            except UnicodeDecodeError as ude:
                out_file.close()
                out_file = open(real_path, 'wb')
                out_file.write(file_web)
            out_file.close()
    web_zip.close()


def check_for_previous_deployment(app_root, create=False):
    marker_file = os.path.join(app_root, "marker.txt")
    if os.path.isfile(marker_file):
        return True
    else:
        if create:
            os.mknod(marker_file)
        return False


#def download_and_check():
#    f = url_get_file(None, 'https://get.openlp.org/webclient', 'download.cfg')
#    print(f)

#download_and_check()


#file_name = "/home/tim/Projects/OpenLP/openlp/remoteweb/deploy.zip"
#app_root = "/home/tim/.openlp/data/remotes/"

#deploy_zipfile(file_name)
#print(check_for_previous_deployment(app_root))
#print(check_for_previous_deployment(app_root, True))
#print(check_for_previous_deployment(app_root))
