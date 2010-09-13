# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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

from opensongimport import OpenSongImport
from olpimport import OpenLPSongImport
from wowimport import WowImport
from cclifileimport import CCLIFileImport
# Imports that might fail
try:
    from olp1import import OpenLP1SongImport
    from sofimport import SofImport
    from oooimport import OooImport
except ImportError:
    pass

class SongFormat(object):
    """
    This is a special enumeration class that holds the various types of songs,
    plus a few helper functions to facilitate generic handling of song types
    for importing.
    """
    _format_availability = {}
    Unknown = -1
    OpenLP2 = 0
    OpenLP1 = 1
    OpenLyrics = 2
    OpenSong = 3
    WordsOfWorship = 4
    CCLI = 5
    SongsOfFellowship = 6
    Generic = 7
    CSV = 8

    @staticmethod
    def get_class(format):
        """
        Return the appropriate imeplementation class.

        ``format``
            The song format.
        """
        if format == SongFormat.OpenLP2:
            return OpenLPSongImport
        if format == SongFormat.OpenLP1:
            return OpenLP1SongImport
        elif format == SongFormat.OpenSong:
            return OpenSongImport
        elif format == SongFormat.SongsOfFellowship:
            return SofImport
        elif format == SongFormat.WordsOfWorship:
            return WowImport
        elif format == SongFormat.Generic:
            return OooImport
        elif format == SongFormat.CCLI:
            return CCLIFileImport
#        else:
        return None

    @staticmethod
    def list():
        """
        Return a list of the supported song formats.
        """
        return [
            SongFormat.OpenLP2,
            SongFormat.OpenLP1,
            SongFormat.OpenLyrics,
            SongFormat.OpenSong,
            SongFormat.WordsOfWorship,
            SongFormat.CCLI,
            SongFormat.SongsOfFellowship,
            SongFormat.Generic
        ]

    @staticmethod
    def set_availability(format, available):
        SongFormat._format_availability[format] = available

    @staticmethod
    def get_availability(format):
        return SongFormat._format_availability.get(format, True)

if u'OpenLP1SongImport' not in locals():
    SongFormat.set_availability(SongFormat.OpenLP1, False)
if u'SofImport' not in locals():
    SongFormat.set_availability(SongFormat.SongsOfFellowship, False)
if u'OooImport' not in locals():
    SongFormat.set_availability(SongFormat.Generic, False)

__all__ = [u'SongFormat']
