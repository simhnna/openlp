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

file_name = "/home/tim/Projects/OpenLP/openlp/remoteweb/deploy.zip"


def deploy_zipfile(file_name):

    app_root = "/home/tim/.openlp/data/remotes/"
    web_zip = zipfile.ZipFile(file_name)
    for web_file in web_zip.namelist():
        (dir_name, filename) = os.path.split(web_file)
        real_path = os.path.join(app_root, web_file[4:])
        if filename == '':
            if not os.path.exists(real_path):
                os.makedirs(real_path)
        else:
            file_web = str(web_zip.read(web_file))
            out_file = open(real_path, 'w')
            out_file.write(file_web)
    web_zip.close()


def check_for_previous_deployment(create=False):
    app_root = "/home/tim/.openlp/data/remotes/"
    marker_file = os.path.join(app_root, "marker.txt")
    if os.path.isfile(marker_file):
        return True
    else:
        if create:
            os.mknod(marker_file)
        return False
    a=1


deploy_zipfile(file_name)
#print(check_for_previous_deployment())
#print(check_for_previous_deployment(True))
#print(check_for_previous_deployment())


    #        xml_file = [name for name in theme_zip.namelist() if os.path.splitext(name)[1].lower() == '.xml']
    #        if len(xml_file) != 1:
    #            self.log_error('Theme contains "{val:d}" XML files'.format(val=len(xml_file)))
     #           raise ValidationError
     #       xml_tree = ElementTree(element=XML(theme_zip.read(xml_file[0]))).getroot()
     #       theme_version = xml_tree.get('version', default=None)
     #       if not theme_version or float(theme_version) < 2.0:
     #           self.log_error('Theme version is less than 2.0')
     #           raise ValidationError
     #       theme_name = xml_tree.find('name').text.strip()
     #       theme_folder = os.path.join(directory, theme_name)
      #      theme_exists = os.path.exists(theme_folder)