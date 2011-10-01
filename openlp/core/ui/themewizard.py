# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2011 Raoul Snyman                                        #
# Portions copyright (c) 2008-2011 Tim Bentley, Gerald Britton, Jonathan      #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import translate, build_icon
from openlp.core.lib.theme import HorizontalType, BackgroundType, \
    BackgroundGradientType
from openlp.core.lib.ui import UiStrings, add_welcome_page, create_valign_combo

class Ui_ThemeWizard(object):
    def setupUi(self, themeWizard):
        themeWizard.setObjectName(u'OpenLP.ThemeWizard')
        themeWizard.setModal(True)
        themeWizard.setWizardStyle(QtGui.QWizard.ModernStyle)
        themeWizard.setOptions(QtGui.QWizard.IndependentPages |
            QtGui.QWizard.NoBackButtonOnStartPage |
            QtGui.QWizard.HaveCustomButton1)
        self.spacer = QtGui.QSpacerItem(10, 0,
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        # Welcome Page
        add_welcome_page(themeWizard, u':/wizards/wizard_createtheme.bmp')
        # Background Page
        self.backgroundPage = QtGui.QWizardPage()
        self.backgroundPage.setObjectName(u'BackgroundPage')
        self.backgroundLayout = QtGui.QVBoxLayout(self.backgroundPage)
        self.backgroundLayout.setObjectName(u'BackgroundLayout')
        self.backgroundTypeLayout = QtGui.QFormLayout()
        self.backgroundTypeLayout.setObjectName(u'BackgroundTypeLayout')
        self.backgroundLabel = QtGui.QLabel(self.backgroundPage)
        self.backgroundLabel.setObjectName(u'BackgroundLabel')
        self.backgroundComboBox = QtGui.QComboBox(self.backgroundPage)
        self.backgroundComboBox.addItems([u'', u'', u''])
        self.backgroundComboBox.setObjectName(u'BackgroundComboBox')
        self.backgroundTypeLayout.addRow(self.backgroundLabel,
            self.backgroundComboBox)
        self.backgroundTypeLayout.setItem(1, QtGui.QFormLayout.LabelRole,
            self.spacer)
        self.backgroundLayout.addLayout(self.backgroundTypeLayout)
        self.backgroundStack = QtGui.QStackedLayout()
        self.backgroundStack.setObjectName(u'BackgroundStack')
        self.colorWidget = QtGui.QWidget(self.backgroundPage)
        self.colorWidget.setObjectName(u'ColorWidget')
        self.colorLayout = QtGui.QFormLayout(self.colorWidget)
        self.colorLayout.setMargin(0)
        self.colorLayout.setObjectName(u'ColorLayout')
        self.colorLabel = QtGui.QLabel(self.colorWidget)
        self.colorLabel.setObjectName(u'ColorLabel')
        self.colorButton = QtGui.QPushButton(self.colorWidget)
        self.colorButton.setObjectName(u'ColorButton')
        self.colorLayout.addRow(self.colorLabel, self.colorButton)
        self.colorLayout.setItem(1, QtGui.QFormLayout.LabelRole, self.spacer)
        self.backgroundStack.addWidget(self.colorWidget)
        self.gradientWidget = QtGui.QWidget(self.backgroundPage)
        self.gradientWidget.setObjectName(u'GradientWidget')
        self.gradientLayout = QtGui.QFormLayout(self.gradientWidget)
        self.gradientLayout.setMargin(0)
        self.gradientLayout.setObjectName(u'GradientLayout')
        self.gradientStartLabel = QtGui.QLabel(self.gradientWidget)
        self.gradientStartLabel.setObjectName(u'GradientStartLabel')
        self.gradientStartButton = QtGui.QPushButton(self.gradientWidget)
        self.gradientStartButton.setObjectName(u'GradientStartButton')
        self.gradientLayout.addRow(self.gradientStartLabel,
            self.gradientStartButton)
        self.gradientEndLabel = QtGui.QLabel(self.gradientWidget)
        self.gradientEndLabel.setObjectName(u'GradientEndLabel')
        self.gradientEndButton = QtGui.QPushButton(self.gradientWidget)
        self.gradientEndButton.setObjectName(u'GradientEndButton')
        self.gradientLayout.addRow(self.gradientEndLabel,
            self.gradientEndButton)
        self.gradientTypeLabel = QtGui.QLabel(self.gradientWidget)
        self.gradientTypeLabel.setObjectName(u'GradientTypeLabel')
        self.gradientComboBox = QtGui.QComboBox(self.gradientWidget)
        self.gradientComboBox.setObjectName(u'GradientComboBox')
        self.gradientComboBox.addItems([u'', u'', u'', u'', u''])
        self.gradientLayout.addRow(self.gradientTypeLabel,
            self.gradientComboBox)
        self.gradientLayout.setItem(3, QtGui.QFormLayout.LabelRole, self.spacer)
        self.backgroundStack.addWidget(self.gradientWidget)
        self.imageWidget = QtGui.QWidget(self.backgroundPage)
        self.imageWidget.setObjectName(u'ImageWidget')
        self.imageLayout = QtGui.QFormLayout(self.imageWidget)
        self.imageLayout.setMargin(0)
        self.imageLayout.setObjectName(u'ImageLayout')
        self.imageColorLabel = QtGui.QLabel(self.colorWidget)
        self.imageColorLabel.setObjectName(u'ImageColorLabel')
        self.imageColorButton = QtGui.QPushButton(self.colorWidget)
        self.imageColorButton.setObjectName(u'ImageColorButton')
        self.imageLayout.addRow(self.imageColorLabel, self.imageColorButton)
        self.imageLabel = QtGui.QLabel(self.imageWidget)
        self.imageLabel.setObjectName(u'ImageLabel')
        self.imageFileLayout = QtGui.QHBoxLayout()
        self.imageFileLayout.setObjectName(u'ImageFileLayout')
        self.imageFileEdit = QtGui.QLineEdit(self.imageWidget)
        self.imageFileEdit.setObjectName(u'ImageFileEdit')
        self.imageFileLayout.addWidget(self.imageFileEdit)
        self.imageBrowseButton = QtGui.QToolButton(self.imageWidget)
        self.imageBrowseButton.setObjectName(u'ImageBrowseButton')
        self.imageBrowseButton.setIcon(
            build_icon(u':/general/general_open.png'))
        self.imageFileLayout.addWidget(self.imageBrowseButton)
        self.imageLayout.addRow(self.imageLabel, self.imageFileLayout)
        self.imageLayout.setItem(2, QtGui.QFormLayout.LabelRole, self.spacer)
        self.backgroundStack.addWidget(self.imageWidget)
        self.backgroundLayout.addLayout(self.backgroundStack)
        themeWizard.addPage(self.backgroundPage)
        # Main Area Page
        self.mainAreaPage = QtGui.QWizardPage()
        self.mainAreaPage.setObjectName(u'MainAreaPage')
        self.mainAreaLayout = QtGui.QFormLayout(self.mainAreaPage)
        self.mainAreaLayout.setObjectName(u'MainAreaLayout')
        self.mainFontLabel = QtGui.QLabel(self.mainAreaPage)
        self.mainFontLabel.setObjectName(u'MainFontLabel')
        self.mainFontComboBox = QtGui.QFontComboBox(self.mainAreaPage)
        self.mainFontComboBox.setObjectName(u'MainFontComboBox')
        self.mainAreaLayout.addRow(self.mainFontLabel, self.mainFontComboBox)
        self.mainColorLabel = QtGui.QLabel(self.mainAreaPage)
        self.mainColorLabel.setObjectName(u'MainColorLabel')
        self.mainPropertiesLayout = QtGui.QHBoxLayout()
        self.mainPropertiesLayout.setObjectName(u'MainPropertiesLayout')
        self.mainColorButton = QtGui.QPushButton(self.mainAreaPage)
        self.mainColorButton.setObjectName(u'MainColorButton')
        self.mainPropertiesLayout.addWidget(self.mainColorButton)
        self.mainPropertiesLayout.addSpacing(20)
        self.mainBoldCheckBox = QtGui.QCheckBox(self.mainAreaPage)
        self.mainBoldCheckBox.setObjectName(u'MainBoldCheckBox')
        self.mainPropertiesLayout.addWidget(self.mainBoldCheckBox)
        self.mainPropertiesLayout.addSpacing(20)
        self.mainItalicsCheckBox = QtGui.QCheckBox(self.mainAreaPage)
        self.mainItalicsCheckBox.setObjectName(u'MainItalicsCheckBox')
        self.mainPropertiesLayout.addWidget(self.mainItalicsCheckBox)
        self.mainAreaLayout.addRow(self.mainColorLabel,
            self.mainPropertiesLayout)
        self.mainSizeLabel = QtGui.QLabel(self.mainAreaPage)
        self.mainSizeLabel.setObjectName(u'MainSizeLabel')
        self.mainSizeLayout = QtGui.QHBoxLayout()
        self.mainSizeLayout.setObjectName(u'MainSizeLayout')
        self.mainSizeSpinBox = QtGui.QSpinBox(self.mainAreaPage)
        self.mainSizeSpinBox.setMaximum(999)
        self.mainSizeSpinBox.setValue(16)
        self.mainSizeSpinBox.setObjectName(u'MainSizeSpinBox')
        self.mainSizeLayout.addWidget(self.mainSizeSpinBox)
        self.mainLineCountLabel = QtGui.QLabel(self.mainAreaPage)
        self.mainLineCountLabel.setObjectName(u'MainLineCountLabel')
        self.mainSizeLayout.addWidget(self.mainLineCountLabel)
        self.mainAreaLayout.addRow(self.mainSizeLabel, self.mainSizeLayout)
        self.lineSpacingLabel = QtGui.QLabel(self.mainAreaPage)
        self.lineSpacingLabel.setObjectName(u'LineSpacingLabel')
        self.lineSpacingSpinBox = QtGui.QSpinBox(self.mainAreaPage)
        self.lineSpacingSpinBox.setMinimum(-50)
        self.lineSpacingSpinBox.setMaximum(50)
        self.lineSpacingSpinBox.setObjectName(u'LineSpacingSpinBox')
        self.mainAreaLayout.addRow(self.lineSpacingLabel,
            self.lineSpacingSpinBox)
        self.outlineCheckBox = QtGui.QCheckBox(self.mainAreaPage)
        self.outlineCheckBox.setObjectName(u'OutlineCheckBox')
        self.outlineLayout = QtGui.QHBoxLayout()
        self.outlineLayout.setObjectName(u'OutlineLayout')
        self.outlineColorButton = QtGui.QPushButton(self.mainAreaPage)
        self.outlineColorButton.setEnabled(False)
        self.outlineColorButton.setObjectName(u'OutlineColorButton')
        self.outlineLayout.addWidget(self.outlineColorButton)
        self.outlineLayout.addSpacing(20)
        self.outlineSizeLabel = QtGui.QLabel(self.mainAreaPage)
        self.outlineSizeLabel.setObjectName(u'OutlineSizeLabel')
        self.outlineLayout.addWidget(self.outlineSizeLabel)
        self.outlineSizeSpinBox = QtGui.QSpinBox(self.mainAreaPage)
        self.outlineSizeSpinBox.setEnabled(False)
        self.outlineSizeSpinBox.setObjectName(u'OutlineSizeSpinBox')
        self.outlineLayout.addWidget(self.outlineSizeSpinBox)
        self.mainAreaLayout.addRow(self.outlineCheckBox, self.outlineLayout)
        self.shadowCheckBox = QtGui.QCheckBox(self.mainAreaPage)
        self.shadowCheckBox.setObjectName(u'ShadowCheckBox')
        self.shadowLayout = QtGui.QHBoxLayout()
        self.shadowLayout.setObjectName(u'ShadowLayout')
        self.shadowColorButton = QtGui.QPushButton(self.mainAreaPage)
        self.shadowColorButton.setEnabled(False)
        self.shadowColorButton.setObjectName(u'shadowColorButton')
        self.shadowLayout.addWidget(self.shadowColorButton)
        self.shadowLayout.addSpacing(20)
        self.shadowSizeLabel = QtGui.QLabel(self.mainAreaPage)
        self.shadowSizeLabel.setObjectName(u'ShadowSizeLabel')
        self.shadowLayout.addWidget(self.shadowSizeLabel)
        self.shadowSizeSpinBox = QtGui.QSpinBox(self.mainAreaPage)
        self.shadowSizeSpinBox.setEnabled(False)
        self.shadowSizeSpinBox.setObjectName(u'ShadowSizeSpinBox')
        self.shadowLayout.addWidget(self.shadowSizeSpinBox)
        self.mainAreaLayout.addRow(self.shadowCheckBox, self.shadowLayout)
        themeWizard.addPage(self.mainAreaPage)
        # Footer Area Page
        self.footerAreaPage = QtGui.QWizardPage()
        self.footerAreaPage.setObjectName(u'FooterAreaPage')
        self.footerAreaLayout = QtGui.QFormLayout(self.footerAreaPage)
        self.footerAreaLayout.setObjectName(u'FooterAreaLayout')
        self.footerFontLabel = QtGui.QLabel(self.footerAreaPage)
        self.footerFontLabel.setObjectName(u'FooterFontLabel')
        self.footerFontComboBox = QtGui.QFontComboBox(self.footerAreaPage)
        self.footerFontComboBox.setObjectName(u'footerFontComboBox')
        self.footerAreaLayout.addRow(self.footerFontLabel,
            self.footerFontComboBox)
        self.footerColorLabel = QtGui.QLabel(self.footerAreaPage)
        self.footerColorLabel.setObjectName(u'FooterColorLabel')
        self.footerColorButton = QtGui.QPushButton(self.footerAreaPage)
        self.footerColorButton.setObjectName(u'footerColorButton')
        self.footerAreaLayout.addRow(self.footerColorLabel,
            self.footerColorButton)
        self.footerSizeLabel = QtGui.QLabel(self.footerAreaPage)
        self.footerSizeLabel.setObjectName(u'FooterSizeLabel')
        self.footerSizeSpinBox = QtGui.QSpinBox(self.footerAreaPage)
        self.footerSizeSpinBox.setMaximum(999)
        self.footerSizeSpinBox.setValue(10)
        self.footerSizeSpinBox.setObjectName(u'FooterSizeSpinBox')
        self.footerAreaLayout.addRow(self.footerSizeLabel,
            self.footerSizeSpinBox)
        self.footerAreaLayout.setItem(3, QtGui.QFormLayout.LabelRole,
            self.spacer)
        themeWizard.addPage(self.footerAreaPage)
        # Alignment Page
        self.alignmentPage = QtGui.QWizardPage()
        self.alignmentPage.setObjectName(u'AlignmentPage')
        self.alignmentLayout = QtGui.QFormLayout(self.alignmentPage)
        self.alignmentLayout.setObjectName(u'AlignmentLayout')
        self.horizontalLabel = QtGui.QLabel(self.alignmentPage)
        self.horizontalLabel.setObjectName(u'HorizontalLabel')
        self.horizontalComboBox = QtGui.QComboBox(self.alignmentPage)
        self.horizontalComboBox.addItems([u'', u'', u'', u''])
        self.horizontalComboBox.setObjectName(u'HorizontalComboBox')
        self.alignmentLayout.addRow(self.horizontalLabel,
            self.horizontalComboBox)
        create_valign_combo(themeWizard, self.alignmentPage,
            self.alignmentLayout)
        self.transitionsLabel = QtGui.QLabel(self.alignmentPage)
        self.transitionsLabel.setObjectName(u'TransitionsLabel')
        self.transitionsCheckBox = QtGui.QCheckBox(self.alignmentPage)
        self.transitionsCheckBox.setObjectName(u'TransitionsCheckBox')
        self.alignmentLayout.addRow(self.transitionsLabel,
            self.transitionsCheckBox)
        self.alignmentLayout.setItem(3, QtGui.QFormLayout.LabelRole,
            self.spacer)
        themeWizard.addPage(self.alignmentPage)
        # Area Position Page
        self.areaPositionPage = QtGui.QWizardPage()
        self.areaPositionPage.setObjectName(u'AreaPositionPage')
        self.areaPositionLayout = QtGui.QHBoxLayout(self.areaPositionPage)
        self.areaPositionLayout.setObjectName(u'AreaPositionLayout')
        self.mainPositionGroupBox = QtGui.QGroupBox(self.areaPositionPage)
        self.mainPositionGroupBox.setObjectName(u'MainPositionGroupBox')
        self.mainPositionLayout = QtGui.QFormLayout(self.mainPositionGroupBox)
        self.mainPositionLayout.setObjectName(u'MainPositionLayout')
        self.mainPositionCheckBox = QtGui.QCheckBox(self.mainPositionGroupBox)
        self.mainPositionCheckBox.setObjectName(u'MainPositionCheckBox')
        self.mainPositionLayout.addRow(self.mainPositionCheckBox)
        self.mainXLabel = QtGui.QLabel(self.mainPositionGroupBox)
        self.mainXLabel.setObjectName(u'MainXLabel')
        self.mainXSpinBox = QtGui.QSpinBox(self.mainPositionGroupBox)
        self.mainXSpinBox.setMaximum(9999)
        self.mainXSpinBox.setObjectName(u'MainXSpinBox')
        self.mainPositionLayout.addRow(self.mainXLabel, self.mainXSpinBox)
        self.mainYLabel = QtGui.QLabel(self.mainPositionGroupBox)
        self.mainYLabel.setObjectName(u'MainYLabel')
        self.mainYSpinBox = QtGui.QSpinBox(self.mainPositionGroupBox)
        self.mainYSpinBox.setMaximum(9999)
        self.mainYSpinBox.setObjectName(u'MainYSpinBox')
        self.mainPositionLayout.addRow(self.mainYLabel, self.mainYSpinBox)
        self.mainWidthLabel = QtGui.QLabel(self.mainPositionGroupBox)
        self.mainWidthLabel.setObjectName(u'MainWidthLabel')
        self.mainWidthSpinBox = QtGui.QSpinBox(self.mainPositionGroupBox)
        self.mainWidthSpinBox.setMaximum(9999)
        self.mainWidthSpinBox.setObjectName(u'MainWidthSpinBox')
        self.mainPositionLayout.addRow(self.mainWidthLabel,
            self.mainWidthSpinBox)
        self.mainHeightLabel = QtGui.QLabel(self.mainPositionGroupBox)
        self.mainHeightLabel.setObjectName(u'MainHeightLabel')
        self.mainHeightSpinBox = QtGui.QSpinBox(self.mainPositionGroupBox)
        self.mainHeightSpinBox.setMaximum(9999)
        self.mainHeightSpinBox.setObjectName(u'MainHeightSpinBox')
        self.mainPositionLayout.addRow(self.mainHeightLabel,
            self.mainHeightSpinBox)
        self.areaPositionLayout.addWidget(self.mainPositionGroupBox)
        self.footerPositionGroupBox = QtGui.QGroupBox(self.areaPositionPage)
        self.footerPositionGroupBox.setObjectName(u'FooterPositionGroupBox')
        self.footerPositionLayout = QtGui.QFormLayout(
            self.footerPositionGroupBox)
        self.footerPositionLayout.setObjectName(u'FooterPositionLayout')
        self.footerPositionCheckBox = QtGui.QCheckBox(
            self.footerPositionGroupBox)
        self.footerPositionCheckBox.setObjectName(u'FooterPositionCheckBox')
        self.footerPositionLayout.addRow(self.footerPositionCheckBox)
        self.footerXLabel = QtGui.QLabel(self.footerPositionGroupBox)
        self.footerXLabel.setObjectName(u'FooterXLabel')
        self.footerXSpinBox = QtGui.QSpinBox(self.footerPositionGroupBox)
        self.footerXSpinBox.setMaximum(9999)
        self.footerXSpinBox.setObjectName(u'FooterXSpinBox')
        self.footerPositionLayout.addRow(self.footerXLabel, self.footerXSpinBox)
        self.footerYLabel = QtGui.QLabel(self.footerPositionGroupBox)
        self.footerYLabel.setObjectName(u'FooterYLabel')
        self.footerYSpinBox = QtGui.QSpinBox(self.footerPositionGroupBox)
        self.footerYSpinBox.setMaximum(9999)
        self.footerYSpinBox.setObjectName(u'FooterYSpinBox')
        self.footerPositionLayout.addRow(self.footerYLabel, self.footerYSpinBox)
        self.footerWidthLabel = QtGui.QLabel(self.footerPositionGroupBox)
        self.footerWidthLabel.setObjectName(u'FooterWidthLabel')
        self.footerWidthSpinBox = QtGui.QSpinBox(self.footerPositionGroupBox)
        self.footerWidthSpinBox.setMaximum(9999)
        self.footerWidthSpinBox.setObjectName(u'FooterWidthSpinBox')
        self.footerPositionLayout.addRow(self.footerWidthLabel,
            self.footerWidthSpinBox)
        self.footerHeightLabel = QtGui.QLabel(self.footerPositionGroupBox)
        self.footerHeightLabel.setObjectName(u'FooterHeightLabel')
        self.footerHeightSpinBox = QtGui.QSpinBox(self.footerPositionGroupBox)
        self.footerHeightSpinBox.setMaximum(9999)
        self.footerHeightSpinBox.setObjectName(u'FooterHeightSpinBox')
        self.footerPositionLayout.addRow(self.footerHeightLabel,
            self.footerHeightSpinBox)
        self.areaPositionLayout.addWidget(self.footerPositionGroupBox)
        themeWizard.addPage(self.areaPositionPage)
        # Preview Page
        self.previewPage = QtGui.QWizardPage()
        self.previewPage.setObjectName(u'PreviewPage')
        self.previewLayout = QtGui.QVBoxLayout(self.previewPage)
        self.previewLayout.setObjectName(u'PreviewLayout')
        self.themeNameLayout = QtGui.QFormLayout()
        self.themeNameLayout.setObjectName(u'ThemeNameLayout')
        self.themeNameLabel = QtGui.QLabel(self.previewPage)
        self.themeNameLabel.setObjectName(u'ThemeNameLabel')
        self.themeNameEdit = QtGui.QLineEdit(self.previewPage)
        self.themeNameEdit.setValidator(QtGui.QRegExpValidator(
            QtCore.QRegExp(r'[^/\\?*|<>\[\]":<>+%]+'), self))
        self.themeNameEdit.setObjectName(u'ThemeNameEdit')
        self.themeNameLayout.addRow(self.themeNameLabel, self.themeNameEdit)
        self.previewLayout.addLayout(self.themeNameLayout)
        self.previewArea = QtGui.QWidget(self.previewPage)
        self.previewArea.setObjectName(u'PreviewArea')
        self.previewAreaLayout = QtGui.QGridLayout(self.previewArea)
        self.previewAreaLayout.setMargin(0)
        self.previewAreaLayout.setColumnStretch(0, 1)
        self.previewAreaLayout.setRowStretch(0, 1)
        self.previewAreaLayout.setObjectName(u'PreviewAreaLayout')
        self.previewBoxLabel = QtGui.QLabel(self.previewArea)
        self.previewBoxLabel.setFrameShape(QtGui.QFrame.Box)
        self.previewBoxLabel.setScaledContents(True)
        self.previewBoxLabel.setObjectName(u'PreviewBoxLabel')
        self.previewAreaLayout.addWidget(self.previewBoxLabel)
        self.previewLayout.addWidget(self.previewArea)
        themeWizard.addPage(self.previewPage)
        self.retranslateUi(themeWizard)
        QtCore.QObject.connect(self.backgroundComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'), self.backgroundStack,
            QtCore.SLOT(u'setCurrentIndex(int)'))
        QtCore.QObject.connect(self.outlineCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.outlineColorButton,
            QtCore.SLOT(u'setEnabled(bool)'))
        QtCore.QObject.connect(self.outlineCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.outlineSizeSpinBox,
            QtCore.SLOT(u'setEnabled(bool)'))
        QtCore.QObject.connect(self.shadowCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.shadowColorButton,
            QtCore.SLOT(u'setEnabled(bool)'))
        QtCore.QObject.connect(self.shadowCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.shadowSizeSpinBox,
            QtCore.SLOT(u'setEnabled(bool)'))
        QtCore.QObject.connect(self.mainPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.mainXSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.mainPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.mainYSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.mainPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.mainWidthSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.mainPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.mainHeightSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.footerPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.footerXSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.footerPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.footerYSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.footerPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.footerWidthSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QObject.connect(self.footerPositionCheckBox,
            QtCore.SIGNAL(u'toggled(bool)'), self.footerHeightSpinBox,
            QtCore.SLOT(u'setDisabled(bool)'))
        QtCore.QMetaObject.connectSlotsByName(themeWizard)

    def retranslateUi(self, themeWizard):
        themeWizard.setWindowTitle(
            translate('OpenLP.ThemeWizard', 'Theme Wizard'))
        self.titleLabel.setText(
            u'<span style="font-size:14pt; font-weight:600;">%s</span>' % \
            translate('OpenLP.ThemeWizard', 'Welcome to the Theme Wizard'))
        self.informationLabel.setText(
            translate('OpenLP.ThemeWizard', 'This wizard will help you to '
                'create and edit your themes. Click the next button below to '
                'start the process by setting up your background.'))
        self.backgroundPage.setTitle(
            translate('OpenLP.ThemeWizard', 'Set Up Background'))
        self.backgroundPage.setSubTitle(
            translate('OpenLP.ThemeWizard', 'Set up your theme\'s background '
                'according to the parameters below.'))
        self.backgroundLabel.setText(
            translate('OpenLP.ThemeWizard', 'Background type:'))
        self.backgroundComboBox.setItemText(BackgroundType.Solid,
            translate('OpenLP.ThemeWizard', 'Solid Color'))
        self.backgroundComboBox.setItemText(BackgroundType.Gradient,
            translate('OpenLP.ThemeWizard', 'Gradient'))
        self.backgroundComboBox.setItemText(
            BackgroundType.Image, UiStrings().Image)
        self.colorLabel.setText(translate('OpenLP.ThemeWizard', 'Color:'))
        self.gradientStartLabel.setText(
            translate(u'OpenLP.ThemeWizard', 'Starting color:'))
        self.gradientEndLabel.setText(
            translate(u'OpenLP.ThemeWizard', 'Ending color:'))
        self.gradientTypeLabel.setText(
            translate('OpenLP.ThemeWizard', 'Gradient:'))
        self.gradientComboBox.setItemText(BackgroundGradientType.Horizontal,
            translate('OpenLP.ThemeWizard', 'Horizontal'))
        self.gradientComboBox.setItemText(BackgroundGradientType.Vertical,
            translate('OpenLP.ThemeWizard', 'Vertical'))
        self.gradientComboBox.setItemText(BackgroundGradientType.Circular,
            translate('OpenLP.ThemeWizard', 'Circular'))
        self.gradientComboBox.setItemText(BackgroundGradientType.LeftTop,
            translate('OpenLP.ThemeWizard', 'Top Left - Bottom Right'))
        self.gradientComboBox.setItemText(BackgroundGradientType.LeftBottom,
            translate('OpenLP.ThemeWizard', 'Bottom Left - Top Right'))
        self.imageColorLabel.setText(
            translate(u'OpenLP.ThemeWizard', 'Background color:'))
        self.imageLabel.setText(u'%s:' % UiStrings().Image)
        self.mainAreaPage.setTitle(
            translate('OpenLP.ThemeWizard', 'Main Area Font Details'))
        self.mainAreaPage.setSubTitle(
            translate('OpenLP.ThemeWizard', 'Define the font and display '
                'characteristics for the Display text'))
        self.mainFontLabel.setText(translate('OpenLP.ThemeWizard', 'Font:'))
        self.mainColorLabel.setText(translate('OpenLP.ThemeWizard', 'Color:'))
        self.mainSizeLabel.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.mainSizeSpinBox.setSuffix(UiStrings().FontSizePtUnit)
        self.lineSpacingLabel.setText(
            translate('OpenLP.ThemeWizard', 'Line Spacing:'))
        self.lineSpacingSpinBox.setSuffix(UiStrings().FontSizePtUnit)
        self.outlineCheckBox.setText(
            translate('OpenLP.ThemeWizard', '&Outline:'))
        self.outlineSizeLabel.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.outlineSizeSpinBox.setSuffix(UiStrings().FontSizePtUnit)
        self.shadowCheckBox.setText(translate('OpenLP.ThemeWizard', '&Shadow:'))
        self.shadowSizeLabel.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.shadowSizeSpinBox.setSuffix(UiStrings().FontSizePtUnit)
        self.mainBoldCheckBox.setText(translate('OpenLP.ThemeWizard', 'Bold'))
        self.mainItalicsCheckBox.setText(
            translate('OpenLP.ThemeWizard', 'Italic'))
        self.footerAreaPage.setTitle(
            translate('OpenLP.ThemeWizard', 'Footer Area Font Details'))
        self.footerAreaPage.setSubTitle(
            translate('OpenLP.ThemeWizard', 'Define the font and display '
                'characteristics for the Footer text'))
        self.footerFontLabel.setText(translate('OpenLP.ThemeWizard', 'Font:'))
        self.footerColorLabel.setText(translate('OpenLP.ThemeWizard', 'Color:'))
        self.footerSizeLabel.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.footerSizeSpinBox.setSuffix(UiStrings().FontSizePtUnit)
        self.alignmentPage.setTitle(
            translate('OpenLP.ThemeWizard', 'Text Formatting Details'))
        self.alignmentPage.setSubTitle(
            translate('OpenLP.ThemeWizard', 'Allows additional display '
                'formatting information to be defined'))
        self.horizontalLabel.setText(
            translate('OpenLP.ThemeWizard', 'Horizontal Align:'))
        self.horizontalComboBox.setItemText(HorizontalType.Left,
            translate('OpenLP.ThemeWizard', 'Left'))
        self.horizontalComboBox.setItemText(HorizontalType.Right,
            translate('OpenLP.ThemeWizard', 'Right'))
        self.horizontalComboBox.setItemText(HorizontalType.Center,
            translate('OpenLP.ThemeWizard', 'Center'))
        self.horizontalComboBox.setItemText(HorizontalType.Justify,
            translate('OpenLP.ThemeWizard', 'Justify'))
        self.transitionsLabel.setText(
            translate('OpenLP.ThemeWizard', 'Transitions:'))
        self.areaPositionPage.setTitle(
            translate('OpenLP.ThemeWizard', 'Output Area Locations'))
        self.areaPositionPage.setSubTitle(
            translate('OpenLP.ThemeWizard', 'Allows you to change and move the'
                ' main and footer areas.'))
        self.mainPositionGroupBox.setTitle(
            translate('OpenLP.ThemeWizard', '&Main Area'))
        self.mainPositionCheckBox.setText(
            translate('OpenLP.ThemeWizard', '&Use default location'))
        self.mainXLabel.setText(translate('OpenLP.ThemeWizard', 'X position:'))
        self.mainXSpinBox.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.mainYSpinBox.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.mainYLabel.setText(translate('OpenLP.ThemeWizard', 'Y position:'))
        self.mainWidthSpinBox.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.mainWidthLabel.setText(translate('OpenLP.ThemeWizard', 'Width:'))
        self.mainHeightSpinBox.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.mainHeightLabel.setText(
            translate('OpenLP.ThemeWizard', 'Height:'))
        self.footerPositionGroupBox.setTitle(
            translate('OpenLP.ThemeWizard', '&Footer Area'))
        self.footerXLabel.setText(
            translate('OpenLP.ThemeWizard', 'X position:'))
        self.footerXSpinBox.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.footerYLabel.setText(
            translate('OpenLP.ThemeWizard', 'Y position:'))
        self.footerYSpinBox.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.footerWidthLabel.setText(
            translate('OpenLP.ThemeWizard', 'Width:'))
        self.footerWidthSpinBox.setSuffix(
            translate('OpenLP.ThemeWizard', 'px'))
        self.footerHeightLabel.setText(
            translate('OpenLP.ThemeWizard', 'Height:'))
        self.footerHeightSpinBox.setSuffix(
            translate('OpenLP.ThemeWizard', 'px'))
        self.footerPositionCheckBox.setText(
            translate('OpenLP.ThemeWizard', 'Use default location'))
        themeWizard.setOption(QtGui.QWizard.HaveCustomButton1, False)
        themeWizard.setButtonText(QtGui.QWizard.CustomButton1,
            translate('OpenLP.ThemeWizard', 'Preview'))
        self.previewPage.setTitle(
            translate('OpenLP.ThemeWizard', 'Save and Preview'))
        self.previewPage.setSubTitle(
            translate('OpenLP.ThemeWizard', 'View the theme and save it '
                'replacing the current one or change the name to create a '
                'new theme'))
        self.themeNameLabel.setText(
            translate('OpenLP.ThemeWizard', 'Theme name:'))
        # Align all QFormLayouts towards each other.
        labelWidth = max(self.backgroundLabel.minimumSizeHint().width(),
            self.horizontalLabel.minimumSizeHint().width())
        self.spacer.changeSize(labelWidth, 0,
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
