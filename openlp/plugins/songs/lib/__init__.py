# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Jonathan Corwin, Michael      #
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

from PyQt4 import QtGui
from openlp.core.lib import translate

class VerseType(object):
    """
    VerseType provides an enumeration for the tags that may be associated
    with verses in songs.
    """
    Verse = 0
    Chorus = 1
    Bridge = 2
    PreChorus = 3
    Intro = 4
    Ending = 5
    Other = 6

    @staticmethod
    def to_string(verse_type):
        """
        Return a string for a given VerseType

        ``verse_type``
            The type to return a string for
        """
        if verse_type == VerseType.Verse:
            return translate('SongsPlugin.VerseType', 'Verse')
        elif verse_type == VerseType.Chorus:
            return translate('SongsPlugin.VerseType', 'Chorus')
        elif verse_type == VerseType.Bridge:
            return translate('SongsPlugin.VerseType', 'Bridge')
        elif verse_type == VerseType.PreChorus:
            return translate('SongsPlugin.VerseType', 'Pre-Chorus')
        elif verse_type == VerseType.Intro:
            return translate('SongsPlugin.VerseType', 'Intro')
        elif verse_type == VerseType.Ending:
            return translate('SongsPlugin.VerseType', 'Ending')
        elif verse_type == VerseType.Other:
            return translate('SongsPlugin.VerseType', 'Other')

    @staticmethod
    def expand_string(verse_type):
        """
        Return the VerseType for a given string

        ``verse_type``
            The string to return a VerseType for
        """
        verse_type = verse_type.lower()
        if verse_type == \
            unicode(VerseType.to_string(VerseType.Verse)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'Verse')
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Chorus)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'Chorus')
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Bridge)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'Bridge')
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.PreChorus)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'PreChorus')
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Intro)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'Intro')
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Ending)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'Ending')
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Other)).lower()[0]:
            return translate('SongsPlugin.VerseType', 'Other')

    @staticmethod
    def from_string(verse_type):
        """
        Return the VerseType for a given string

        ``verse_type``
            The string to return a VerseType for
        """
        verse_type = verse_type.lower()
        if verse_type == unicode(VerseType.to_string(VerseType.Verse)).lower():
            return VerseType.Verse
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Chorus)).lower():
            return VerseType.Chorus
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Bridge)).lower():
            return VerseType.Bridge
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.PreChorus)).lower():
            return VerseType.PreChorus
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Intro)).lower():
            return VerseType.Intro
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Ending)).lower():
            return VerseType.Ending
        elif verse_type == \
            unicode(VerseType.to_string(VerseType.Other)).lower():
            return VerseType.Other


def retrieve_windows_encoding(recommendation=None):
    # map chardet result to compatible windows standard code page
    codepage_mapping = {'IBM866': u'cp866', 'TIS-620': u'cp874',
        'SHIFT_JIS': u'cp932', 'GB2312': u'cp936', 'HZ-GB-2312': u'cp936',
        'EUC-KR': u'cp949', 'Big5': u'cp950', 'ISO-8859-2': u'cp1250',
        'windows-1250': u'cp1250', 'windows-1251': u'cp1251',
        'windows-1252': u'cp1252', 'ISO-8859-7': u'cp1253',
        'windows-1253': u'cp1253', 'ISO-8859-8': u'cp1255',
        'windows-1255': u'cp1255'}
    if recommendation in codepage_mapping:
        recommendation = codepage_mapping[recommendation]

    # Show dialog for encoding selection
    encodings = [(u'cp1256', translate('SongsPlugin', 'Arabic (CP-1256)')),
        (u'cp1257', translate('SongsPlugin', 'Baltic (CP-1257)')),
        (u'cp1250', translate('SongsPlugin', 'Central European (CP-1250)')),
        (u'cp1251', translate('SongsPlugin', 'Cyrillic (CP-1251)')),
        (u'cp1253', translate('SongsPlugin', 'Greek (CP-1253)')),
        (u'cp1255', translate('SongsPlugin', 'Hebrew (CP-1255)')),
        (u'cp932', translate('SongsPlugin', 'Japanese (CP-932)')),
        (u'cp949', translate('SongsPlugin', 'Korean (CP-949)')),
        (u'cp936', translate('SongsPlugin', 'Simplified Chinese (CP-936)')),
        (u'cp874', translate('SongsPlugin', 'Thai (CP-874)')),
        (u'cp950', translate('SongsPlugin', 'Traditional Chinese (CP-950)')),
        (u'cp1254', translate('SongsPlugin', 'Turkish (CP-1254)')),
        (u'cp1258', translate('SongsPlugin', 'Vietnam (CP-1258)')),
        (u'cp1252', translate('SongsPlugin', 'Western European (CP-1252)'))]
    recommended_index = -1
    if recommendation:
        for index in range(len(encodings)):
            if recommendation == encodings[index][0]:
                recommended_index = index
                break
    if recommended_index > 0:
        choice = QtGui.QInputDialog.getItem(None,
            translate('SongsPlugin', 'Character Encoding'),
            translate('SongsPlugin', 'The codepage setting is responsible\n'
                'for the correct character representation.\n'
                'Usually you are fine with the preselected choise.'),
            [pair[1] for pair in encodings], recommended_index, False)
    else:
        choice = QtGui.QInputDialog.getItem(None,
            translate('SongsPlugin', 'Character Encoding'),
            translate('SongsPlugin', 'Please choose the character encoding.\n'
                'The encoding is responsible for the correct character '
                'representation.'), [pair[1] for pair in encodings], 0, False)
    if not choice[1]:
        return None
    return filter(lambda item: item[1] == choice[0], encodings)[0][0]

from xml import LyricsXML, SongXMLBuilder, SongXMLParser, OpenLyricsParser
from songstab import SongsTab
from mediaitem import SongMediaItem
