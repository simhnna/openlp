# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Edwin Lunando, Joshua Miller, Stevan Pettit,  #
# Andreas Preikschat, Mattias Põldaru, Christian Richter, Philip Ridout,      #
# Simon Scudder, Jeffrey Smith, Maikel Stuivenberg, Martin Thompson, Jon      #
# Tibble, Dave Warnock, Frode Woldsund                                        #
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

import cgi
import datetime
import logging
import os
import uuid

from openlp.core.lib import build_icon, clean_tags, expand_tags, translate, \
    ImageSource

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
    CanPreview = 1
    CanEdit = 2
    CanMaintain = 3
    RequiresMedia = 4
    CanLoop = 5
    CanAppend = 6
    NoLineBreaks = 7
    OnLoadUpdate = 8
    AddIfNewItem = 9
    ProvidesOwnDisplay = 10
    HasDetailedTitleDisplay = 11
    HasVariableStartTime = 12
    CanSoftBreak = 13
    CanWordSplit = 14
    HasBackgroundAudio = 15


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
            self.renderer = plugin.renderer
            self.name = plugin.name
        self.title = u''
        self.shortname = u''
        self.audit = u''
        self.items = []
        self.iconic_representation = None
        self.raw_footer = []
        self.foot_text = u''
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
        self.search_string = u''
        self.data_string = u''
        self.edit_id = None
        self.xml_version = None
        self.start_time = 0
        self.end_time = 0
        self.media_length = 0
        self.from_service = False
        self.image_border = u'#000000'
        self.background_audio = []
        self.theme_overwritten = False
        self.temporary_edit = False
        self._new_item()

    def _new_item(self):
        """
        Method to set the internal id of the item. This is used to compare
        service items to see if they are the same.
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

    def render(self, provides_own_theme_data=False):
        """
        The render method is what generates the frames for the screen and
        obtains the display information from the renderer. At this point all
        slides are built for the given display size.

        ``provides_own_theme_data``
            This switch disables the usage of the item's theme. However, this is
            disabled by default. If this is used, it has to be taken care, that
            the renderer knows the correct theme data. However, this is needed
            for the theme manager.
        """
        log.debug(u'Render called')
        self._display_frames = []
        self.bg_image_bytes = None
        if not provides_own_theme_data:
            self.renderer.set_item_theme(self.theme)
            self.themedata, self.main, self.footer = self.renderer.pre_render()
        if self.service_item_type == ServiceItemType.Text:
            log.debug(u'Formatting slides: %s' % self.title)
            for slide in self._raw_frames:
                pages = self.renderer.format_slide(slide[u'raw_slide'], self)
                for page in pages:
                    page = page.replace(u'<br>', u'{br}')
                    html = expand_tags(cgi.escape(page.rstrip()))
                    self._display_frames.append({
                        u'title': clean_tags(page),
                        u'text': clean_tags(page.rstrip()),
                        u'html': html.replace(u'&amp;nbsp;', u'&nbsp;'),
                        u'verseTag': slide[u'verseTag']
                    })
        elif self.service_item_type == ServiceItemType.Image or \
            self.service_item_type == ServiceItemType.Command:
            pass
        else:
            log.error(u'Invalid value renderer: %s' % self.service_item_type)
        self.title = clean_tags(self.title)
        # The footer should never be None, but to be compatible with a few
        # nightly builds between 1.9.4 and 1.9.5, we have to correct this to
        # avoid tracebacks.
        if self.raw_footer is None:
            self.raw_footer = []
        self.foot_text = u'<br>'.join(filter(None, self.raw_footer))

    def add_from_image(self, path, title, background=None):
        """
        Add an image slide to the service item.

        ``path``
            The directory in which the image file is located.

        ``title``
            A title for the slide in the service item.
        """
        if background:
            self.image_border = background
        self.service_item_type = ServiceItemType.Image
        self._raw_frames.append({u'title': title, u'path': path})
        self.renderer.image_manager.addImage(
            path, ImageSource.ImagePlugin, self.image_border)
        self._new_item()

    def add_from_text(self, raw_slide, verse_tag=None):
        """
        Add a text slide to the service item.

        ``raw_slide``
            The raw text of the slide.
        """
        if verse_tag:
            verse_tag = verse_tag.upper()
        self.service_item_type = ServiceItemType.Text
        title = raw_slide[:30].split(u'\n')[0]
        self._raw_frames.append(
            {u'title': title, u'raw_slide': raw_slide, u'verseTag': verse_tag})
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
            u'name': self.name,
            u'plugin': self.name,
            u'theme': self.theme,
            u'title': self.title,
            u'icon': self.icon,
            u'footer': self.raw_footer,
            u'type': self.service_item_type,
            u'audit': self.audit,
            u'notes': self.notes,
            u'from_plugin': self.from_plugin,
            u'capabilities': self.capabilities,
            u'search': self.search_string,
            u'data': self.data_string,
            u'xml_version': self.xml_version,
            u'start_time': self.start_time,
            u'end_time': self.end_time,
            u'media_length': self.media_length,
            u'background_audio': self.background_audio,
            u'theme_overwritten': self.theme_overwritten
        }
        service_data = []
        if self.service_item_type == ServiceItemType.Text:
            service_data = [slide for slide in self._raw_frames]
        elif self.service_item_type == ServiceItemType.Image:
            service_data = [slide[u'title'] for slide in self._raw_frames]
        elif self.service_item_type == ServiceItemType.Command:
            for slide in self._raw_frames:
                service_data.append(
                    {u'title': slide[u'title'], u'image': slide[u'image']})
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
        log.debug(u'set_from_service called with path %s' % path)
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
        # Added later so may not be present in older services.
        self.search_string = header.get(u'search', u'')
        self.data_string = header.get(u'data', u'')
        self.xml_version = header.get(u'xml_version')
        self.start_time = header.get(u'start_time', 0)
        self.end_time = header.get(u'end_time', 0)
        self.media_length = header.get(u'media_length', 0)
        if u'background_audio' in header:
            self.background_audio = []
            for filename in header[u'background_audio']:
                # Give them real file paths
                self.background_audio.append(os.path.join(path, filename))
        self.theme_overwritten = header.get(u'theme_overwritten', False)
        if self.service_item_type == ServiceItemType.Text:
            for slide in serviceitem[u'serviceitem'][u'data']:
                self._raw_frames.append(slide)
        elif self.service_item_type == ServiceItemType.Image:
            for text_image in serviceitem[u'serviceitem'][u'data']:
                filename = os.path.join(path, text_image)
                self.add_from_image(filename, text_image)
        elif self.service_item_type == ServiceItemType.Command:
            for text_image in serviceitem[u'serviceitem'][u'data']:
                filename = os.path.join(path, text_image[u'title'])
                self.add_from_command(
                    path, text_image[u'title'], text_image[u'image'])
        self._new_item()

    def get_display_title(self):
        """
        Returns the title of the service item.
        """
        if self.is_text():
            return self.title
        else:
            if ItemCapabilities.HasDetailedTitleDisplay in self.capabilities:
                return self._raw_frames[0][u'title']
            elif len(self._raw_frames) > 1:
                return self.title
            else:
                return self._raw_frames[0][u'title']

    def merge(self, other):
        """
        Updates the _uuid with the value from the original one
        The _uuid is unique for a given service item but this allows one to
        replace an original version.

        ``other``
            The service item to be merged with
        """
        self._uuid = other._uuid
        self.notes = other.notes
        self.temporary_edit = other.temporary_edit
        # Copy theme over if present.
        if other.theme is not None:
            self.theme = other.theme
            self._new_item()
        self.render()
        if self.is_capable(ItemCapabilities.HasBackgroundAudio):
            log.debug(self.background_audio)

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
        Returns the correct frame for a given list and renders it if required.
        """
        if self.service_item_type == ServiceItemType.Text:
            return self._display_frames[row][u'html'].split(u'\n')[0]
        elif self.service_item_type == ServiceItemType.Image:
            return self._raw_frames[row][u'path']
        else:
            return self._raw_frames[row][u'image']

    def get_frame_title(self, row=0):
        """
        Returns the title of the raw frame
        """
        try:
            return self._raw_frames[row][u'title']
        except IndexError:
            return u''

    def get_frame_path(self, row=0):
        """
        Returns the path of the raw frame
        """
        try:
            return self._raw_frames[row][u'path']
        except IndexError:
            return u''

    def get_media_time(self):
        """
        Returns the start and finish time for a media item
        """
        start = None
        end = None
        if self.start_time != 0:
            start = translate('OpenLP.ServiceItem',
                '<strong>Start</strong>: %s') % \
                unicode(datetime.timedelta(seconds=self.start_time))
        if self.media_length != 0:
            end = translate('OpenLP.ServiceItem',
                '<strong>Length</strong>: %s') % \
                unicode(datetime.timedelta(seconds=self.media_length))
        if not start and not end:
            return u''
        elif start and not end:
            return start
        elif not start and end:
            return end
        else:
            return u'%s <br>%s' % (start, end)

    def update_theme(self, theme):
        """
        updates the theme in the service item

        ``theme``
            The new theme to be replaced in the service item
        """
        self.theme_overwritten = (theme == None)
        self.theme = theme
        self._new_item()
        self.render()

