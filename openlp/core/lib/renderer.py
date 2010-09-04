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
The :mod:`renderer` module enables OpenLP to take the input from plugins and
format it for the output display.
"""
import logging

from PyQt4 import QtGui, QtCore

from openlp.core.lib import resize_image, expand_tags

log = logging.getLogger(__name__)

class Renderer(object):
    """
    Genarates a pixmap image of a array of text. The Text is formatted to
    make sure it fits on the screen and if not extra frames are generated.
    """
    log.info(u'Renderer Loaded')

    def __init__(self):
        """
        Initialise the renderer.
        """
        self._rect = None
        self.theme_name = None
        self._theme = None
        self._bg_image_filename = None
        self.frame = None
        self.bg_frame = None
        self.bg_image = None

    def set_theme(self, theme):
        """
        Set the theme to be used.

        ``theme``
            The theme to be used.
        """
        log.debug(u'set theme')
        self._theme = theme
        self.bg_frame = None
        self.bg_image = None
        self._bg_image_filename = None
        self.theme_name = theme.theme_name
        if theme.background_type == u'image':
            if theme.background_filename:
                self._bg_image_filename = unicode(filename)
                if self.frame:
                    self.bg_image = resize_image(self._bg_image_filename,
                        self.frame.width(),
                        self.frame.height())

    def set_text_rectangle(self, rect_main, rect_footer):
        """
        Sets the rectangle within which text should be rendered.

        ``rect_main``
            The main text block.

        ``rect_footer``
            The footer text block.
        """
        log.debug(u'set_text_rectangle %s , %s' % (rect_main, rect_footer))
        self._rect = rect_main
        self._rect_footer = rect_footer

    def set_frame_dest(self, frame_width, frame_height):
        """
        Set the size of the slide.

        ``frame_width``
            The width of the slide.

        ``frame_height``
            The height of the slide.

        """
        log.debug(u'set frame dest (frame) w %d h %d', frame_width,
            frame_height)
        self.frame = QtGui.QImage(frame_width, frame_height,
            QtGui.QImage.Format_ARGB32_Premultiplied)
        if self._bg_image_filename and not self.bg_image:
            self.bg_image = resize_image(self._bg_image_filename,
                self.frame.width(), self.frame.height())
        if self._theme.background_type == u'image':
            self.bg_frame = QtGui.QImage(self.frame.width(),
                self.frame.height(), QtGui.QImage.Format_ARGB32_Premultiplied)
            painter = QtGui.QPainter()
            painter.begin(self.bg_frame)
            painter.fillRect(self.frame.rect(), QtCore.Qt.black)
            if self.bg_image:
                painter.drawImage(0, 0, self.bg_image)
            painter.end()
        else:
            self.bg_frame = None

    def format_slide(self, words, line_break):
        """
        Figure out how much text can appear on a slide, using the current
        theme settings.

        ``words``
            The words to be fitted on the slide.
        """
        log.debug(u'format_slide - Start')
        line_end = u''
        if line_break:
            line_end = u'<br>'
        words = words.replace(u'\r\n', u'\n')
        verses_text = words.split(u'\n')
        text = []
        for verse in verses_text:
            lines = verse.split(u'\n')
            for line in lines:
                text.append(line)
        doc = QtGui.QTextDocument()
        doc.setPageSize(QtCore.QSizeF(self._rect.width(), self._rect.height()))
        df = doc.defaultFont()
        df.setPointSize(self._theme.font_main_proportion)
        df.setFamily(self._theme.font_main_name)
        main_weight = 50
        if self._theme.font_main_weight == u'Bold':
            main_weight = 75
        df.setWeight(main_weight)
        doc.setDefaultFont(df)
        layout = doc.documentLayout()
        formatted = []
        if self._theme.font_main_weight == u'Bold' and \
            self._theme.font_main_italics:
            shell = u'{p}{st}{it}%s{/it}{/st}{/p}'
        elif self._theme.font_main_weight == u'Bold' and \
            not self._theme.font_main_italics:
            shell = u'{p}{st}%s{/st}{/p}'
        elif self._theme.font_main_italics:
            shell = u'{p}{it}%s{/it}{/p}'
        else:
            shell = u'{p}%s{/p}'
        temp_text = u''
        old_html_text = u''
        for line in text:
            # mark line ends
            temp_text = temp_text + line + line_end
            html_text = shell % expand_tags(temp_text)
            doc.setHtml(html_text)
            # Text too long so gone to next mage
            if layout.pageCount() != 1:
                formatted.append(shell % old_html_text)
                temp_text = line + line_end
            old_html_text = temp_text
        formatted.append(shell % old_html_text)
        log.debug(u'format_slide - End')
        return formatted
