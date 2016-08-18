# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
The :mod:`lib` module contains most of the components and libraries that make
OpenLP work.
"""

import logging
import os
import re
import math
from distutils.version import LooseVersion

from PyQt5 import QtCore, QtGui, Qt, QtWidgets

from openlp.core.common import translate

log = logging.getLogger(__name__ + '.__init__')


class ServiceItemContext(object):
    """
    The context in which a Service Item is being generated
    """
    Preview = 0
    Live = 1
    Service = 2


class ImageSource(object):
    """
    This enumeration class represents different image sources. An image sources states where an image is used. This
    enumeration class is need in the context of the :class:~openlp.core.lib.imagemanager`.

    ``ImagePlugin``
        This states that an image is being used by the image plugin.

    ``Theme``
        This says, that the image is used by a theme.

    ``CommandPlugins``
        This states that an image is being used by a command plugin.
    """
    ImagePlugin = 1
    Theme = 2
    CommandPlugins = 3


class MediaType(object):
    """
    An enumeration class for types of media.
    """
    Audio = 1
    Video = 2


class ServiceItemAction(object):
    """
    Provides an enumeration for the required action moving between service items by left/right arrow keys
    """
    Previous = 1
    PreviousLastSlide = 2
    Next = 3


def get_text_file_string(text_file):
    """
    Open a file and return its content as unicode string. If the supplied file name is not a file then the function
    returns False. If there is an error loading the file or the content can't be decoded then the function will return
    None.

    :param text_file: The name of the file.
    :return: The file as a single string
    """
    if not os.path.isfile(text_file):
        return False
    file_handle = None
    content = None
    try:
        file_handle = open(text_file, 'r', encoding='utf-8')
        if file_handle.read(3) != '\xEF\xBB\xBF':
            # no BOM was found
            file_handle.seek(0)
        content = file_handle.read()
    except (IOError, UnicodeError):
        log.exception('Failed to open text file {text}'.format(text=text_file))
    finally:
        if file_handle:
            file_handle.close()
    return content


def str_to_bool(string_value):
    """
    Convert a string version of a boolean into a real boolean.

    :param string_value: The string value to examine and convert to a boolean type.
    :return: The correct boolean value
    """
    if isinstance(string_value, bool):
        return string_value
    return str(string_value).strip().lower() in ('true', 'yes', 'y')


def build_icon(icon):
    """
    Build a QIcon instance from an existing QIcon, a resource location, or a physical file location. If the icon is a
    QIcon instance, that icon is simply returned. If not, it builds a QIcon instance from the resource or file name.

    :param icon:
        The icon to build. This can be a QIcon, a resource string in the form ``:/resource/file.png``, or a file
        location like ``/path/to/file.png``. However, the **recommended** way is to specify a resource string.
    :return: The build icon.
    """
    button_icon = QtGui.QIcon()
    if isinstance(icon, QtGui.QIcon):
        button_icon = icon
    elif isinstance(icon, str):
        if icon.startswith(':/'):
            button_icon.addPixmap(QtGui.QPixmap(icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            button_icon.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(icon)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    elif isinstance(icon, QtGui.QImage):
        button_icon.addPixmap(QtGui.QPixmap.fromImage(icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return button_icon


def image_to_byte(image, base_64=True):
    """
    Resize an image to fit on the current screen for the web and returns it as a byte stream.

    :param image: The image to converted.
    :param base_64: If True returns the image as Base64 bytes, otherwise the image is returned as a byte array.
        To preserve original intention, this defaults to True
    """
    log.debug('image_to_byte - start')
    byte_array = QtCore.QByteArray()
    # use buffer to store pixmap into byteArray
    buffie = QtCore.QBuffer(byte_array)
    buffie.open(QtCore.QIODevice.WriteOnly)
    image.save(buffie, "PNG")
    log.debug('image_to_byte - end')
    if not base_64:
        return byte_array
    # convert to base64 encoding so does not get missed!
    return bytes(byte_array.toBase64()).decode('utf-8')


def create_thumb(image_path, thumb_path, return_icon=True, size=None):
    """
    Create a thumbnail from the given image path and depending on ``return_icon`` it returns an icon from this thumb.

    :param image_path: The image file to create the icon from.
    :param thumb_path: The filename to save the thumbnail to.
    :param return_icon: States if an icon should be build and returned from the thumb. Defaults to ``True``.
    :param size: Allows to state a own size (QtCore.QSize) to use. Defaults to ``None``, which means that a default
     height of 88 is used.
    :return: The final icon.
    """
    ext = os.path.splitext(thumb_path)[1].lower()
    reader = QtGui.QImageReader(image_path)
    if size is None:
        # No size given; use default height of 88
        if reader.size().isEmpty():
            ratio = 1
        else:
            ratio = reader.size().width() / reader.size().height()
        reader.setScaledSize(QtCore.QSize(int(ratio * 88), 88))
    elif size.isValid():
        # Complete size given
        reader.setScaledSize(size)
    else:
        # Invalid size given
        if reader.size().isEmpty():
            ratio = 1
        else:
            ratio = reader.size().width() / reader.size().height()
        if size.width() >= 0:
            # Valid width; scale height
            reader.setScaledSize(QtCore.QSize(size.width(), int(size.width() / ratio)))
        elif size.height() >= 0:
            # Valid height; scale width
            reader.setScaledSize(QtCore.QSize(int(ratio * size.height()), size.height()))
        else:
            # Invalid; use default height of 88
            reader.setScaledSize(QtCore.QSize(int(ratio * 88), 88))
    thumb = reader.read()
    thumb.save(thumb_path, ext[1:])
    if not return_icon:
        return
    if os.path.exists(thumb_path):
        return build_icon(thumb_path)
    # Fallback for files with animation support.
    return build_icon(image_path)


def validate_thumb(file_path, thumb_path):
    """
    Validates whether an file's thumb still exists and if is up to date. **Note**, you must **not** call this function,
    before checking the existence of the file.

    :param file_path: The path to the file. The file **must** exist!
    :param thumb_path: The path to the thumb.
    :return: True, False if the image has changed since the thumb was created.
    """
    if not os.path.exists(thumb_path):
        return False
    image_date = os.stat(file_path).st_mtime
    thumb_date = os.stat(thumb_path).st_mtime
    return image_date <= thumb_date


def resize_image(image_path, width, height, background='#000000'):
    """
    Resize an image to fit on the current screen.

    DO NOT REMOVE THE DEFAULT BACKGROUND VALUE!

    :param image_path: The path to the image to resize.
    :param width: The new image width.
    :param height: The new image height.
    :param background: The background colour. Defaults to black.
    """
    log.debug('resize_image - start')
    reader = QtGui.QImageReader(image_path)
    # The image's ratio.
    image_ratio = reader.size().width() / reader.size().height()
    resize_ratio = width / height
    # Figure out the size we want to resize the image to (keep aspect ratio).
    if image_ratio == resize_ratio:
        size = QtCore.QSize(width, height)
    elif image_ratio < resize_ratio:
        # Use the image's height as reference for the new size.
        size = QtCore.QSize(image_ratio * height, height)
    else:
        # Use the image's width as reference for the new size.
        size = QtCore.QSize(width, 1 / (image_ratio / width))
    reader.setScaledSize(size)
    preview = reader.read()
    if image_ratio == resize_ratio:
        # We neither need to centre the image nor add "bars" to the image.
        return preview
    real_width = preview.width()
    real_height = preview.height()
    # and move it to the centre of the preview space
    new_image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
    painter = QtGui.QPainter(new_image)
    painter.fillRect(new_image.rect(), QtGui.QColor(background))
    painter.drawImage((width - real_width) // 2, (height - real_height) // 2, preview)
    return new_image


def check_item_selected(list_widget, message):
    """
    Check if a list item is selected so an action may be performed on it

    :param list_widget: The list to check for selected items
    :param message: The message to give the user if no item is selected
    """
    if not list_widget.selectedIndexes():
        QtWidgets.QMessageBox.information(list_widget.parent(),
                                          translate('OpenLP.MediaManagerItem', 'No Items Selected'), message)
        return False
    return True


def clean_tags(text, remove_chords=False):
    """
    Remove Tags from text for display

    :param text: Text to be cleaned
    :param remove_chords: Clean ChordPro tags
    """
    text = text.replace('<br>', '\n')
    text = text.replace('{br}', '\n')
    text = text.replace('&nbsp;', ' ')
    for tag in FormattingTags.get_html_tags():
        text = text.replace(tag['start tag'], '')
        text = text.replace(tag['end tag'], '')
    # Remove ChordPro tags
    if remove_chords:
        text = re.sub(r'\[.+?\]', r'', text)
    return text


def expand_tags(text):
    """
    Expand tags HTML for display

    :param text: The text to be expanded.
    """
    text = expand_chords(text)
    for tag in FormattingTags.get_html_tags():
        text = text.replace(tag['start tag'], tag['start html'])
        text = text.replace(tag['end tag'], tag['end html'])
    return text


def expand_and_align_chords_in_line(match):
    """
    Expand the chords in the line and align them using whitespaces.
    NOTE: There is equivalent javascript code in chords.js, in the updateSlide function. Make sure to update both!

    :param match:
    :return: The line with expanded html-chords
    """
    slimchars = 'fiíIÍjlĺľrtť.,;/ ()|"\'!:\\'
    whitespaces = ''
    chordlen = 0
    taillen = 0
    # The match could be "[G]sweet the " from a line like "A[D]mazing [D7]grace! How [G]sweet the [D]sound!"
    # The actual chord, would be "G" in match "[G]sweet the "
    chord = match.group(1)
    # The tailing word of the chord, would be "sweet" in match "[G]sweet the "
    tail = match.group(2)
    # The remainder of the line, until line end or next chord. Would be " the " in match "[G]sweet the "
    remainder = match.group(3)
    # Line end if found, else None
    end = match.group(4)
    # Based on char width calculate width of chord
    for chord_char in chord:
        if chord_char not in slimchars:
            chordlen += 2
        else:
            chordlen += 1
    # Based on char width calculate width of tail
    for tail_char in tail:
        if tail_char not in slimchars:
            taillen += 2
        else:
            taillen += 1
    # Based on char width calculate width of remainder
    for remainder_char in remainder:
        if remainder_char not in slimchars:
            taillen += 2
        else:
            taillen += 1
    # If the chord is wider than the tail+remainder and the line goes on, some padding is needed
    if chordlen >= taillen and end is None:
        # Decide if the padding should be "_" for drawing out words or spaces
        if tail:
            if not remainder:
                for c in range(math.ceil((chordlen - taillen) / 2) + 1):
                    whitespaces += '_'
            else:
                for c in range(chordlen - taillen + 2):
                    whitespaces += '&nbsp;'
        else:
            if not remainder:
                for c in range(math.floor((chordlen - taillen) / 2)):
                    whitespaces += '_'
            else:
                for c in range(chordlen - taillen + 1):
                    whitespaces += '&nbsp;'
    else:
        if not tail and remainder and remainder[0] == ' ':
            for c in range(chordlen):
                whitespaces += '&nbsp;'
    if whitespaces:
        whitespaces = '<span class="ws">' + whitespaces + '</span>'
    return '<span class="chord"><span><strong>' + chord + '</strong></span></span>' + tail + whitespaces + remainder


def expand_chords(text):
    """
    Expand ChordPro tags

    :param text:
    """
    text_lines = text.split('{br}')
    expanded_text_lines = []
    chords_on_prev_line = False
    for line in text_lines:
        # If a ChordPro is detected in the line, replace it with a html-span tag and wrap the line in a span tag.
        if '[' in line and ']' in line:
            if chords_on_prev_line:
                new_line = '<span class="chordline">'
            else:
                new_line = '<span class="chordline firstchordline">'
                chords_on_prev_line = True
            # Matches a chord, a tail, a remainder and a line end. See expand_and_align_chords_in_line() for more info.
            new_line += re.sub(r'\[(\w.*?)\]([\u0080-\uFFFF,\w]*)'
                               '([\u0080-\uFFFF,\w,\s,\.,\,,\!,\?,\;,\:,\|,\",\',\-,\_]*)(\Z)?',
                               expand_and_align_chords_in_line, line)
            new_line += '</span>'
            expanded_text_lines.append(new_line)
        else:
            chords_on_prev_line = False
            expanded_text_lines.append(line)
    return '{br}'.join(expanded_text_lines)


def create_separated_list(string_list):
    """
    Returns a string that represents a join of a list of strings with a localized separator. This function corresponds

    to QLocale::createSeparatedList which was introduced in Qt 4.8 and implements the algorithm from
    http://www.unicode.org/reports/tr35/#ListPatterns

     :param string_list: List of unicode strings
    """
    if LooseVersion(Qt.PYQT_VERSION_STR) >= LooseVersion('4.9') and LooseVersion(Qt.qVersion()) >= LooseVersion('4.8'):
        return QtCore.QLocale().createSeparatedList(string_list)
    if not string_list:
        return ''
    elif len(string_list) == 1:
        return string_list[0]
    # TODO: Verify mocking of translate() test before conversion
    elif len(string_list) == 2:
        return translate('OpenLP.core.lib', '%s and %s',
                         'Locale list separator: 2 items') % (string_list[0], string_list[1])
    else:
        merged = translate('OpenLP.core.lib', '%s, and %s',
                           'Locale list separator: end') % (string_list[-2], string_list[-1])
        for index in reversed(list(range(1, len(string_list) - 2))):
            merged = translate('OpenLP.core.lib', '%s, %s',
                               'Locale list separator: middle') % (string_list[index], merged)
        return translate('OpenLP.core.lib', '%s, %s', 'Locale list separator: start') % (string_list[0], merged)


from .exceptions import ValidationError
from .filedialog import FileDialog
from .screen import ScreenList
from .formattingtags import FormattingTags
from .plugin import PluginStatus, StringContent, Plugin
from .pluginmanager import PluginManager
from .settingstab import SettingsTab
from .serviceitem import ServiceItem, ServiceItemType, ItemCapabilities
from .htmlbuilder import build_html, build_lyrics_format_css, build_lyrics_outline_css, build_chords_css
from .imagemanager import ImageManager
from .renderer import Renderer
from .mediamanageritem import MediaManagerItem
from .projector.db import ProjectorDB, Projector
from .projector.pjlink1 import PJLink1
from .projector.constants import PJLINK_PORT, ERROR_MSG, ERROR_STRING
