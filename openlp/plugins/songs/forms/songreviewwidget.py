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
A widget representing a song in the duplicate song removal wizard review page.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.lib import build_icon
from openlp.plugins.songs.lib.xml import SongXML

class SongReviewWidget(QtGui.QWidget):
    """
    A widget representing a song on the duplicate song review page.
    It displays most of the information a song contains and
    provides a "remove" button to remove the song from the database.
    The remove logic is not implemented here, but a signal is provided
    when the remove button is clicked.
    """
    def __init__(self, parent, song):
        """
        ``parent``
            The QWidget-derived parent of the wizard.

        ``song``
            The Song which this SongReviewWidget should represent.
        """
        QtGui.QWidget.__init__(self, parent)
        self.song = song
        self.setupUi()
        self.retranslateUi()
        self.song_remove_button.clicked.connect(self.on_remove_button_clicked)

    def setupUi(self):
        self.song_vertical_layout = QtGui.QVBoxLayout(self)
        self.song_vertical_layout.setObjectName(u'song_vertical_layout')
        self.song_group_box = QtGui.QGroupBox(self)
        self.song_group_box.setObjectName(u'song_group_box')
        self.song_group_box.setMinimumWidth(300)
        self.song_group_box.setMaximumWidth(300)
        self.song_group_box_layout = QtGui.QVBoxLayout(self.song_group_box)
        self.song_group_box_layout.setObjectName(u'song_group_box_layout')
        self.song_info_form_layout = QtGui.QFormLayout()
        self.song_info_form_layout.setObjectName(u'song_info_form_layout')
        # Add title widget.
        self.song_title_label = QtGui.QLabel(self)
        self.song_title_label.setObjectName(u'song_title_label')
        self.song_info_form_layout.setWidget(0, QtGui.QFormLayout.LabelRole, self.song_title_label)
        self.song_title_content = QtGui.QLabel(self)
        self.song_title_content.setObjectName(u'song_title_content')
        self.song_title_content.setText(self.song.title)
        self.song_title_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(0, QtGui.QFormLayout.FieldRole, self.song_title_content)
        # Add alternate title widget.
        self.song_alternate_title_label = QtGui.QLabel(self)
        self.song_alternate_title_label.setObjectName(u'song_alternate_title_label')
        self.song_info_form_layout.setWidget(1, QtGui.QFormLayout.LabelRole, self.song_alternate_title_label)
        self.song_alternate_title_content = QtGui.QLabel(self)
        self.song_alternate_title_content.setObjectName(u'song_alternate_title_content')
        self.song_alternate_title_content.setText(self.song.alternate_title)
        self.song_alternate_title_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(1, QtGui.QFormLayout.FieldRole, self.song_alternate_title_content)
        # Add CCLI number widget.
        self.song_ccli_number_label = QtGui.QLabel(self)
        self.song_ccli_number_label.setObjectName(u'song_ccli_number_label')
        self.song_info_form_layout.setWidget(2, QtGui.QFormLayout.LabelRole, self.song_ccli_number_label)
        self.song_ccli_number_content = QtGui.QLabel(self)
        self.song_ccli_number_content.setObjectName(u'song_ccli_number_content')
        self.song_ccli_number_content.setText(self.song.ccli_number)
        self.song_ccli_number_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(2, QtGui.QFormLayout.FieldRole, self.song_ccli_number_content)
        # Add copyright widget.
        self.song_copyright_label = QtGui.QLabel(self)
        self.song_copyright_label.setObjectName(u'song_copyright_label')
        self.song_info_form_layout.setWidget(3, QtGui.QFormLayout.LabelRole, self.song_copyright_label)
        self.song_copyright_content = QtGui.QLabel(self)
        self.song_copyright_content.setObjectName(u'song_copyright_content')
        self.song_copyright_content.setWordWrap(True)
        self.song_copyright_content.setText(self.song.copyright)
        self.song_info_form_layout.setWidget(3, QtGui.QFormLayout.FieldRole, self.song_copyright_content)
        # Add comments widget.
        self.song_comments_label = QtGui.QLabel(self)
        self.song_comments_label.setObjectName(u'song_comments_label')
        self.song_info_form_layout.setWidget(4, QtGui.QFormLayout.LabelRole, self.song_comments_label)
        self.song_comments_content = QtGui.QLabel(self)
        self.song_comments_content.setObjectName(u'song_comments_content')
        self.song_comments_content.setText(self.song.comments)
        self.song_comments_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(4, QtGui.QFormLayout.FieldRole, self.song_comments_content)
        # Add authors widget.
        self.song_authors_label = QtGui.QLabel(self)
        self.song_authors_label.setObjectName(u'song_authors_label')
        self.song_info_form_layout.setWidget(5, QtGui.QFormLayout.LabelRole, self.song_authors_label)
        self.song_authors_content = QtGui.QLabel(self)
        self.song_authors_content.setObjectName(u'song_authors_content')
        self.song_authors_content.setWordWrap(True)
        authors_text = u', '.join([author.display_name for author in self.song.authors])
        self.song_authors_content.setText(authors_text)
        self.song_info_form_layout.setWidget(5, QtGui.QFormLayout.FieldRole, self.song_authors_content)
        # Add verse order widget.
        self.song_verse_order_label = QtGui.QLabel(self)
        self.song_verse_order_label.setObjectName(u'song_verse_order_label')
        self.song_info_form_layout.setWidget(6, QtGui.QFormLayout.LabelRole, self.song_verse_order_label)
        self.song_verse_order_content = QtGui.QLabel(self)
        self.song_verse_order_content.setObjectName(u'song_verse_order_content')
        self.song_verse_order_content.setText(self.song.verse_order)
        self.song_verse_order_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(6, QtGui.QFormLayout.FieldRole, self.song_verse_order_content)
        # Add verses widget.
        self.song_group_box_layout.addLayout(self.song_info_form_layout)
        self.song_info_verse_group_box = QtGui.QGroupBox(self.song_group_box)
        self.song_info_verse_group_box.setObjectName(u'song_info_verse_group_box')
        self.song_info_verse_group_box_layout = QtGui.QFormLayout(self.song_info_verse_group_box)
        song_xml = SongXML()
        verses = song_xml.get_verses(self.song.lyrics)
        for verse in verses:
            verse_marker = verse[0]['type'] + verse[0]['label']
            verse_label = QtGui.QLabel(self.song_info_verse_group_box)
            verse_label.setText(verse[1])
            verse_label.setWordWrap(True)
            self.song_info_verse_group_box_layout.addRow(verse_marker, verse_label)
        self.song_group_box_layout.addWidget(self.song_info_verse_group_box)
        self.song_group_box_layout.addStretch()
        self.song_vertical_layout.addWidget(self.song_group_box)
        self.song_remove_button = QtGui.QPushButton(self)
        self.song_remove_button.setObjectName(u'song_remove_button')
        self.song_remove_button.setIcon(build_icon(u':/songs/song_delete.png'))
        self.song_remove_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.song_vertical_layout.addWidget(self.song_remove_button, alignment = QtCore.Qt.AlignHCenter)

    def retranslateUi(self):
        self.song_remove_button.setText(u'Remove')
        self.song_title_label.setText(u'Title:')
        self.song_alternate_title_label.setText(u'Alternate Title:')
        self.song_ccli_number_label.setText(u'CCLI Number:')
        self.song_verse_order_label.setText(u'Verse Order:')
        self.song_copyright_label.setText(u'Copyright:')
        self.song_comments_label.setText(u'Comments:')
        self.song_authors_label.setText(u'Authors:')
        self.song_info_verse_group_box.setTitle(u'Verses')

    def on_remove_button_clicked(self):
        """
        Signal emitted when the "remove" button is clicked.
        """
        self.emit(QtCore.SIGNAL(u'song_remove_button_clicked(PyQt_PyObject)'), self)
