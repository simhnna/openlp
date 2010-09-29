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
"""
The :mod:`serviceitem` provides the service item functionality including the
type and capability of an item.
"""

import logging
import os
import time
import uuid

from PyQt4 import QtGui

from openlp.core.lib import build_icon, resize_image, clean_tags, expand_tags

log = logging.getLogger(__name__)

class ServiceItemType(object):
    """
    Defines the type of service item
    """
    Text = 1
    Image = 2
    Command = 3

class ItemCapabilities(object):
    """
    Provides an enumeration of a serviceitem's capabilities
    """
    AllowsPreview = 1
    AllowsEdit = 2
    AllowsMaintain = 3
    RequiresMedia = 4
    AllowsLoop = 5
    AllowsAdditions = 6
    NoLineBreaks = 7

class ServiceItem(object):
    """
    The service item is a base class for the plugins to use to interact with
    the service manager, the slide controller, and the projection screen
    compositor.
    """
    log.info(u'Service Item created')

    def __init__(self, plugin=None):
        """
        Set up the service item.

        ``plugin``
            The plugin that this service item belongs to.
        """
        if plugin:
            self.render_manager = plugin.renderManager
            self.name = plugin.name
        self.title = u''
        self.shortname = u''
        self.audit = u''
        self.items = []
        self.iconic_representation = None
        self.raw_footer = None
        self.foot_text = None
        self.theme = None
        self.service_item_type = None
        self._raw_frames = []
        self._display_frames = []
        self._uuid = 0
        self.notes = u''
        self.from_plugin = False
        self.capabilities = []
        self.is_valid = True
        self.icon = None
        self.themedata = None
        self.main = None
        self.footer = None
        self.bg_image_bytes = None

    def _new_item(self):
        """
        Method to set the internal id of the item
        This is used to compare service items to see if they are
        the same
        """
        self._uuid = unicode(uuid.uuid1())

    def add_capability(self, capability):
        """
        Add an ItemCapability to a ServiceItem

        ``capability``
            The capability to add
        """
        self.capabilities.append(capability)

    def is_capable(self, capability):
        """
        Tell the caller if a ServiceItem has a capability

        ``capability``
            The capability to test for
        """
        return capability in self.capabilities

    def add_icon(self, icon):
        """
        Add an icon to the service item. This is used when displaying the
        service item in the service manager.

        ``icon``
            A string to an icon in the resources or on disk.
        """
        self.icon = icon
        self.iconic_representation = build_icon(icon)

    def render(self, useOverride=False):
        """
        The render method is what generates the frames for the screen and
        obtains the display information from the renderemanager.
        At this point all the slides are build for the given
        display size.
        """
        log.debug(u'Render called')
        self._display_frames = []
        self.bg_image_bytes = None
        line_break = True
        if self.is_capable(ItemCapabilities.NoLineBreaks):
            line_break = False
        if self.service_item_type == ServiceItemType.Text:
            log.debug(u'Formatting slides')
            theme = None
            if self.theme:
                theme = self.theme
            self.main, self.footer = \
                self.render_manager.set_override_theme(theme, useOverride)
            self.bg_image_bytes = self.render_manager.renderer.bg_image_bytes
            self.themedata = self.render_manager.renderer._theme
            for slide in self._raw_frames:
                before = time.time()
                formatted = self.render_manager \
                    .format_slide(slide[u'raw_slide'], line_break)
                for page in formatted:
                    self._display_frames.append(
                        {u'title': clean_tags(page),
                        u'text': clean_tags(page.rstrip()),
                        u'html': expand_tags(page.rstrip()),
                        u'verseTag': slide[u'verseTag'] })
                log.log(15, u'Formatting took %4s' % (time.time() - before))
        elif self.service_item_type == ServiceItemType.Image:
            self.themedata = self.render_manager.global_theme_data
            for slide in self._raw_frames:
                slide[u'image'] = resize_image(slide[u'image'],
                    self.render_manager.width, self.render_manager.height)
        elif self.service_item_type == ServiceItemType.Command:
            pass
        else:
            log.error(u'Invalid value renderer :%s' % self.service_item_type)
        self.title = clean_tags(self.title)
        self.foot_text = None
        if self.raw_footer:
            for foot in self.raw_footer:
                if not self.foot_text:
                    self.foot_text = foot
                else:
                    self.foot_text = u'%s<br>%s' % (self.foot_text, foot)

    def add_from_image(self, path, title, image):
        """
        Add an image slide to the service item.

        ``path``
            The directory in which the image file is located.

        ``title``
            A title for the slide in the service item.

        ``image``
            The actual image file name.
        """
        self.service_item_type = ServiceItemType.Image
        self._raw_frames.append(
            {u'title': title, u'image': image, u'path': path})
        self._new_item()

    def add_from_text(self, title, raw_slide, verse_tag=None):
        """
        Add a text slide to the service item.

        ``frame_title``
            The title of the slide in the service item.

        ``raw_slide``
            The raw text of the slide.
        """
        self.service_item_type = ServiceItemType.Text
        title = title.split(u'\n')[0]
        self._raw_frames.append(
            {u'title': title, u'raw_slide': raw_slide, u'verseTag':verse_tag})
        self._new_item()

    def add_from_command(self, path, file_name, image):
        """
        Add a slide from a command.

        ``path``
            The title of the slide in the service item.

        ``file_name``
            The title of the slide in the service item.

        ``image``
            The command of/for the slide.
        """
        self.service_item_type = ServiceItemType.Command
        self._raw_frames.append(
            {u'title': file_name, u'image': image, u'path': path})
        self._new_item()

    def get_service_repr(self):
        """
        This method returns some text which can be saved into the service
        file to represent this item.
        """
        service_header = {
            u'name': self.name.lower(),
            u'plugin': self.name,
            u'theme':self.theme,
            u'title':self.title,
            u'icon':self.icon,
            u'footer':self.raw_footer,
            u'type':self.service_item_type,
            u'audit':self.audit,
            u'notes':self.notes,
            u'from_plugin':self.from_plugin,
            u'capabilities':self.capabilities
        }
        service_data = []
        if self.service_item_type == ServiceItemType.Text:
            for slide in self._raw_frames:
                service_data.append(slide)
        elif self.service_item_type == ServiceItemType.Image:
            for slide in self._raw_frames:
                service_data.append(slide[u'title'])
        elif self.service_item_type == ServiceItemType.Command:
            for slide in self._raw_frames:
                service_data.append(
                    {u'title':slide[u'title'], u'image':slide[u'image']})
        return {u'header': service_header, u'data': service_data}

    def set_from_service(self, serviceitem, path=None):
        """
        This method takes a service item from a saved service file (passed
        from the ServiceManager) and extracts the data actually required.

        ``serviceitem``
            The item to extract data from.

        ``path``
            Defaults to *None*. Any path data, usually for images.
        """
        header = serviceitem[u'serviceitem'][u'header']
        self.title = header[u'title']
        self.name = header[u'name']
        self.service_item_type = header[u'type']
        self.shortname = header[u'plugin']
        self.theme = header[u'theme']
        self.add_icon(header[u'icon'])
        self.raw_footer = header[u'footer']
        self.audit = header[u'audit']
        self.notes = header[u'notes']
        self.from_plugin = header[u'from_plugin']
        self.capabilities = header[u'capabilities']
        if self.service_item_type == ServiceItemType.Text:
            for slide in serviceitem[u'serviceitem'][u'data']:
                self._raw_frames.append(slide)
        elif self.service_item_type == ServiceItemType.Image:
            for text_image in serviceitem[u'serviceitem'][u'data']:
                filename = os.path.join(path, text_image)
                real_image = QtGui.QImage(unicode(filename))
                self.add_from_image(path, text_image, real_image)
        elif self.service_item_type == ServiceItemType.Command:
            for text_image in serviceitem[u'serviceitem'][u'data']:
                filename = os.path.join(path, text_image[u'title'])
                self.add_from_command(
                    path, text_image[u'title'], text_image[u'image'] )
        self._new_item()

    def merge(self, other):
        """
        Updates the _uuid with the value from the original one
        The _uuid is unique for a given service item but this allows one to
        replace an original version.
        """
        self._uuid = other._uuid

    def __eq__(self, other):
        """
        Confirms the service items are for the same instance
        """
        if not other:
            return False
        return self._uuid == other._uuid

    def __ne__(self, other):
        """
        Confirms the service items are not for the same instance
        """
        return self._uuid != other._uuid

    def is_media(self):
        """
        Confirms if the ServiceItem is media
        """
        return ItemCapabilities.RequiresMedia in self.capabilities

    def is_command(self):
        """
        Confirms if the ServiceItem is a command
        """
        return self.service_item_type == ServiceItemType.Command

    def is_image(self):
        """
        Confirms if the ServiceItem is an image
        """
        return self.service_item_type == ServiceItemType.Image

    def uses_file(self):
        """
        Confirms if the ServiceItem uses a file
        """
        return self.service_item_type == ServiceItemType.Image or \
            self.service_item_type == ServiceItemType.Command

    def is_text(self):
        """
        Confirms if the ServiceItem is text
        """
        return self.service_item_type == ServiceItemType.Text

    def get_frames(self):
        """
        Returns the frames for the ServiceItem
        """
        if self.service_item_type == ServiceItemType.Text:
            return self._display_frames
        else:
            return self._raw_frames

    def get_rendered_frame(self, row):
        """
        Returns the correct frame for a given list and
        renders it if required.
        """
        if self.service_item_type == ServiceItemType.Text:
            return None, self._display_frames[row][u'html'].split(u'\n')[0]
        else:
            return self._raw_frames[row][u'image'], u''

    def get_frame_title(self, row=0):
        """
        Returns the title of the raw frame
        """
        return self._raw_frames[row][u'title']

    def get_frame_path(self, row=0):
        """
        Returns the title of the raw frame
        """
        return self._raw_frames[row][u'path']
