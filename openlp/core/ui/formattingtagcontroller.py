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
The :mod:`formattingtagform` provides an Tag Edit facility. The Base set are protected and included each time loaded.
Custom tags can be defined and saved. The Custom Tag arrays are saved in a pickle so QSettings works on them. Base Tags
cannot be changed.
"""

import re

from openlp.core.lib import FormattingTags, translate


class FormattingTagController(object):
    """
    The :class:`FormattingTagController` manages the non UI functions .
    """
    def __init__(self):
        """
        Initiator
        """
        self.html_tag_regex = re.compile(r'<(?:(?P<close>/(?=[^\s/>]+>))?'
        r'(?P<tag>[^\s/!\?>]+)(?:\s+[^\s=]+="[^"]*")*\s*(?P<empty>/)?'
        r'|(?P<cdata>!\[CDATA\[(?:(?!\]\]>).)*\]\])'
        r'|(?P<procinst>\?(?:(?!\?>).)*\?)'
        r'|(?P<comment>!--(?:(?!-->).)*--))>', re.UNICODE)
        self.html_regex = re.compile(r'^(?:[^<>]*%s)*[^<>]*$' % self.html_tag_regex.pattern)

    def pre_save(self):
        """
        Cleanup the array before save validation runs
        """
        self.protected_tags = [tag for tag in FormattingTags.html_expands if tag.get(u'protected')]
        self.custom_tags = []

    def validate_for_save(self, desc, tag, start_html, end_html):
        """
        Validate a custom tag and add to the tags array if valid..

        `description`
            Explanation of the tag.

        `tag`
            The tag in the song used to mark the text.

        `start_html`
            The start html tag.

        `end_html`
            The end html tag.

        """
        if not desc:
            pass
        print desc
        print self.start_html_to_end_html(start_html)

    def _strip(self, tag):
        """
        Remove tag wrappers for editing.
        """
        tag = tag.replace(u'{', u'')
        tag = tag.replace(u'}', u'')
        return tag

    def start_html_to_end_html(self, start_html):
        """
        Return the end HTML for a given start HTML or None if invalid.

        `start_html`
            The start html tag.

        """
        end_tags = []
        match = self.html_regex.match(start_html)
        if match:
            match = self.html_tag_regex.search(start_html)
            while match:
                if match.group(u'tag'):
                    tag = match.group(u'tag').lower()
                    if match.group(u'close'):
                        if match.group(u'empty') or not end_tags or end_tags.pop() != tag:
                            return
                    elif not match.group(u'empty'):
                        end_tags.append(tag)
                match = self.html_tag_regex.search(start_html, match.end())
            return u''.join(map(lambda tag: u'</%s>' % tag, reversed(end_tags)))

    def start_tag_changed(self, start_html, end_html):
        """
        Validate the HTML tags when the start tag has been changed.

        `start_html`
            The start html tag.

        `end_html`
            The end html tag.

        """
        end = self.start_html_to_end_html(start_html)
        if not end_html:
            if not end:
                return translate('OpenLP.FormattingTagForm', 'Start tag %s is not valid HTML' % start_html), None
            return None, end
        return None, None

    def end_tag_changed(self, start_html, end_html):
        """
        Validate the HTML tags when the end tag has been changed.

        `start_html`
            The start html tag.

        `end_html`
            The end html tag.

        """
        end = self.start_html_to_end_html(start_html)
        if not end_html:
            return None, end
        if end and end != end_html:
            return translate('OpenLP.FormattingTagForm',
                'End tag %s does not match end tag for start tag %s' % (end, start_html)), None
        return None, None