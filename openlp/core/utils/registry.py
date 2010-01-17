# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2009 Raoul Snyman                                        #
# Portions copyright (c) 2008-2009 Martin Thompson, Tim Bentley, Carsten      #
# Tinggaard, Jon Tibble, Jonathan Corwin, Maikel Stuivenberg, Scott Guerrieri #
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

from ConfigParser import SafeConfigParser

class Registry(object):
    """
    The Registry class is a high-level class for working with a configuration
    file.
    """
    def __init__(self, dir):
        self.config = SafeConfigParser()
        self.file_name = os.path.join(dir, u'openlp.conf')
        self._load()

    def has_value(self, section, key):
        """
        Check if a value exists.
        """
        return self.config.has_option(section, key)

    def get_value(self, section, key, default=None):
        """
        Get a single value from the registry.
        """
        try:
            if self.config.get(section, key):
                return self.config.get(section, key)
            else:
                return default
        except:
            return default

    def set_value(self, section, key, value):
        """
        Set a single value in the registry.
        """
        try :
            self.config.set(section, key, unicode(value))
            return self._save()
        except:
            return False

    def delete_value(self, section, key):
        """
        Delete a single value from the registry.
        """
        try:
            self.config.remove_option(section, key)
            return self._save()
        except:
            return False

    def has_section(self, section):
        """
        Check if a section exists.
        """
        return self.config.has_section(section)

    def create_section(self, section):
        """
        Create a new section in the registry.
        """
        try:
            self.config.add_section(section)
            return self._save()
        except:
            return False

    def delete_section(self, section):
        """
        Delete a section (including all values).
        """
        try:
            self.config.remove_section(section)
            return self._save()
        except:
            return False

    def _load(self):
        file_handle = None
        try:
            if not os.path.isfile(self.file_name):
                return False
            file_handle = open(self.file_name, u'r')
            self.config.readfp(file_handle)
            return True
        except:
            return False
        finally:
            if file_handle:
                file_handle.close()

    def _save(self):
        file_handle = None
        try:
            if not os.path.exists(os.path.dirname(self.file_name)):
                os.makedirs(os.path.dirname(self.file_name))
            file_handle = open(self.file_name, u'w')
            self.config.write(file_handle)
            return self._load()
        except:
            return False
        finally:
            if file_handle:
                file_handle.close()
