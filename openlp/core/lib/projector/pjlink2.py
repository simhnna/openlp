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
    :mod:`openlp.core.lib.projector.pjlink2` module provides the PJLink Class 2
    updates from PJLink Class 1.

    This module only handles the UDP socket functionality. Command/query/status
    change messages will still be processed by the PJLink 1 module.

    Currently, the only variance is the addition of a UDP "search" command to
    query the local network for Class 2 capable projectors,
    and UDP "notify" messages from projectors to connected software of status
    changes (i.e., power change, input change, error changes).

    Differences between Class 1 and Class 2 PJLink specifications are as follows.

    New Functionality:
        * Search - UDP Query local network for Class 2 capabable projector(s).
        * Status - UDP Status change with connected projector(s). Status change
            messages consist of:
            * Initial projector power up when network communication becomes available
            * Lamp off/standby to warmup or on
            * Lamp on to cooldown or off/standby
            * Input source select change completed
            * Error status change (i.e., fan/lamp/temp/cover open/filter/other error(s))

    New Commands:
        * Query serial number of projector
        * Query version number of projector software
        * Query model number of replacement lamp
        * Query model number of replacement air filter
        * Query current projector screen resolution
        * Query recommended screen resolution
        * Query name of specific input terminal (video source)
        * Adjust projector microphone in 1-step increments
        * Adjust projector speacker in 1-step increments

    Extended Commands:
        * Addition of INTERNAL terminal (video source) for a total of 6 types of terminals.
        * Number of terminals (video source) has been expanded from [1-9]
            to [1-9a-z] (Addition of 26 terminals for each type of input).

    See PJLink Class 2 Specifications for details.
    http://pjlink.jbmia.or.jp/english/dl_class2.html

        Section 5-1 PJLink Specifications

        Section 5-5 Guidelines for Input Terminals
"""
import logging
log = logging.getLogger(__name__)

log.debug('pjlink2 loaded')

from PyQt5 import QtNetwork


class PJLinkUDP(QtNetwork.QUdpSocket):
    """
    Socket service for handling datagram (UDP) sockets.
    """
    log.debug('PJLinkUDP loaded')
    # Class varialbe for projector list. Should be replaced by ProjectorManager's
    # projector list after being loaded there.
    projector_list = None
    projectors_found = None  # UDP search found list
