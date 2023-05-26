#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
from mainWindow import Ui_MainWindow
from preferences import Ui_PreferencesDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from worker import TilesGenerator, TilesDownloader, TilesMerger


#Custom slots
def openHelp(self):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/0x010C/TilledMapDownloader"))
Ui_MainWindow.openHelp = openHelp


def updateStatus(self, progress, message):
    self.statusBar.setProperty("value", progress*100)
    self.statusMessage.setText(message)
    if progress == 0.8:
        self.setupMergeStep()
    elif progress == 1:
        self.setupFinishedStep()
Ui_MainWindow.updateStatus = updateStatus

def startProcess(self):
    if self.urlInput.text() != "":
        filename = QtWidgets.QFileDialog.getSaveFileName(None, "TilledMapDownloader", "", "Images (*.png *.jpg *.jpeg)", "")
        if filename[0]:
            self.startButton.setDisabled(True)
            self.filename = os.path.normpath(filename[0])
            if not self.filename.endswith(('.png', '.jpg', '.jpeg')):
                self.filename += '.png'
            if uiPreferences.keepTilesInput.isChecked():
                self.directory = os.path.join(os.path.split(self.filename)[0], "tiles")
                if not os.path.exists(self.directory):
                    os.makedirs(self.directory)
            else:
                self.directory = QtCore.QTemporaryDir().path()
            self.setupDownloadStep()
Ui_MainWindow.startProcess = startProcess

def setupDownloadStep(self):
    self.min_x = self.xMinInput.value()
    self.max_x = self.xMaxInput.value()
    self.min_y = self.yMinInput.value()
    self.max_y = self.yMaxInput.value()
    base_url = self.urlInput.text()
    nb_threads = uiPreferences.threadsInput.value()

    tiles_generator = TilesGenerator(self.min_x, self.max_x, self.min_y, self.max_y, self.directory)

    i = 0
    for y in range(self.min_y, self.max_y+1):
        directory_y = os.path.join(self.directory, str(y))
        if not os.path.exists(directory_y):
            os.makedirs(directory_y)

    self.threads = []
    for i in range(0, nb_threads):
        thread = TilesDownloader(tiles_generator, base_url, self.directory)
        thread.progress.connect(self.updateStatus)
        thread.start()
        self.threads.append(thread)
Ui_MainWindow.setupDownloadStep = setupDownloadStep

def setupMergeStep(self):
    self.merger = TilesMerger(self.min_x, self.max_x, self.min_y, self.max_y, self.directory, self.filename)
    self.merger.progress.connect(self.updateStatus)
    self.merger.start()
Ui_MainWindow.setupMergeStep = setupMergeStep

def setupFinishedStep(self):
    self.startButton.setDisabled(False)
Ui_MainWindow.setupFinishedStep = setupFinishedStep


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
