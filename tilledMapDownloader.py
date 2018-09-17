#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar, and a central widget.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""
import sys
import os
from mainWindow import Ui_MainWindow
from preferences import Ui_PreferencesDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from worker import Worker


#Custom slots
def openHelp(self):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/0x010C/TilledMapDownloader"))
Ui_MainWindow.openHelp = openHelp

def updateStatus(self, progress, message):
    self.statusBar.setProperty("value", progress*100)
    self.statusMessage.setText(message)
Ui_MainWindow.updateStatus = updateStatus


def startProcess(self):
    if self.urlInput.text() != "":
        filename = QtWidgets.QFileDialog.getSaveFileName(None, "TilledMapDownloader", "", "Images (*.png *.jpg *.jpeg)", "", QtWidgets.QFileDialog.DontUseNativeDialog)
        if filename[0]:
            self.startButton.setDisabled(True)
            if uiPreferences.keepTilesInput.isChecked():
                directory = "/".join(filename[0].split("/")[:-1])
                if not os.path.exists(directory):
                    os.makedirs(directory)
                directory += "/tiles"
                if not os.path.exists(directory):
                    os.makedirs(directory)
            else:
                directory = QtCore.QTemporaryDir().path()
            work = Worker(self.xMinInput.value(), self.xMaxInput.value(), self.yMinInput.value(), self.yMaxInput.value(), self.urlInput.text(), directory, filename[0], self.updateStatus, uiPreferences.threadsInput.value()) #TODO nb_threads
            self.startButton.setEnabled(True)


Ui_MainWindow.startProcess = startProcess


if __name__ == "__main__":
    global uiPreferences
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Breeze'))

    #Setup the main window
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    #Setup the preferences dialog
    PreferencesDialog = QtWidgets.QDialog()
    uiPreferences = Ui_PreferencesDialog()
    uiPreferences.setupUi(PreferencesDialog)

    #Connect some extra signals
    ui.startButton.clicked.connect(ui.startProcess)
    ui.actionPref.triggered.connect(PreferencesDialog.show)
    ui.actionHelp.triggered.connect(ui.openHelp)

    MainWindow.show()
    sys.exit(app.exec_())
