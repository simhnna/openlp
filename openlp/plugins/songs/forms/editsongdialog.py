# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/raoul/Projects/openlp-2/resources/forms/editsongdialog.ui'
#
# Created: Thu Feb 19 23:35:35 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_EditSongDialog(object):
    def setupUi(self, EditSongDialog):
        EditSongDialog.setObjectName("EditSongDialog")
        EditSongDialog.resize(786, 704)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/openlp-logo-16x16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EditSongDialog.setWindowIcon(icon)
        EditSongDialog.setModal(True)
        self.EditSongLayout = QtGui.QVBoxLayout(EditSongDialog)
        self.EditSongLayout.setSpacing(8)
        self.EditSongLayout.setMargin(8)
        self.EditSongLayout.setObjectName("EditSongLayout")
        self.TopWidget = QtGui.QWidget(EditSongDialog)
        self.TopWidget.setObjectName("TopWidget")
        self.TopLayout = QtGui.QHBoxLayout(self.TopWidget)
        self.TopLayout.setSpacing(8)
        self.TopLayout.setMargin(0)
        self.TopLayout.setObjectName("TopLayout")
        self.TextWidget = QtGui.QWidget(self.TopWidget)
        self.TextWidget.setObjectName("TextWidget")
        self.DetailsLayout = QtGui.QVBoxLayout(self.TextWidget)
        self.DetailsLayout.setSpacing(8)
        self.DetailsLayout.setMargin(0)
        self.DetailsLayout.setObjectName("DetailsLayout")
        self.TitleLabel = QtGui.QLabel(self.TextWidget)
        self.TitleLabel.setObjectName("TitleLabel")
        self.DetailsLayout.addWidget(self.TitleLabel)
        self.TitleEditItem = QtGui.QLineEdit(self.TextWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TitleEditItem.sizePolicy().hasHeightForWidth())
        self.TitleEditItem.setSizePolicy(sizePolicy)
        self.TitleEditItem.setObjectName("TitleEditItem")
        self.DetailsLayout.addWidget(self.TitleEditItem)
        self.AlternativeTitleLabel = QtGui.QLabel(self.TextWidget)
        self.AlternativeTitleLabel.setObjectName("AlternativeTitleLabel")
        self.DetailsLayout.addWidget(self.AlternativeTitleLabel)
        self.AlternativeEdit = QtGui.QLineEdit(self.TextWidget)
        self.AlternativeEdit.setObjectName("AlternativeEdit")
        self.DetailsLayout.addWidget(self.AlternativeEdit)
        self.LyricsLabel = QtGui.QLabel(self.TextWidget)
        self.LyricsLabel.setObjectName("LyricsLabel")
        self.DetailsLayout.addWidget(self.LyricsLabel)
        self.VerseEditWidget = QtGui.QWidget(self.TextWidget)
        self.VerseEditWidget.setObjectName("VerseEditWidget")
        self.VerseEditLayout = QtGui.QVBoxLayout(self.VerseEditWidget)
        self.VerseEditLayout.setSpacing(8)
        self.VerseEditLayout.setMargin(0)
        self.VerseEditLayout.setObjectName("VerseEditLayout")
        self.VerseListWidget = QtGui.QListWidget(self.VerseEditWidget)
        self.VerseListWidget.setObjectName("VerseListWidget")
        self.VerseEditLayout.addWidget(self.VerseListWidget)
        self.VerseButtonWidget = QtGui.QWidget(self.VerseEditWidget)
        self.VerseButtonWidget.setObjectName("VerseButtonWidget")
        self.VerseButtonLayout = QtGui.QHBoxLayout(self.VerseButtonWidget)
        self.VerseButtonLayout.setSpacing(8)
        self.VerseButtonLayout.setMargin(0)
        self.VerseButtonLayout.setObjectName("VerseButtonLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.VerseButtonLayout.addItem(spacerItem)
        self.AddButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.AddButton.setObjectName("AddButton")
        self.VerseButtonLayout.addWidget(self.AddButton)
        self.EditButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.EditButton.setObjectName("EditButton")
        self.VerseButtonLayout.addWidget(self.EditButton)
        self.DeleteButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.DeleteButton.setObjectName("DeleteButton")
        self.VerseButtonLayout.addWidget(self.DeleteButton)
        self.VerseEditLayout.addWidget(self.VerseButtonWidget)
        self.DetailsLayout.addWidget(self.VerseEditWidget)
        self.VerseOrderLabel = QtGui.QLabel(self.TextWidget)
        self.VerseOrderLabel.setObjectName("VerseOrderLabel")
        self.DetailsLayout.addWidget(self.VerseOrderLabel)
        self.VerseOrderEdit = QtGui.QLineEdit(self.TextWidget)
        self.VerseOrderEdit.setObjectName("VerseOrderEdit")
        self.DetailsLayout.addWidget(self.VerseOrderEdit)
        self.CommentsLabel = QtGui.QLabel(self.TextWidget)
        self.CommentsLabel.setObjectName("CommentsLabel")
        self.DetailsLayout.addWidget(self.CommentsLabel)
        self.CommentsEdit = QtGui.QTextEdit(self.TextWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CommentsEdit.sizePolicy().hasHeightForWidth())
        self.CommentsEdit.setSizePolicy(sizePolicy)
        self.CommentsEdit.setMaximumSize(QtCore.QSize(16777215, 84))
        self.CommentsEdit.setObjectName("CommentsEdit")
        self.DetailsLayout.addWidget(self.CommentsEdit)
        self.ThemeGroupBox = QtGui.QGroupBox(self.TextWidget)
        self.ThemeGroupBox.setObjectName("ThemeGroupBox")
        self.ThemeLayout = QtGui.QHBoxLayout(self.ThemeGroupBox)
        self.ThemeLayout.setSpacing(8)
        self.ThemeLayout.setMargin(8)
        self.ThemeLayout.setObjectName("ThemeLayout")
        self.ThemeSelectionComboItem = QtGui.QComboBox(self.ThemeGroupBox)
        self.ThemeSelectionComboItem.setObjectName("ThemeSelectionComboItem")
        self.ThemeLayout.addWidget(self.ThemeSelectionComboItem)
#        self.ThemeAddItem = QtGui.QPushButton(self.ThemeGroupBox)
#        self.ThemeAddItem.setMaximumSize(QtCore.QSize(110, 16777215))
#        self.ThemeAddItem.setObjectName("ThemeAddItem")
#        self.ThemeLayout.addWidget(self.ThemeAddItem)
        self.DetailsLayout.addWidget(self.ThemeGroupBox)
        self.TopLayout.addWidget(self.TextWidget)
        self.AdditionalWidget = QtGui.QWidget(self.TopWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AdditionalWidget.sizePolicy().hasHeightForWidth())
        self.AdditionalWidget.setSizePolicy(sizePolicy)
        self.AdditionalWidget.setMinimumSize(QtCore.QSize(100, 0))
        self.AdditionalWidget.setObjectName("AdditionalWidget")
        self.AdditionalLayout = QtGui.QVBoxLayout(self.AdditionalWidget)
        self.AdditionalLayout.setSpacing(8)
        self.AdditionalLayout.setMargin(0)
        self.AdditionalLayout.setObjectName("AdditionalLayout")
        self.AuthorsGroupBox = QtGui.QGroupBox(self.AdditionalWidget)
        self.AuthorsGroupBox.setObjectName("AuthorsGroupBox")
        self.AuthorsLayout = QtGui.QVBoxLayout(self.AuthorsGroupBox)
        self.AuthorsLayout.setSpacing(8)
        self.AuthorsLayout.setMargin(8)
        self.AuthorsLayout.setObjectName("AuthorsLayout")
        self.AuthorAddWidget = QtGui.QWidget(self.AuthorsGroupBox)
        self.AuthorAddWidget.setObjectName("AuthorAddWidget")
        self.AddAuthorLayout = QtGui.QHBoxLayout(self.AuthorAddWidget)
        self.AddAuthorLayout.setSpacing(8)
        self.AddAuthorLayout.setMargin(0)
        self.AddAuthorLayout.setObjectName("AddAuthorLayout")
        self.AuthorsSelectionComboItem = QtGui.QComboBox(self.AuthorAddWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AuthorsSelectionComboItem.sizePolicy().hasHeightForWidth())
        self.AuthorsSelectionComboItem.setSizePolicy(sizePolicy)
        self.AuthorsSelectionComboItem.setEditable(False)
        self.AuthorsSelectionComboItem.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.AuthorsSelectionComboItem.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.AuthorsSelectionComboItem.setMinimumContentsLength(8)
        self.AuthorsSelectionComboItem.setObjectName("AuthorsSelectionComboItem")
        self.AddAuthorLayout.addWidget(self.AuthorsSelectionComboItem)
        self.AuthorAddtoSongItem = QtGui.QPushButton(self.AuthorAddWidget)
        self.AuthorAddtoSongItem.setMaximumSize(QtCore.QSize(110, 16777215))
        self.AuthorAddtoSongItem.setObjectName("AuthorAddtoSongItem")
        self.AddAuthorLayout.addWidget(self.AuthorAddtoSongItem)
        self.AuthorsLayout.addWidget(self.AuthorAddWidget)
        self.AuthorsListView = QtGui.QTableWidget(self.AuthorsGroupBox)
        self.AuthorsListView.setAlternatingRowColors(True)
        self.AuthorsListView.setObjectName("AuthorsListView")
        self.AuthorsListView.setColumnCount(0)
        self.AuthorsListView.setRowCount(0)
        self.AuthorsLayout.addWidget(self.AuthorsListView)
        self.AuthorRemoveWidget = QtGui.QWidget(self.AuthorsGroupBox)
        self.AuthorRemoveWidget.setObjectName("AuthorRemoveWidget")
        self.AuthorRemoveLayout = QtGui.QHBoxLayout(self.AuthorRemoveWidget)
        self.AuthorRemoveLayout.setSpacing(8)
        self.AuthorRemoveLayout.setMargin(0)
        self.AuthorRemoveLayout.setObjectName("AuthorRemoveLayout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.AuthorRemoveLayout.addItem(spacerItem1)
        self.AuthorRemoveItem = QtGui.QPushButton(self.AuthorRemoveWidget)
        self.AuthorRemoveItem.setObjectName("AuthorRemoveItem")
        self.AuthorRemoveLayout.addWidget(self.AuthorRemoveItem)
        self.AddAuthorsButton = QtGui.QPushButton(self.AuthorRemoveWidget)
        self.AddAuthorsButton.setObjectName("AddAuthorsButton")
        self.AuthorRemoveLayout.addWidget(self.AddAuthorsButton)
        self.AuthorsLayout.addWidget(self.AuthorRemoveWidget)
        self.AdditionalLayout.addWidget(self.AuthorsGroupBox)
        self.SongBookGroup = QtGui.QGroupBox(self.AdditionalWidget)
        self.SongBookGroup.setObjectName("SongBookGroup")
        self.SongbookLayout = QtGui.QGridLayout(self.SongBookGroup)
        self.SongbookLayout.setMargin(8)
        self.SongbookLayout.setSpacing(8)
        self.SongbookLayout.setObjectName("SongbookLayout")
        self.SongbookCombo = QtGui.QComboBox(self.SongBookGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SongbookCombo.sizePolicy().hasHeightForWidth())
        self.SongbookCombo.setSizePolicy(sizePolicy)
        self.SongbookCombo.setObjectName("SongbookCombo")
        self.SongbookLayout.addWidget(self.SongbookCombo, 0, 0, 1, 1)
        self.AddSongBookButton = QtGui.QPushButton(self.SongBookGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AddSongBookButton.sizePolicy().hasHeightForWidth())
        self.AddSongBookButton.setSizePolicy(sizePolicy)
        self.AddSongBookButton.setObjectName("AddSongBookButton")
        self.SongbookLayout.addWidget(self.AddSongBookButton, 0, 1, 1, 1)
        self.AdditionalLayout.addWidget(self.SongBookGroup)
        self.TopicGroupBox = QtGui.QGroupBox(self.AdditionalWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TopicGroupBox.sizePolicy().hasHeightForWidth())
        self.TopicGroupBox.setSizePolicy(sizePolicy)
        self.TopicGroupBox.setObjectName("TopicGroupBox")
        self.TopicLayout = QtGui.QVBoxLayout(self.TopicGroupBox)
        self.TopicLayout.setSpacing(8)
        self.TopicLayout.setMargin(8)
        self.TopicLayout.setObjectName("TopicLayout")
        self.TopicAddWidget = QtGui.QWidget(self.TopicGroupBox)
        self.TopicAddWidget.setObjectName("TopicAddWidget")
        self.TopicAddLayout = QtGui.QHBoxLayout(self.TopicAddWidget)
        self.TopicAddLayout.setSpacing(8)
        self.TopicAddLayout.setMargin(0)
        self.TopicAddLayout.setObjectName("TopicAddLayout")
        self.SongTopicCombo = QtGui.QComboBox(self.TopicAddWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SongTopicCombo.sizePolicy().hasHeightForWidth())
        self.SongTopicCombo.setSizePolicy(sizePolicy)
        self.SongTopicCombo.setObjectName("SongTopicCombo")
        self.TopicAddLayout.addWidget(self.SongTopicCombo)
        self.AddTopicsToSongButton = QtGui.QPushButton(self.TopicAddWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AddTopicsToSongButton.sizePolicy().hasHeightForWidth())
        self.AddTopicsToSongButton.setSizePolicy(sizePolicy)
        self.AddTopicsToSongButton.setObjectName("AddTopicsToSongButton")
        self.TopicAddLayout.addWidget(self.AddTopicsToSongButton)
        self.TopicLayout.addWidget(self.TopicAddWidget)
        self.ToticsListView = QtGui.QTableWidget(self.TopicGroupBox)
        self.ToticsListView.setAlternatingRowColors(True)
        self.ToticsListView.setObjectName("ToticsListView")
        self.ToticsListView.setColumnCount(0)
        self.ToticsListView.setRowCount(0)
        self.TopicLayout.addWidget(self.ToticsListView)
        self.TopicRemoveWidget = QtGui.QWidget(self.TopicGroupBox)
        self.TopicRemoveWidget.setObjectName("TopicRemoveWidget")
        self.TopicRemoveLayout = QtGui.QHBoxLayout(self.TopicRemoveWidget)
        self.TopicRemoveLayout.setSpacing(8)
        self.TopicRemoveLayout.setMargin(0)
        self.TopicRemoveLayout.setObjectName("TopicRemoveLayout")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.TopicRemoveLayout.addItem(spacerItem2)
        self.pushButton = QtGui.QPushButton(self.TopicRemoveWidget)
        self.pushButton.setObjectName("pushButton")
        self.TopicRemoveLayout.addWidget(self.pushButton)
        self.AddTopicButton = QtGui.QPushButton(self.TopicRemoveWidget)
        self.AddTopicButton.setObjectName("AddTopicButton")
        self.TopicRemoveLayout.addWidget(self.AddTopicButton)
        self.TopicLayout.addWidget(self.TopicRemoveWidget)
        self.AdditionalLayout.addWidget(self.TopicGroupBox)
        self.CopyrightgroupBox = QtGui.QGroupBox(self.AdditionalWidget)
        self.CopyrightgroupBox.setObjectName("CopyrightgroupBox")
        self.CopyrightLayout = QtGui.QVBoxLayout(self.CopyrightgroupBox)
        self.CopyrightLayout.setSpacing(8)
        self.CopyrightLayout.setMargin(8)
        self.CopyrightLayout.setObjectName("CopyrightLayout")
        self.CopyrightWidget = QtGui.QWidget(self.CopyrightgroupBox)
        self.CopyrightWidget.setObjectName("CopyrightWidget")
        self.CopyLayout = QtGui.QHBoxLayout(self.CopyrightWidget)
        self.CopyLayout.setSpacing(8)
        self.CopyLayout.setMargin(0)
        self.CopyLayout.setObjectName("CopyLayout")
        self.CopyrightEditItem = QtGui.QLineEdit(self.CopyrightWidget)
        self.CopyrightEditItem.setObjectName("CopyrightEditItem")
        self.CopyLayout.addWidget(self.CopyrightEditItem)
        self.CopyrightInsertItem = QtGui.QPushButton(self.CopyrightWidget)
        self.CopyrightInsertItem.setMaximumSize(QtCore.QSize(29, 16777215))
        self.CopyrightInsertItem.setObjectName("CopyrightInsertItem")
        self.CopyLayout.addWidget(self.CopyrightInsertItem)
        self.CopyrightLayout.addWidget(self.CopyrightWidget)
        self.CcliWidget = QtGui.QWidget(self.CopyrightgroupBox)
        self.CcliWidget.setObjectName("CcliWidget")
        self.CCLILayout = QtGui.QHBoxLayout(self.CcliWidget)
        self.CCLILayout.setSpacing(8)
        self.CCLILayout.setMargin(0)
        self.CCLILayout.setObjectName("CCLILayout")
        self.CCLILabel = QtGui.QLabel(self.CcliWidget)
        self.CCLILabel.setObjectName("CCLILabel")
        self.CCLILayout.addWidget(self.CCLILabel)
        self.CCLNumberEdit = QtGui.QLineEdit(self.CcliWidget)
        self.CCLNumberEdit.setObjectName("CCLNumberEdit")
        self.CCLILayout.addWidget(self.CCLNumberEdit)
        self.CopyrightLayout.addWidget(self.CcliWidget)
        self.AdditionalLayout.addWidget(self.CopyrightgroupBox)
        self.TopLayout.addWidget(self.AdditionalWidget)
        self.EditSongLayout.addWidget(self.TopWidget)
        self.ButtonBox = QtGui.QDialogButtonBox(EditSongDialog)
        self.ButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.ButtonBox.setObjectName("ButtonBox")
        self.EditSongLayout.addWidget(self.ButtonBox)

        self.retranslateUi(EditSongDialog)
        QtCore.QObject.connect(self.ButtonBox, QtCore.SIGNAL("rejected()"), EditSongDialog.close)
        QtCore.QObject.connect(self.ButtonBox, QtCore.SIGNAL("accepted()"), EditSongDialog.close)
        QtCore.QMetaObject.connectSlotsByName(EditSongDialog)
        EditSongDialog.setTabOrder(self.TitleEditItem, self.AlternativeEdit)
        EditSongDialog.setTabOrder(self.AlternativeEdit, self.VerseOrderEdit)
        EditSongDialog.setTabOrder(self.VerseOrderEdit, self.CommentsEdit)
        EditSongDialog.setTabOrder(self.CommentsEdit, self.ThemeSelectionComboItem)
        EditSongDialog.setTabOrder(self.ThemeSelectionComboItem, self.AuthorAddtoSongItem)
        EditSongDialog.setTabOrder(self.AuthorAddtoSongItem, self.AuthorsListView)
        EditSongDialog.setTabOrder(self.AuthorsListView, self.AuthorRemoveItem)
        EditSongDialog.setTabOrder(self.AuthorRemoveItem, self.SongbookCombo)
        EditSongDialog.setTabOrder(self.SongbookCombo, self.AddSongBookButton)
        EditSongDialog.setTabOrder(self.AddSongBookButton, self.SongTopicCombo)
        EditSongDialog.setTabOrder(self.SongTopicCombo, self.ToticsListView)
        EditSongDialog.setTabOrder(self.ToticsListView, self.pushButton)
        EditSongDialog.setTabOrder(self.pushButton, self.CopyrightEditItem)
        EditSongDialog.setTabOrder(self.CopyrightEditItem, self.CopyrightInsertItem)
        EditSongDialog.setTabOrder(self.CopyrightInsertItem, self.CCLNumberEdit)
        EditSongDialog.setTabOrder(self.CCLNumberEdit, self.ButtonBox)

    def retranslateUi(self, EditSongDialog):
        EditSongDialog.setWindowTitle(QtGui.QApplication.translate("EditSongDialog", "Song Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.TitleLabel.setText(QtGui.QApplication.translate("EditSongDialog", "Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.AlternativeTitleLabel.setText(QtGui.QApplication.translate("EditSongDialog", "Alternative Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.LyricsLabel.setText(QtGui.QApplication.translate("EditSongDialog", "Lyrics:", None, QtGui.QApplication.UnicodeUTF8))
        self.AddButton.setText(QtGui.QApplication.translate("EditSongDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.EditButton.setText(QtGui.QApplication.translate("EditSongDialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.DeleteButton.setText(QtGui.QApplication.translate("EditSongDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.VerseOrderLabel.setText(QtGui.QApplication.translate("EditSongDialog", "Verse Order:", None, QtGui.QApplication.UnicodeUTF8))
        self.CommentsLabel.setText(QtGui.QApplication.translate("EditSongDialog", "Comments:", None, QtGui.QApplication.UnicodeUTF8))
        self.ThemeGroupBox.setTitle(QtGui.QApplication.translate("EditSongDialog", "Theme", None, QtGui.QApplication.UnicodeUTF8))
        self.AuthorsGroupBox.setTitle(QtGui.QApplication.translate("EditSongDialog", "Authors", None, QtGui.QApplication.UnicodeUTF8))
        self.AuthorAddtoSongItem.setText(QtGui.QApplication.translate("EditSongDialog", "Add to Song", None, QtGui.QApplication.UnicodeUTF8))
        self.AuthorRemoveItem.setText(QtGui.QApplication.translate("EditSongDialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.AddAuthorsButton.setText(QtGui.QApplication.translate("EditSongDialog", "Manage Authors", None, QtGui.QApplication.UnicodeUTF8))
        self.SongBookGroup.setTitle(QtGui.QApplication.translate("EditSongDialog", "Song Book", None, QtGui.QApplication.UnicodeUTF8))
        self.AddSongBookButton.setText(QtGui.QApplication.translate("EditSongDialog", "Manage Song Books", None, QtGui.QApplication.UnicodeUTF8))
        self.TopicGroupBox.setTitle(QtGui.QApplication.translate("EditSongDialog", "Topic", None, QtGui.QApplication.UnicodeUTF8))
        self.AddTopicsToSongButton.setText(QtGui.QApplication.translate("EditSongDialog", "Add to Song", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("EditSongDialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.AddTopicButton.setText(QtGui.QApplication.translate("EditSongDialog", "Manage Topics", None, QtGui.QApplication.UnicodeUTF8))
        self.CopyrightgroupBox.setTitle(QtGui.QApplication.translate("EditSongDialog", "Copyright Infomaton", None, QtGui.QApplication.UnicodeUTF8))
        self.CopyrightInsertItem.setText(QtGui.QApplication.translate("EditSongDialog", "©", None, QtGui.QApplication.UnicodeUTF8))
        self.CCLILabel.setText(QtGui.QApplication.translate("EditSongDialog", "CCLI Number:", None, QtGui.QApplication.UnicodeUTF8))
