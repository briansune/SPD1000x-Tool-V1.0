# -*- coding: utf-8 -*-

import sys

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt5 import QtGui
from spd1000x_gui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.sys_ports = []
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.lVoltMax = [3, 0, 0, 0]
        self.lCurrMax = [5, 0, 0]

        self.lVoltSel = [1, 0, 0, 0]
        self.lVoltVar = [0, 0, 0, 0]
        self.lCurrSel = [1, 0, 0]
        self.lCurrVar = [0, 0, 0]

        self.ui.oLcdVoltIn0.setEnabled(self.lVoltSel[0])
        self.ui.oLcdVoltIn1.setEnabled(self.lVoltSel[1])
        self.ui.oLcdVoltIn2.setEnabled(self.lVoltSel[2])
        self.ui.oLcdVoltIn3.setEnabled(self.lVoltSel[3])
        self.ui.oLcdCurrIn0.setEnabled(self.lCurrSel[0])
        self.ui.oLcdCurrIn1.setEnabled(self.lCurrSel[1])
        self.ui.oLcdCurrIn2.setEnabled(self.lCurrSel[2])

        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.ui.oActAbout.triggered.connect(self.about)
        self.ui.oActExit.triggered.connect(self.close)
        self.ui.oButVoltSel.clicked.connect(self.setVoltInSel)
        self.ui.oButCurrSel.clicked.connect(self.setCurrInSel)
        self.ui.oDialVolt.sliderReleased.connect(self.setVoltInVar)
        self.ui.oDialCurr.sliderReleased.connect(self.setCurrInVar)

    def setCurrInSel(self):
        self.lCurrSel.insert(0, self.lCurrSel.pop())
        self.ui.oLcdCurrIn0.setEnabled(self.lCurrSel[0])
        self.ui.oLcdCurrIn1.setEnabled(self.lCurrSel[1])
        self.ui.oLcdCurrIn2.setEnabled(self.lCurrSel[2])

    def setCurrInVar(self):
        for i_idx, b_flag in enumerate(self.lCurrSel):
            if b_flag:
                self.lCurrVar[i_idx] = self.ui.oDialCurr.value()
                break
        self.ui.oLcdCurrIn0.display(self.lCurrVar[0])
        self.ui.oLcdCurrIn1.display(self.lCurrVar[1])
        self.ui.oLcdCurrIn2.display(self.lCurrVar[2])

    def setVoltInSel(self):
        self.lVoltSel.insert(0, self.lVoltSel.pop())
        self.ui.oLcdVoltIn0.setEnabled(self.lVoltSel[0])
        self.ui.oLcdVoltIn1.setEnabled(self.lVoltSel[1])
        self.ui.oLcdVoltIn2.setEnabled(self.lVoltSel[2])
        self.ui.oLcdVoltIn3.setEnabled(self.lVoltSel[3])

    def setVoltInVar(self):
        for i_idx, b_flag in enumerate(self.lVoltSel):
            if b_flag:
                self.lVoltVar[i_idx] = self.ui.oDialVolt.value()
                break
        self.ui.oLcdVoltIn0.display(self.lVoltVar[0])
        self.ui.oLcdVoltIn1.display(self.lVoltVar[1])
        self.ui.oLcdVoltIn2.display(self.lVoltVar[2])
        self.ui.oLcdVoltIn3.display(self.lVoltVar[3])

    @staticmethod
    def about():
        o_msg_box = QMessageBox()
        o_msg_box.setWindowTitle("SPD1305X Power Supply")
        o_msg_box.setText("<p>Designer: Brfo</p>"
                          "<p>Contact: briansune@gmail.com</p>"
                          "<p>Date: 2021</p>")
        o_msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
