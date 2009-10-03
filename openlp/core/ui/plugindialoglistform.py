# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugindialoglistform.ui'
#
# Created: Thu Aug 13 05:52:06 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

import logging
from PyQt4 import QtCore, QtGui
from openlp.core.lib import translate, PluginStatus, buildIcon

class PluginCombo(QtGui.QComboBox):
    """
    Customised version of QTableWidget which can respond to keyboard
    events.
    """
    def __init__(self, parent=None, plugin=None):
        QtGui.QComboBox.__init__(self, parent)
        self.parent = parent
        self.plugin = plugin

    def enterEvent(self, event):
        self.parent.activePlugin = self.plugin
        event.ignore()

class PluginForm(QtGui.QDialog):
    global log
    log = logging.getLogger(u'PluginForm')

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.activePlugin = None
        self.setupUi(self)
        log.debug(u'Defined')

    def setupUi(self, PluginForm):
        PluginForm.setObjectName(u'PluginForm')
        PluginForm.resize(400, 568)
        icon = buildIcon(u':/icon/openlp-logo-16x16.png')
        PluginForm.setWindowIcon(icon)
        self.PluginViewList = QtGui.QTableWidget(PluginForm)
        self.PluginViewList.setGeometry(QtCore.QRect(20, 10, 371, 261))
        self.PluginViewList.setObjectName(u'PluginViewList')
        self.PluginViewList.setShowGrid(False)
        self.PluginViewList.setGridStyle(QtCore.Qt.SolidLine)
        self.PluginViewList.setSortingEnabled(False)
        self.PluginViewList.setColumnCount(3)
        item = QtGui.QTableWidgetItem()
        self.PluginViewList.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.PluginViewList.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.PluginViewList.setHorizontalHeaderItem(2, item)
        self.PluginViewList.horizontalHeader().setVisible(True)
        self.PluginViewList.horizontalHeader().setStretchLastSection(True)
        self.PluginViewList.verticalHeader().setVisible(False)
        self.ButtonBox = QtGui.QDialogButtonBox(PluginForm)
        self.ButtonBox.setGeometry(QtCore.QRect(220, 530, 170, 25))
        self.ButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.ButtonBox.setObjectName(u'ButtonBox')
        self.PluginInfoGroupBox = QtGui.QGroupBox(PluginForm)
        self.PluginInfoGroupBox.setGeometry(QtCore.QRect(20, 270, 371, 241))
        self.PluginInfoGroupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.PluginInfoGroupBox.setFlat(False)
        self.PluginInfoGroupBox.setObjectName("PluginInfoGroupBox")
        self.AboutTextLabel = QtGui.QLabel(self.PluginInfoGroupBox)
        self.AboutTextLabel.setGeometry(QtCore.QRect(10, 30, 351, 191))
        self.AboutTextLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.AboutTextLabel.setWordWrap(True)
        self.AboutTextLabel.setObjectName("AboutTextLabel")

        self.retranslateUi(PluginForm)
        QtCore.QObject.connect(self.ButtonBox,
            QtCore.SIGNAL(u'accepted()'), PluginForm.close)
        QtCore.QMetaObject.connectSlotsByName(PluginForm)
        QtCore.QObject.connect(self.PluginViewList,
           QtCore.SIGNAL(u'itemClicked(QTableWidgetItem*)'), self.displayAbout)

    def retranslateUi(self, PluginForm):
        PluginForm.setWindowTitle(translate(u'PluginForm', u'Plugin list'))
        self.PluginInfoGroupBox.setTitle(translate("PluginForm", "Selected Plugin Information"))
        self.PluginViewList.horizontalHeaderItem(0).setText(
            translate(u'PluginForm', u'Name'))
        self.PluginViewList.horizontalHeaderItem(1).setText(
            translate(u'PluginForm', u'Version'))
        self.PluginViewList.horizontalHeaderItem(2).setText(
            translate(u'PluginForm', u'Status'))

    def load(self):
        """
        Load the plugin details into the screen
        """
        self.PluginViewList.setRowCount(0)
        for plugin in self.parent.plugin_manager.plugins:
            row = self.PluginViewList.rowCount()
            self.PluginViewList.setRowCount(row + 1)
            item1 = QtGui.QTableWidgetItem(plugin.name)
            item1.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item1.setTextAlignment(QtCore.Qt.AlignVCenter)
            item2 = QtGui.QTableWidgetItem(plugin.version)
            item2.setTextAlignment(QtCore.Qt.AlignVCenter)
            item2.setFlags(QtCore.Qt.ItemIsSelectable)
            self.PluginViewList.setItem(row, 0, item1)
            self.PluginViewList.setItem(row, 1, item2)
            if plugin.can_be_disabled():
                combo = PluginCombo(self, plugin)
                self.PluginViewList.setCellWidget(row, 2, combo)
                combo.addItem(translate(u'PluginForm', u'Active'))
                combo.addItem(translate(u'PluginForm', u'Inactive'))
                combo.setCurrentIndex(int(plugin.status))
                QtCore.QObject.connect(combo,
                    QtCore.SIGNAL(u'currentIndexChanged(int)'), self.statusComboChanged)
                self.PluginViewList.setRowHeight(row, 25)
            else:
                item3 = QtGui.QTableWidgetItem(
                    translate(u'PluginForm', u'Active'))
                item3.setTextAlignment(QtCore.Qt.AlignVCenter)
                item3.setFlags(QtCore.Qt.ItemIsSelectable)
                self.PluginViewList.setItem(row, 2, item3)
                self.PluginViewList.setRowHeight(row, 15)

    def displayAbout(self, item):
        if item is None:
            return False
        row = self.PluginViewList.row(item)
        text = self.parent.plugin_manager.plugins[row].about()
        if text is not None:
            self.AboutTextLabel.setText(translate(u'PluginList', text))

    def statusComboChanged(self, status):
        log.debug(u'Combo status changed %s for plugin %s' %(status, self.activePlugin.name))
        self.activePlugin.toggle_status(status)
        if status == PluginStatus.Active:
            self.activePlugin.initialise()
        else:
            self.activePlugin.finalise()
