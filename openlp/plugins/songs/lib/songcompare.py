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
The :mod:`songcompare` module provides functionality to search for
duplicate songs. It has one single :function:`songs_probably_equal`.

The algorithm is based on the diff algorithm.
First a diffset is calculated for two songs.
To compensate for typos all differences that are smaller than a
limit (<max_typo_size) and are surrounded by larger equal blocks
(>min_fragment_size) are removed and the surrounding equal parts are merged.
Finally two conditions can qualify a song tuple to be a duplicate:
1. There is a block of equal content that is at least min_block_size large.
   This condition should hit for all larger songs that have a long enough
   equal part. Even if only one verse is equal this condition should still hit.
2. Two thirds of the smaller song is contained in the larger song.
   This condition should hit if one of the two songs (or both) is small (smaller
   than the min_block_size), but most of the song is contained in the other song.
"""
import difflib


MIN_FRAGMENT_SIZE = 5
MIN_BLOCK_SIZE = 70
MAX_TYPO_SIZE = 3


def songs_probably_equal(song1, song2):
    """
    Calculate and return whether two songs are probably equal.

    ``song1``
        The first song to compare.

    ``song2``
        The second song to compare.
    """
    if len(song1.search_lyrics) < len(song2.search_lyrics):
        small = song1.search_lyrics
        large = song2.search_lyrics
    else:
        small = song2.search_lyrics
        large = song1.search_lyrics
    differ = difflib.SequenceMatcher(a=large, b=small)
    diff_tuples = differ.get_opcodes()
    diff_no_typos = _remove_typos(diff_tuples)
    if _length_of_equal_blocks(diff_no_typos) >= MIN_BLOCK_SIZE or \
            _length_of_longest_equal_block(diff_no_typos) > len(small) * 2 / 3:
                return True
    else:
        return False


def _op_length(opcode):
    """
    Return the length of a given difference.

    ``opcode``
        The difference.
    """
    return max(opcode[2] - opcode[1], opcode[4] - opcode[3])


def _remove_typos(diff):
    """
    Remove typos from a diff set. A typo is a small difference (<max_typo_size)
    surrounded by larger equal passages (>min_fragment_size).

    ``diff``
        The diff set to remove the typos from.
    """
    # Remove typo at beginning of the string.
    if len(diff) >= 2:
        if diff[0][0] != "equal" and _op_length(diff[0]) <= MAX_TYPO_SIZE and \
                _op_length(diff[1]) >= MIN_FRAGMENT_SIZE:
                    del diff[0]
    # Remove typos in the middle of the string.
    if len(diff) >= 3:
        for index in range(len(diff) - 3, -1, -1):
            if _op_length(diff[index]) >= MIN_FRAGMENT_SIZE and \
                diff[index + 1][0] != "equal" and _op_length(diff[index + 1]) <= MAX_TYPO_SIZE and \
                    _op_length(diff[index + 2]) >= MIN_FRAGMENT_SIZE:
                        del diff[index + 1]
    # Remove typo at the end of the string.
    if len(diff) >= 2:
        if _op_length(diff[-2]) >= MIN_FRAGMENT_SIZE and \
            diff[-1][0] != "equal" and _op_length(diff[-1]) <= MAX_TYPO_SIZE:
                del diff[-1]

    # Merge the bordering equal passages that occured by removing differences.
    for index in range(len(diff) - 2, -1, -1):
        if diff[index][0] == "equal" and _op_length(diff[index]) >= MIN_FRAGMENT_SIZE and \
            diff[index + 1][0] == "equal" and _op_length(diff[index + 1]) >= MIN_FRAGMENT_SIZE:
                diff[index] = ("equal", diff[index][1], diff[index + 1][2], diff[index][3],
                    diff[index + 1][4])
                del diff[index + 1]

    return diff


def _length_of_equal_blocks(diff):
    """
    Return the total length of all equal blocks in a diff set.
    Blocks smaller than min_block_size are not counted.

    ``diff``
        The diff set to return the length for.
    """
    length = 0
    for element in diff:
        if element[0] == "equal" and _op_length(element) >= MIN_BLOCK_SIZE:
            length += _op_length(element)
    return length


def _length_of_longest_equal_block(diff):
    """
    Return the length of the largest equal block in a diff set.

    ``diff``
        The diff set to return the length for.
    """
    length = 0
    for element in diff:
        if element[0] == "equal" and _op_length(element) > length:
            length = _op_length(element)
    return length
