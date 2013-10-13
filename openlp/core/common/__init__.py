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
The :mod:`common` module contains most of the components and libraries that make
OpenLP work.
"""
import os
import logging
import sys

log = logging.getLogger(__name__)


def check_directory_exists(directory, do_not_log=False):
    """
    Check a theme directory exists and if not create it

    ``directory``
        The directory to make sure exists

    ``do_not_log``
        To not log anything. This is need for the start up, when the log isn't ready.
    """
    if not do_not_log:
        log.debug('check_directory_exists %s' % directory)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except IOError:
        pass


def get_frozen_path(frozen_option, non_frozen_option):
    """
    Return a path based on the system status.
    """
    if hasattr(sys, 'frozen') and sys.frozen == 1:
        return frozen_option
    return non_frozen_option

from .applocation import AppLocation
