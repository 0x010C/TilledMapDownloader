# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(400, 110)
        PreferencesDialog.setMinimumSize(QtCore.QSize(400, 110))
        #PreferencesDialog.setMaximumSize(QtCore.QSize(400, 110))
        PreferencesDialog.setModal(True)
        self.formLayout = QtWidgets.QFormLayout(PreferencesDialog)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(PreferencesDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.threadsInput = QtWidgets.QSpinBox(PreferencesDialog)
        self.threadsInput.setMinimum(1)
        self.threadsInput.setMaximum(120)
        self.threadsInput.setProperty("value", 12)
        self.threadsInput.setObjectName("threadsInput")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.threadsInput)
        self.label_2 = QtWidgets.QLabel(PreferencesDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.keepTilesInput = QtWidgets.QRadioButton(PreferencesDialog)
        self.keepTilesInput.setObjectName("keepTilesInput")
        self.horizontalLayout.addWidget(self.keepTilesInput)
        self.dontKeepTilesInput = QtWidgets.QRadioButton(PreferencesDialog)
        self.dontKeepTilesInput.setObjectName("dontKeepTilesInput")
        self.dontKeepTilesInput.setChecked(True)
        self.horizontalLayout.addWidget(self.dontKeepTilesInput)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)

        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        _translate = QtCore.QCoreApplication.translate
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Préférences"))
        self.label.setText(_translate("PreferencesDialog", "Nombre de threads"))
        self.label_2.setText(_translate("PreferencesDialog", "Conserver les tiuiles intermédiaires "))
        self.keepTilesInput.setText(_translate("PreferencesDialog", "Oui"))
        self.dontKeepTilesInput.setText(_translate("PreferencesDialog", "Non"))

