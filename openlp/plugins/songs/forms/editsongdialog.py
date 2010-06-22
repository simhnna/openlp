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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import build_icon, translate

class Ui_EditSongDialog(object):
    def setupUi(self, EditSongDialog):
        EditSongDialog.setObjectName(u'EditSongDialog')
        EditSongDialog.resize(645, 417)
        icon = build_icon(u':/icon/openlp.org-icon-32.bmp')
        EditSongDialog.setWindowIcon(icon)
        EditSongDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(EditSongDialog)
        self.verticalLayout.setMargin(8)
        self.verticalLayout.setObjectName(u'verticalLayout')
        self.SongTabWidget = QtGui.QTabWidget(EditSongDialog)
        self.SongTabWidget.setObjectName(u'SongTabWidget')
        self.LyricsTab = QtGui.QWidget()
        self.LyricsTab.setObjectName(u'LyricsTab')
        self.LyricsTabLayout = QtGui.QGridLayout(self.LyricsTab)
        self.LyricsTabLayout.setMargin(8)
        self.LyricsTabLayout.setSpacing(8)
        self.LyricsTabLayout.setObjectName(u'LyricsTabLayout')
        self.TitleLabel = QtGui.QLabel(self.LyricsTab)
        self.TitleLabel.setObjectName(u'TitleLabel')
        self.LyricsTabLayout.addWidget(self.TitleLabel, 0, 0, 1, 1)
        self.TitleEditItem = QtGui.QLineEdit(self.LyricsTab)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.TitleEditItem.sizePolicy().hasHeightForWidth())
        self.TitleEditItem.setSizePolicy(sizePolicy)
        self.TitleEditItem.setObjectName(u'TitleEditItem')
        self.LyricsTabLayout.addWidget(self.TitleEditItem, 0, 1, 1, 2)
        self.AlternativeTitleLabel = QtGui.QLabel(self.LyricsTab)
        self.AlternativeTitleLabel.setObjectName(u'AlternativeTitleLabel')
        self.LyricsTabLayout.addWidget(self.AlternativeTitleLabel, 1, 0, 1, 1)
        self.AlternativeEdit = QtGui.QLineEdit(self.LyricsTab)
        self.AlternativeEdit.setObjectName(u'AlternativeEdit')
        self.LyricsTabLayout.addWidget(self.AlternativeEdit, 1, 1, 1, 2)
        self.LyricsLabel = QtGui.QLabel(self.LyricsTab)
        self.LyricsLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.LyricsLabel.setObjectName(u'LyricsLabel')
        self.LyricsTabLayout.addWidget(self.LyricsLabel, 2, 0, 1, 1)
        self.VerseListWidget = QtGui.QTableWidget(self.LyricsTab)
        self.VerseListWidget.setColumnCount(1)
        self.VerseListWidget.horizontalHeader().setVisible(False)
        self.VerseListWidget.setSelectionBehavior(1)
        self.VerseListWidget.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)
        self.VerseListWidget.setAlternatingRowColors(True)
        self.VerseListWidget.setObjectName(u'VerseListWidget')
        self.LyricsTabLayout.addWidget(self.VerseListWidget, 2, 1, 1, 1)
        self.VerseOrderLabel = QtGui.QLabel(self.LyricsTab)
        self.VerseOrderLabel.setObjectName(u'VerseOrderLabel')
        self.LyricsTabLayout.addWidget(self.VerseOrderLabel, 4, 0, 1, 1)
        self.VerseOrderEdit = QtGui.QLineEdit(self.LyricsTab)
        self.VerseOrderEdit.setObjectName(u'VerseOrderEdit')
        self.LyricsTabLayout.addWidget(self.VerseOrderEdit, 4, 1, 1, 2)
        self.VerseButtonWidget = QtGui.QWidget(self.LyricsTab)
        self.VerseButtonWidget.setObjectName(u'VerseButtonWidget')
        self.VerseButtonsLayout = QtGui.QVBoxLayout(self.VerseButtonWidget)
        self.VerseButtonsLayout.setSpacing(8)
        self.VerseButtonsLayout.setMargin(0)
        self.VerseButtonsLayout.setObjectName(u'VerseButtonsLayout')
        self.VerseAddButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.VerseAddButton.setObjectName(u'VerseAddButton')
        self.VerseButtonsLayout.addWidget(self.VerseAddButton)
        self.VerseEditButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.VerseEditButton.setObjectName(u'VerseEditButton')
        self.VerseButtonsLayout.addWidget(self.VerseEditButton)
        self.VerseEditAllButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.VerseEditAllButton.setObjectName(u'VerseEditAllButton')
        self.VerseButtonsLayout.addWidget(self.VerseEditAllButton)
        self.VerseDeleteButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.VerseDeleteButton.setObjectName(u'VerseDeleteButton')
        self.VerseButtonsLayout.addWidget(self.VerseDeleteButton)
        spacerItem = QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.VerseButtonsLayout.addItem(spacerItem)
        self.LyricsTabLayout.addWidget(self.VerseButtonWidget, 2, 2, 1, 1)
        self.SongTabWidget.addTab(self.LyricsTab, u'')
        self.AuthorsTab = QtGui.QWidget()
        self.AuthorsTab.setObjectName(u'AuthorsTab')
        self.AuthorsTabLayout = QtGui.QHBoxLayout(self.AuthorsTab)
        self.AuthorsTabLayout.setSpacing(8)
        self.AuthorsTabLayout.setMargin(8)
        self.AuthorsTabLayout.setObjectName(u'AuthorsTabLayout')
        self.AuthorsMaintenanceWidget = QtGui.QWidget(self.AuthorsTab)
        self.AuthorsMaintenanceWidget.setObjectName(u'AuthorsMaintenanceWidget')
        self.AuthorsMaintenanceLayout = QtGui.QVBoxLayout(
            self.AuthorsMaintenanceWidget)
        self.AuthorsMaintenanceLayout.setSpacing(8)
        self.AuthorsMaintenanceLayout.setMargin(0)
        self.AuthorsMaintenanceLayout.setObjectName(u'AuthorsMaintenanceLayout')
        self.AuthorsGroupBox = QtGui.QGroupBox(self.AuthorsMaintenanceWidget)
        self.AuthorsGroupBox.setObjectName(u'AuthorsGroupBox')
        self.AuthorsLayout = QtGui.QVBoxLayout(self.AuthorsGroupBox)
        self.AuthorsLayout.setSpacing(8)
        self.AuthorsLayout.setMargin(8)
        self.AuthorsLayout.setObjectName(u'AuthorsLayout')
        self.AuthorAddWidget = QtGui.QWidget(self.AuthorsGroupBox)
        self.AuthorAddWidget.setObjectName(u'AuthorAddWidget')
        self.AuthorAddLayout = QtGui.QHBoxLayout(self.AuthorAddWidget)
        self.AuthorAddLayout.setSpacing(8)
        self.AuthorAddLayout.setMargin(0)
        self.AuthorAddLayout.setObjectName(u'AuthorAddLayout')
        self.AuthorsSelectionComboItem = QtGui.QComboBox(self.AuthorAddWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.AuthorsSelectionComboItem.sizePolicy().hasHeightForWidth())
        self.AuthorsSelectionComboItem.setSizePolicy(sizePolicy)
        self.AuthorsSelectionComboItem.setEditable(True)
        self.AuthorsSelectionComboItem.setInsertPolicy(
            QtGui.QComboBox.InsertAlphabetically)
        self.AuthorsSelectionComboItem.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.AuthorsSelectionComboItem.setMinimumContentsLength(8)
        self.AuthorsSelectionComboItem.setObjectName(
            u'AuthorsSelectionComboItem')
        self.AuthorAddLayout.addWidget(self.AuthorsSelectionComboItem)
        self.AuthorAddButton = QtGui.QPushButton(self.AuthorAddWidget)
        self.AuthorAddButton.setMaximumSize(QtCore.QSize(110, 16777215))
        self.AuthorAddButton.setObjectName(u'AuthorAddButton')
        self.AuthorAddLayout.addWidget(self.AuthorAddButton)
        self.AuthorsLayout.addWidget(self.AuthorAddWidget)
        self.AuthorsListView = QtGui.QListWidget(self.AuthorsGroupBox)
        self.AuthorsListView.setAlternatingRowColors(True)
        self.AuthorsListView.setObjectName(u'AuthorsListView')
        self.AuthorsLayout.addWidget(self.AuthorsListView)
        self.AuthorRemoveWidget = QtGui.QWidget(self.AuthorsGroupBox)
        self.AuthorRemoveWidget.setObjectName(u'AuthorRemoveWidget')
        self.AuthorRemoveLayout = QtGui.QHBoxLayout(self.AuthorRemoveWidget)
        self.AuthorRemoveLayout.setSpacing(8)
        self.AuthorRemoveLayout.setMargin(0)
        self.AuthorRemoveLayout.setObjectName(u'AuthorRemoveLayout')
        spacerItem1 = QtGui.QSpacerItem(40, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.AuthorRemoveLayout.addItem(spacerItem1)
        self.AuthorRemoveButton = QtGui.QPushButton(self.AuthorRemoveWidget)
        self.AuthorRemoveButton.setObjectName(u'AuthorRemoveButton')
        self.AuthorRemoveLayout.addWidget(self.AuthorRemoveButton)
        self.AuthorsLayout.addWidget(self.AuthorRemoveWidget)
        self.AuthorsMaintenanceLayout.addWidget(self.AuthorsGroupBox)
        self.MaintenanceWidget = QtGui.QWidget(self.AuthorsMaintenanceWidget)
        self.MaintenanceWidget.setObjectName(u'MaintenanceWidget')
        self.MaintenanceLayout = QtGui.QHBoxLayout(self.MaintenanceWidget)
        self.MaintenanceLayout.setSpacing(0)
        self.MaintenanceLayout.setMargin(0)
        self.MaintenanceLayout.setObjectName(u'MaintenanceLayout')
        self.MaintenanceButton = QtGui.QPushButton(self.MaintenanceWidget)
        self.MaintenanceButton.setObjectName(u'MaintenanceButton')
        self.MaintenanceLayout.addWidget(self.MaintenanceButton)
        spacerItem2 = QtGui.QSpacerItem(66, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.MaintenanceLayout.addItem(spacerItem2)
        self.AuthorsMaintenanceLayout.addWidget(self.MaintenanceWidget)
        self.AuthorsTabLayout.addWidget(self.AuthorsMaintenanceWidget)
        self.TopicBookWidget = QtGui.QWidget(self.AuthorsTab)
        self.TopicBookWidget.setObjectName(u'TopicBookWidget')
        self.TopicBookLayout = QtGui.QVBoxLayout(self.TopicBookWidget)
        self.TopicBookLayout.setSpacing(8)
        self.TopicBookLayout.setMargin(0)
        self.TopicBookLayout.setObjectName(u'TopicBookLayout')
        self.TopicGroupBox = QtGui.QGroupBox(self.TopicBookWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.TopicGroupBox.sizePolicy().hasHeightForWidth())
        self.TopicGroupBox.setSizePolicy(sizePolicy)
        self.TopicGroupBox.setObjectName(u'TopicGroupBox')
        self.TopicLayout = QtGui.QVBoxLayout(self.TopicGroupBox)
        self.TopicLayout.setSpacing(8)
        self.TopicLayout.setMargin(8)
        self.TopicLayout.setObjectName(u'TopicLayout')
        self.TopicAddWidget = QtGui.QWidget(self.TopicGroupBox)
        self.TopicAddWidget.setObjectName(u'TopicAddWidget')
        self.TopicAddLayout = QtGui.QHBoxLayout(self.TopicAddWidget)
        self.TopicAddLayout.setSpacing(8)
        self.TopicAddLayout.setMargin(0)
        self.TopicAddLayout.setObjectName(u'TopicAddLayout')
        self.SongTopicCombo = QtGui.QComboBox(self.TopicAddWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.SongTopicCombo.sizePolicy().hasHeightForWidth())
        self.SongTopicCombo.setEditable(True)
        self.SongTopicCombo.setSizePolicy(sizePolicy)
        self.SongTopicCombo.setObjectName(u'SongTopicCombo')
        self.TopicAddLayout.addWidget(self.SongTopicCombo)
        self.TopicAddButton = QtGui.QPushButton(self.TopicAddWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.TopicAddButton.sizePolicy().hasHeightForWidth())
        self.TopicAddButton.setSizePolicy(sizePolicy)
        self.TopicAddButton.setObjectName(u'TopicAddButton')
        self.TopicAddLayout.addWidget(self.TopicAddButton)
        self.TopicLayout.addWidget(self.TopicAddWidget)
        self.TopicsListView = QtGui.QListWidget(self.TopicGroupBox)
        self.TopicsListView.setAlternatingRowColors(True)
        self.TopicsListView.setObjectName(u'TopicsListView')
        self.TopicLayout.addWidget(self.TopicsListView)
        self.TopicRemoveWidget = QtGui.QWidget(self.TopicGroupBox)
        self.TopicRemoveWidget.setObjectName(u'TopicRemoveWidget')
        self.TopicRemoveLayout = QtGui.QHBoxLayout(self.TopicRemoveWidget)
        self.TopicRemoveLayout.setSpacing(8)
        self.TopicRemoveLayout.setMargin(0)
        self.TopicRemoveLayout.setObjectName(u'TopicRemoveLayout')
        spacerItem3 = QtGui.QSpacerItem(40, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.TopicRemoveLayout.addItem(spacerItem3)
        self.TopicRemoveButton = QtGui.QPushButton(self.TopicRemoveWidget)
        self.TopicRemoveButton.setObjectName(u'TopicRemoveButton')
        self.TopicRemoveLayout.addWidget(self.TopicRemoveButton)
        self.TopicLayout.addWidget(self.TopicRemoveWidget)
        self.TopicBookLayout.addWidget(self.TopicGroupBox)
        self.SongBookGroup = QtGui.QGroupBox(self.TopicBookWidget)
        self.SongBookGroup.setObjectName(u'SongBookGroup')
        self.SongbookLayout = QtGui.QGridLayout(self.SongBookGroup)
        self.SongbookLayout.setMargin(8)
        self.SongbookLayout.setSpacing(8)
        self.SongbookLayout.setObjectName(u'SongbookLayout')
        self.SongbookCombo = QtGui.QComboBox(self.SongBookGroup)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.SongbookCombo.sizePolicy().hasHeightForWidth())
        self.SongbookCombo.setEditable(True)
        self.SongbookCombo.setSizePolicy(sizePolicy)
        self.SongbookCombo.setObjectName(u'SongbookCombo')
        self.SongbookLayout.addWidget(self.SongbookCombo, 0, 0, 1, 1)
        self.TopicBookLayout.addWidget(self.SongBookGroup)
        self.AuthorsTabLayout.addWidget(self.TopicBookWidget)
        self.SongTabWidget.addTab(self.AuthorsTab, u'')
        self.ThemeTab = QtGui.QWidget()
        self.ThemeTab.setObjectName(u'ThemeTab')
        self.ThemeTabLayout = QtGui.QVBoxLayout(self.ThemeTab)
        self.ThemeTabLayout.setSpacing(8)
        self.ThemeTabLayout.setMargin(8)
        self.ThemeTabLayout.setObjectName(u'ThemeTabLayout')
        self.ThemeCopyCommentsWidget = QtGui.QWidget(self.ThemeTab)
        self.ThemeCopyCommentsWidget.setObjectName(u'ThemeCopyCommentsWidget')
        self.ThemeCopyCommentsLayout = QtGui.QHBoxLayout(
            self.ThemeCopyCommentsWidget)
        self.ThemeCopyCommentsLayout.setSpacing(8)
        self.ThemeCopyCommentsLayout.setMargin(0)
        self.ThemeCopyCommentsLayout.setObjectName(u'ThemeCopyCommentsLayout')
        self.TextWidget = QtGui.QWidget(self.ThemeCopyCommentsWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.TextWidget.sizePolicy().hasHeightForWidth())
        self.TextWidget.setSizePolicy(sizePolicy)
        self.TextWidget.setObjectName(u'TextWidget')
        self.DetailsLayout = QtGui.QVBoxLayout(self.TextWidget)
        self.DetailsLayout.setSpacing(8)
        self.DetailsLayout.setMargin(0)
        self.DetailsLayout.setObjectName(u'DetailsLayout')
        self.ThemeGroupBox = QtGui.QGroupBox(self.TextWidget)
        self.ThemeGroupBox.setObjectName(u'ThemeGroupBox')
        self.ThemeLayout = QtGui.QHBoxLayout(self.ThemeGroupBox)
        self.ThemeLayout.setSpacing(8)
        self.ThemeLayout.setMargin(8)
        self.ThemeLayout.setObjectName(u'ThemeLayout')
        self.ThemeSelectionComboItem = QtGui.QComboBox(self.ThemeGroupBox)
        self.ThemeSelectionComboItem.setEditable(True)
        self.ThemeSelectionComboItem.setObjectName(u'ThemeSelectionComboItem')
        self.ThemeLayout.addWidget(self.ThemeSelectionComboItem)
        self.ThemeAddButton = QtGui.QPushButton(self.ThemeGroupBox)
        self.ThemeAddButton.setMaximumSize(QtCore.QSize(110, 16777215))
        self.ThemeAddButton.setObjectName(u'ThemeAddButton')
        self.ThemeLayout.addWidget(self.ThemeAddButton)
        self.DetailsLayout.addWidget(self.ThemeGroupBox)
        self.CopyrightGroupBox = QtGui.QGroupBox(self.TextWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.CopyrightGroupBox.sizePolicy().hasHeightForWidth())
        self.CopyrightGroupBox.setSizePolicy(sizePolicy)
        self.CopyrightGroupBox.setObjectName(u'CopyrightGroupBox')
        self.CopyrightLayout = QtGui.QVBoxLayout(self.CopyrightGroupBox)
        self.CopyrightLayout.setSpacing(8)
        self.CopyrightLayout.setMargin(8)
        self.CopyrightLayout.setObjectName(u'CopyrightLayout')
        self.CopyrightWidget = QtGui.QWidget(self.CopyrightGroupBox)
        self.CopyrightWidget.setObjectName(u'CopyrightWidget')
        self.CopyLayout = QtGui.QHBoxLayout(self.CopyrightWidget)
        self.CopyLayout.setSpacing(8)
        self.CopyLayout.setMargin(0)
        self.CopyLayout.setObjectName(u'CopyLayout')
        self.CopyrightEditItem = QtGui.QLineEdit(self.CopyrightWidget)
        self.CopyrightEditItem.setObjectName(u'CopyrightEditItem')
        self.CopyLayout.addWidget(self.CopyrightEditItem)
        self.CopyrightInsertButton = QtGui.QPushButton(self.CopyrightWidget)
        self.CopyrightInsertButton.setMaximumSize(QtCore.QSize(29, 16777215))
        self.CopyrightInsertButton.setObjectName(u'CopyrightInsertButton')
        self.CopyLayout.addWidget(self.CopyrightInsertButton)
        self.CopyrightLayout.addWidget(self.CopyrightWidget)
        self.CcliWidget = QtGui.QWidget(self.CopyrightGroupBox)
        self.CcliWidget.setObjectName(u'CcliWidget')
        self.CCLILayout = QtGui.QHBoxLayout(self.CcliWidget)
        self.CCLILayout.setSpacing(8)
        self.CCLILayout.setMargin(0)
        self.CCLILayout.setObjectName(u'CCLILayout')
        self.CCLILabel = QtGui.QLabel(self.CcliWidget)
        self.CCLILabel.setObjectName(u'CCLILabel')
        self.CCLILayout.addWidget(self.CCLILabel)
        self.CCLNumberEdit = QtGui.QLineEdit(self.CcliWidget)
        self.CCLNumberEdit.setObjectName(u'CCLNumberEdit')
        self.CCLILayout.addWidget(self.CCLNumberEdit)
        self.CopyrightLayout.addWidget(self.CcliWidget)
        self.DetailsLayout.addWidget(self.CopyrightGroupBox)
        spacerItem4 = QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.DetailsLayout.addItem(spacerItem4)
        self.ThemeCopyCommentsLayout.addWidget(self.TextWidget)
        self.CommentsGroupBox = QtGui.QGroupBox(self.ThemeCopyCommentsWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.CommentsGroupBox.sizePolicy().hasHeightForWidth())
        self.CommentsGroupBox.setSizePolicy(sizePolicy)
        self.CommentsGroupBox.setObjectName(u'CommentsGroupBox')
        self.CommentsLayout = QtGui.QVBoxLayout(self.CommentsGroupBox)
        self.CommentsLayout.setSpacing(0)
        self.CommentsLayout.setMargin(8)
        self.CommentsLayout.setObjectName(u'CommentsLayout')
        self.CommentsEdit = QtGui.QTextEdit(self.CommentsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.CommentsEdit.sizePolicy().hasHeightForWidth())
        self.CommentsEdit.setSizePolicy(sizePolicy)
        self.CommentsEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.CommentsEdit.setObjectName(u'CommentsEdit')
        self.CommentsLayout.addWidget(self.CommentsEdit)
        self.ThemeCopyCommentsLayout.addWidget(self.CommentsGroupBox)
        self.ThemeTabLayout.addWidget(self.ThemeCopyCommentsWidget)
        self.SongTabWidget.addTab(self.ThemeTab, u'')
        self.verticalLayout.addWidget(self.SongTabWidget)
        self.ButtonBox = QtGui.QDialogButtonBox(EditSongDialog)
        self.ButtonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        self.ButtonBox.setObjectName(u'ButtonBox')
        self.verticalLayout.addWidget(self.ButtonBox)

        self.retranslateUi(EditSongDialog)
        QtCore.QObject.connect(self.ButtonBox,
            QtCore.SIGNAL(u'rejected()'), EditSongDialog.closePressed)
        QtCore.QObject.connect(self.ButtonBox,
            QtCore.SIGNAL(u'accepted()'), EditSongDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(EditSongDialog)
        EditSongDialog.setTabOrder(self.SongTabWidget, self.TitleEditItem)
        EditSongDialog.setTabOrder(self.TitleEditItem, self.AlternativeEdit)
        EditSongDialog.setTabOrder(self.AlternativeEdit, self.VerseListWidget)
        EditSongDialog.setTabOrder(self.VerseListWidget, self.VerseAddButton)
        EditSongDialog.setTabOrder(self.VerseAddButton, self.VerseEditButton)
        EditSongDialog.setTabOrder(self.VerseEditButton,
            self.VerseEditAllButton)
        EditSongDialog.setTabOrder(self.VerseEditAllButton,
            self.VerseDeleteButton)
        EditSongDialog.setTabOrder(self.VerseDeleteButton, self.VerseOrderEdit)
        EditSongDialog.setTabOrder(self.VerseOrderEdit,
            self.AuthorsSelectionComboItem)
        EditSongDialog.setTabOrder(self.AuthorsSelectionComboItem,
            self.AuthorAddButton)
        EditSongDialog.setTabOrder(self.AuthorAddButton, self.AuthorsListView)
        EditSongDialog.setTabOrder(self.AuthorsListView,
            self.AuthorRemoveButton)
        EditSongDialog.setTabOrder(self.AuthorRemoveButton,
            self.MaintenanceButton)
        EditSongDialog.setTabOrder(self.MaintenanceButton, self.SongTopicCombo)
        EditSongDialog.setTabOrder(self.SongTopicCombo, self.TopicAddButton)
        EditSongDialog.setTabOrder(self.TopicAddButton, self.TopicsListView)
        EditSongDialog.setTabOrder(self.TopicsListView, self.TopicRemoveButton)
        EditSongDialog.setTabOrder(self.TopicRemoveButton, self.SongbookCombo)
        EditSongDialog.setTabOrder(self.SongbookCombo,
            self.ThemeSelectionComboItem)
        EditSongDialog.setTabOrder(self.ThemeSelectionComboItem,
            self.ThemeAddButton)
        EditSongDialog.setTabOrder(self.ThemeAddButton, self.CopyrightEditItem)
        EditSongDialog.setTabOrder(self.CopyrightEditItem,
            self.CopyrightInsertButton)
        EditSongDialog.setTabOrder(self.CopyrightInsertButton,
            self.CCLNumberEdit)
        EditSongDialog.setTabOrder(self.CCLNumberEdit, self.CommentsEdit)
        EditSongDialog.setTabOrder(self.CommentsEdit, self.ButtonBox)

    def retranslateUi(self, EditSongDialog):
        EditSongDialog.setWindowTitle(
            translate('SongsPlugin.EditSongForm', 'Song Editor'))
        self.TitleLabel.setText(
            translate('SongsPlugin.EditSongForm', '&Title:'))
        self.AlternativeTitleLabel.setText(
            translate('SongsPlugin.EditSongForm', 'Alt&ernate Title:'))
        self.LyricsLabel.setText(
            translate('SongsPlugin.EditSongForm', '&Lyrics:'))
        self.VerseOrderLabel.setText(
            translate('SongsPlugin.EditSongForm', '&Verse Order:'))
        self.VerseAddButton.setText(
            translate('SongsPlugin.EditSongForm', '&Add'))
        self.VerseEditButton.setText(
            translate('SongsPlugin.EditSongForm', '&Edit'))
        self.VerseEditAllButton.setText(
            translate('SongsPlugin.EditSongForm', 'Ed&it All'))
        self.VerseDeleteButton.setText(
            translate('SongsPlugin.EditSongForm', '&Delete'))
        self.SongTabWidget.setTabText(
            self.SongTabWidget.indexOf(self.LyricsTab),
            translate('SongsPlugin.EditSongForm', 'Title && Lyrics'))
        self.AuthorsGroupBox.setTitle(
            translate('SongsPlugin.EditSongForm', 'Authors'))
        self.AuthorAddButton.setText(
            translate('SongsPlugin.EditSongForm', '&Add to Song'))
        self.AuthorRemoveButton.setText(
            translate('SongsPlugin.EditSongForm', '&Remove'))
        self.MaintenanceButton.setText(translate('SongsPlugin.EditSongForm',
            '&Manage Authors, Topics, Books'))
        self.TopicGroupBox.setTitle(
            translate('SongsPlugin.EditSongForm', 'Topic'))
        self.TopicAddButton.setText(
            translate('SongsPlugin.EditSongForm', 'A&dd to Song'))
        self.TopicRemoveButton.setText(
            translate('SongsPlugin.EditSongForm', 'R&emove'))
        self.SongBookGroup.setTitle(
            translate('SongsPlugin.EditSongForm', 'Song Book'))
        self.SongTabWidget.setTabText(
            self.SongTabWidget.indexOf(self.AuthorsTab),
            translate('SongsPlugin.EditSongForm', 'Authors, Topics && Book'))
        self.ThemeGroupBox.setTitle(
            translate('SongsPlugin.EditSongForm', 'Theme'))
        self.ThemeAddButton.setText(
            translate('SongsPlugin.EditSongForm', 'New &Theme'))
        self.CopyrightGroupBox.setTitle(
            translate('SongsPlugin.EditSongForm', 'Copyright Information'))
        self.CopyrightInsertButton.setText(
            translate('SongsPlugin.EditSongForm', '\xa9'))
        self.CCLILabel.setText(
            translate('SongsPlugin.EditSongForm', 'CCLI Number:'))
        self.CommentsGroupBox.setTitle(
            translate('SongsPlugin.EditSongForm', 'Comments'))
        self.SongTabWidget.setTabText(
            self.SongTabWidget.indexOf(self.ThemeTab),
            translate('SongsPlugin.EditSongForm',
                'Theme, Copyright Info && Comments'))
