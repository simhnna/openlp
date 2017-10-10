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
Provide the theme XML and handling functions for OpenLP v2 themes.
"""
import json
import logging

from lxml import etree, objectify

from openlp.core.common import de_hump
from openlp.core.common.applocation import AppLocation
from openlp.core.common.json import OpenLPJsonDecoder, OpenLPJsonEncoder
from openlp.core.lib import ScreenList, str_to_bool, get_text_file_string

log = logging.getLogger(__name__)


class BackgroundType(object):
    """
    Type enumeration for backgrounds.
    """
    Solid = 0
    Gradient = 1
    Image = 2
    Transparent = 3
    Video = 4

    @staticmethod
    def to_string(background_type):
        """
        Return a string representation of a background type.
        """
        if background_type == BackgroundType.Solid:
            return 'solid'
        elif background_type == BackgroundType.Gradient:
            return 'gradient'
        elif background_type == BackgroundType.Image:
            return 'image'
        elif background_type == BackgroundType.Transparent:
            return 'transparent'
        elif background_type == BackgroundType.Video:
            return 'video'

    @staticmethod
    def from_string(type_string):
        """
        Return a background type for the given string.
        """
        if type_string == 'solid':
            return BackgroundType.Solid
        elif type_string == 'gradient':
            return BackgroundType.Gradient
        elif type_string == 'image':
            return BackgroundType.Image
        elif type_string == 'transparent':
            return BackgroundType.Transparent
        elif type_string == 'video':
            return BackgroundType.Video


class BackgroundGradientType(object):
    """
    Type enumeration for background gradients.
    """
    Horizontal = 0
    Vertical = 1
    Circular = 2
    LeftTop = 3
    LeftBottom = 4

    @staticmethod
    def to_string(gradient_type):
        """
        Return a string representation of a background gradient type.
        """
        if gradient_type == BackgroundGradientType.Horizontal:
            return 'horizontal'
        elif gradient_type == BackgroundGradientType.Vertical:
            return 'vertical'
        elif gradient_type == BackgroundGradientType.Circular:
            return 'circular'
        elif gradient_type == BackgroundGradientType.LeftTop:
            return 'leftTop'
        elif gradient_type == BackgroundGradientType.LeftBottom:
            return 'leftBottom'

    @staticmethod
    def from_string(type_string):
        """
        Return a background gradient type for the given string.
        """
        if type_string == 'horizontal':
            return BackgroundGradientType.Horizontal
        elif type_string == 'vertical':
            return BackgroundGradientType.Vertical
        elif type_string == 'circular':
            return BackgroundGradientType.Circular
        elif type_string == 'leftTop':
            return BackgroundGradientType.LeftTop
        elif type_string == 'leftBottom':
            return BackgroundGradientType.LeftBottom


class HorizontalType(object):
    """
    Type enumeration for horizontal alignment.
    """
    Left = 0
    Right = 1
    Center = 2
    Justify = 3

    Names = ['left', 'right', 'center', 'justify']


class VerticalType(object):
    """
    Type enumeration for vertical alignment.
    """
    Top = 0
    Middle = 1
    Bottom = 2

    Names = ['top', 'middle', 'bottom']


BOOLEAN_LIST = ['bold', 'italics', 'override', 'outline', 'shadow', 'slide_transition']

INTEGER_LIST = ['size', 'line_adjustment', 'x', 'height', 'y', 'width', 'shadow_size', 'outline_size',
                'horizontal_align', 'vertical_align', 'wrap_style']


class Theme(object):
    """
    A class to encapsulate the Theme XML.
    """
    def __init__(self):
        """
        Initialise the theme object.
        """
        # basic theme object with defaults
        json_path = AppLocation.get_directory(AppLocation.AppDir) / 'core' / 'lib' / 'json' / 'theme.json'
        jsn = get_text_file_string(json_path)
        self.load_theme(jsn)
        self.background_filename = None

    def expand_json(self, var, prev=None):
        """
        Expand the json objects and make into variables.

        :param var: The array list to be processed.
        :param prev: The preceding string to add to the key to make the variable.
        """
        for key, value in var.items():
            if prev:
                key = prev + "_" + key
            if isinstance(value, dict):
                self.expand_json(value, key)
            else:
                setattr(self, key, value)

    def extend_image_filename(self, path):
        """
        Add the path name to the image name so the background can be rendered.

        :param openlp.core.common.path.Path path: The path name to be added.
        :rtype: None
        """
        if self.background_type == 'image' or self.background_type == 'video':
            if self.background_filename and path:
                self.theme_name = self.theme_name.strip()
                self.background_filename = path / self.theme_name / self.background_filename

    def set_default_header_footer(self):
        """
        Set the header and footer size into the current primary screen.
        10 px on each side is removed to allow for a border.
        """
        current_screen = ScreenList().current
        self.font_main_y = 0
        self.font_main_width = current_screen['size'].width() - 20
        self.font_main_height = current_screen['size'].height() * 9 / 10
        self.font_footer_width = current_screen['size'].width() - 20
        self.font_footer_y = current_screen['size'].height() * 9 / 10
        self.font_footer_height = current_screen['size'].height() / 10

    def load_theme(self, theme, theme_path=None):
        """
        Convert the JSON file and expand it.

        :param theme: the theme string
        :param openlp.core.common.path.Path theme_path: The path to the theme
        :rtype: None
        """
        if theme_path:
            jsn = json.loads(theme, cls=OpenLPJsonDecoder, base_path=theme_path)
        else:
            jsn = json.loads(theme, cls=OpenLPJsonDecoder)
        self.expand_json(jsn)

    def export_theme(self, theme_path=None):
        """
        Loop through the fields and build a dictionary of them

        """
        theme_data = {}
        for attr, value in self.__dict__.items():
            theme_data["{attr}".format(attr=attr)] = value
        if theme_path:
            return json.dumps(theme_data, cls=OpenLPJsonEncoder, base_path=theme_path)
        return json.dumps(theme_data, cls=OpenLPJsonEncoder)

    def parse(self, xml):
        """
        Read in an XML string and parse it.

        :param xml: The XML string to parse.
        """
        self.parse_xml(str(xml))

    def parse_xml(self, xml):
        """
        Parse an XML string.

        :param xml: The XML string to parse.
        """
        # remove encoding string
        line = xml.find('?>')
        if line:
            xml = xml[line + 2:]
        try:
            theme_xml = objectify.fromstring(xml)
        except etree.XMLSyntaxError:
            log.exception('Invalid xml {text}'.format(text=xml))
            return
        xml_iter = theme_xml.getiterator()
        for element in xml_iter:
            master = ''
            if element.tag == 'background':
                if element.attrib:
                    for attr in element.attrib:
                        self._create_attr(element.tag, attr, element.attrib[attr])
            parent = element.getparent()
            if parent is not None:
                if parent.tag == 'font':
                    master = parent.tag + '_' + parent.attrib['type']
                # set up Outline and Shadow Tags and move to font_main
                if parent.tag == 'display':
                    if element.tag.startswith('shadow') or element.tag.startswith('outline'):
                        self._create_attr('font_main', element.tag, element.text)
                    master = parent.tag
                if parent.tag == 'background':
                    master = parent.tag
            if master:
                self._create_attr(master, element.tag, element.text)
                if element.attrib:
                    for attr in element.attrib:
                        base_element = attr
                        # correction for the shadow and outline tags
                        if element.tag == 'shadow' or element.tag == 'outline':
                            if not attr.startswith(element.tag):
                                base_element = element.tag + '_' + attr
                        self._create_attr(master, base_element, element.attrib[attr])
            else:
                if element.tag == 'name':
                    self._create_attr('theme', element.tag, element.text)

    @staticmethod
    def _translate_tags(master, element, value):
        """
        Clean up XML removing and redefining tags
        """
        master = master.strip().lstrip()
        element = element.strip().lstrip()
        value = str(value).strip().lstrip()
        if master == 'display':
            if element == 'wrapStyle':
                return True, None, None, None
            if element.startswith('shadow') or element.startswith('outline'):
                master = 'font_main'
        # fix bold font
        ret_value = None
        if element == 'weight':
            element = 'bold'
            if value == 'Normal':
                ret_value = False
            else:
                ret_value = True
        if element == 'proportion':
            element = 'size'
        return False, master, element, ret_value if ret_value is not None else value

    def _create_attr(self, master, element, value):
        """
        Create the attributes with the correct data types and name format
        """
        reject, master, element, value = self._translate_tags(master, element, value)
        if reject:
            return
        field = de_hump(element)
        tag = master + '_' + field
        if field in BOOLEAN_LIST:
            setattr(self, tag, str_to_bool(value))
        elif field in INTEGER_LIST:
            setattr(self, tag, int(value))
        else:
            # make string value unicode
            if not isinstance(value, str):
                value = str(str(value), 'utf-8')
            # None means an empty string so lets have one.
            if value == 'None':
                value = ''
            setattr(self, tag, str(value).strip().lstrip())

    def __str__(self):
        """
        Return a string representation of this object.
        """
        theme_strings = []
        for key in dir(self):
            if key[0:1] != '_':
                theme_strings.append('{key:>30}: {value}'.format(key=key, value=getattr(self, key)))
        return '\n'.join(theme_strings)
