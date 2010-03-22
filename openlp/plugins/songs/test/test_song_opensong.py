# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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
import sys

__ThisDir__ = os.path.dirname(__file__)
if "" == __ThisDir__ :
    __ThisDir__ = os.path.abspath(u'.')

sys.path.append(os.path.abspath(u'%s/../../../..'%__ThisDir__))

from openlp.plugins.songs.lib.songxml import *


_sample1 = \
'''<?xml version="1.0" encoding="UTF-8"?>
<song>
  <title></title>
  <author></author>
  <copyright></copyright>
  <presentation></presentation>
  <ccli></ccli>
  <theme></theme>
  <lyrics>[V1]
. chord line 1
 verse 1 line 1
. chord line 2
 verse 1 line 2

[V2]
 verse 2 line 1
 verse 2 line 2

[V3]
 verse 3 line 1
 verse 3 line 2

[C]
. chorus chord line 1
 chorus line 1
. chorus chord line 2
 chorus line 2</lyrics>
</song>
'''

_sample2 = \
'''<?xml version="1.0" encoding="UTF-8"?>
<song>
  <title></title>
  <author></author>
  <copyright></copyright>
  <presentation></presentation>
  <ccli></ccli>
  <theme></theme>
  <lyrics>[V]
1verse 1 line 1
2verse 2 line 1
3verse 3 line 1
1verse 1 line 2
2verse 2 line 2
3verse 3 line 2

[C]
 chorus line 1
 chorus line 2</lyrics>
</song>
'''

_sample3 = \
'''<?xml version="1.0" encoding="UTF-8"?>
<song>
  <title></title>
  <author></author>
  <copyright></copyright>
  <presentation></presentation>
  <ccli></ccli>
  <theme></theme>
  <lyrics>[V]
1verse 1 line 1
2verse 2 line 1
3verse 3 line 1
1verse 1 line 2
2verse 2 line 2
3verse 3 line 2

[C]
 chorus line 1
 chorus line 2

[P]
 pre-chorus line 1
 pre-chorus line 2
 pre-chorus line 3

[B]
 bridge line 1
 bridge line 2
</lyrics>
</song>
'''

class Test_OpenSong(object):
    """Test cases for converting from OpenSong xml format to Song"""

    def test_sample1(self):
        """OpenSong: handwritten sample1"""
        s = Song()
        s.from_opensong_buffer(_sample1)
        l = s.get_lyrics()
        assert(len(l) == (4*3+3))
        assert(s.get_number_of_slides() == 4)

    def test_sample2(self):
        """OpenSong: handwritten sample2 - with verses and chorus"""
        s = Song()
        s.from_opensong_buffer(_sample2)
        l = s.get_lyrics()
        assert(len(l) == (4*3+3))
        assert(s.get_number_of_slides() == 4)

    def test_sample3(self):
        """OpenSong: handwritten sample3 - with verses, chorus, bridge and pre-chorus"""
        s = Song()
        s.from_opensong_buffer(_sample3)
        l = s.get_lyrics()
        assert(len(l) == (4*3+4+5+4))
        assert(s.get_number_of_slides() == 6)

    def test_file1(self):
        """OpenSong: parse Amazing Grace"""
        global __ThisDir__
        s = Song()
        s.from_opensong_file(u'%s/data_opensong/Amazing Grace'%(__ThisDir__))
        assert(s.get_title() == 'Amazing Grace')
        assert(s.get_copyright() == '1982 Jubilate Hymns Limited')
        assert(s.get_song_cclino() == '1037882')
        assert(s.get_category_array(True) == 'God: Attributes')
        assert(s.get_author_list(True) == 'John Newton')
        assert(s.get_verse_order() == '')
        assert(s.get_number_of_slides() == 4)

    def test_file2(self):
        """OpenSong: parse The Solid Rock"""
        s = Song()
        s.from_opensong_file(u'%s/data_opensong/The Solid Rock'%(__ThisDir__))
        assert(s.get_title() == 'The Solid Rock')
        assert(s.get_copyright() == 'Public Domain')
        assert(s.get_song_cclino() == '101740')
        assert(s.get_category_array(True) == 'Christ: Victory, Fruit: Peace/Comfort')
        assert(s.get_author_list(True) == 'Edward Mote, John B. Dykes')
        assert(s.get_verse_order() == 'V1 C V2 C V3 C V4 C')
        assert(s.get_number_of_slides() == 5)

    def test_file3(self):
        """OpenSong: parse 'På en fjern ensom høj' (danish)"""
        #FIXME: problem with XML convert and danish characters
        s = Song()
        s.from_opensong_file(u'%s/data_opensong/På en fjern ensom høj'%(__ThisDir__))
        assert(s.get_title() == u'På en fjern ensom høj')
        assert(s.get_copyright() == '')
        assert(s.get_song_cclino() == '')
        assert(s.get_category_array(True) == '')
        assert(s.get_author_list(True) == '')
        assert(s.get_verse_order() == 'V1 C1 V2 C2 V3 C3 V4 C4')
        assert(s.get_number_of_slides() == 8)

if '__main__' == __name__:
    r = Test_OpenSong()
    r.test_file3()
