# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,    #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund             #
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
The :mod:`customxmlhandler` module provides the XML functionality for custom
slides

The basic XML is of the format::

    <?xml version="1.0" encoding="UTF-8"?>
    <song version="1.0">
        <lyrics language="en">
            <verse type="chorus" label="1">
                <![CDATA[ ... ]]>
            </verse>
        </lyrics>
    </song>
"""

import logging

from xml.dom.minidom import Document
from xml.etree.ElementTree import dump
from lxml import etree, objectify

log = logging.getLogger(__name__)

class CustomXMLBuilder(object):
    """
    This class builds the XML used to describe songs.
    """
    log.info(u'CustomXMLBuilder Loaded')

    def __init__(self):
        """
        Set up the custom builder.
        """
        # Create the minidom document
        self.custom_xml = Document()

    def new_document(self):
        """
        Create a new custom XML document.
        """
        # Create the <song> base element
        self.song = self.custom_xml.createElement(u'song')
        self.custom_xml.appendChild(self.song)
        self.song.setAttribute(u'version', u'1.0')

    def add_lyrics_to_song(self):
        """
        Set up and add a ``<lyrics>`` tag which contains the lyrics of the
        custom item.
        """
        # Create the main <lyrics> element
        self.lyrics = self.custom_xml.createElement(u'lyrics')
        self.lyrics.setAttribute(u'language', u'en')
        self.song.appendChild(self.lyrics)

    def add_verse_to_lyrics(self, type, number, content):
        """
        Add a verse to the ``<lyrics>`` tag.

        ``type``
            A string denoting the type of verse. Possible values are "Chorus",
            "Verse", "Bridge", and "Custom".

        ``number``
            An integer denoting the number of the item, for example: verse 1.

        ``content``
            The actual text of the verse to be stored.
        """
        verse = self.custom_xml.createElement(u'verse')
        verse.setAttribute(u'type', type)
        verse.setAttribute(u'label', number)
        self.lyrics.appendChild(verse)
        # add data as a CDATA section to protect the XML from special chars
        cds = self.custom_xml.createCDATASection(content)
        verse.appendChild(cds)

    def _dump_xml(self):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return self.custom_xml.toprettyxml(indent=u'  ')

    def extract_xml(self):
        """
        Extract our newly created XML custom.
        """
        return self.custom_xml.toxml(u'utf-8')


class CustomXMLParser(object):
    """
    A class to read in and parse a custom's XML.
    """
    log.info(u'CustomXMLParser Loaded')

    def __init__(self, xml):
        """
        Set up our custom XML parser.

        ``xml``
            The XML of the custom to be parsed.
        """
        self.custom_xml = None
        if xml[:5] == u'<?xml':
            xml = xml[38:]
        try:
            self.custom_xml = objectify.fromstring(xml)
        except etree.XMLSyntaxError:
            log.exception(u'Invalid xml %s', xml)

    def get_verses(self):
        """
        Iterates through the verses in the XML and returns a list of verses
        and their attributes.
        """
        xml_iter = self.custom_xml.getiterator()
        verse_list = []
        for element in xml_iter:
            if element.tag == u'verse':
                if element.text is None:
                    element.text = u''
                verse_list.append([element.attrib, unicode(element.text)])
        return verse_list

    def _dump_xml(self):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return dump(self.custom_xml)
