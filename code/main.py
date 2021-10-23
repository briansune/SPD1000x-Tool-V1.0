# -*- coding: utf-8 -*-

import sys
import pyvisa as visa
import spd1000_series as _spd
import re
import threading
import time

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt5 import QtGui
from spd1000x_gui import Ui_oMainWind


class Window(QMainWindow, Ui_oMainWind):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.sys_ports = []
        self.ui = Ui_oMainWind()
        self.ui.setupUi(self)
        self.lVoltMax = [3, 9, 9, 9]
        self.lCurrMax = [5, 9, 9]

        self.lVoltSel = [1, 0, 0, 0]
        self.lVoltVar = [0, 0, 0, 0]
        self.lCurrSel = [1, 0, 0]
        self.lCurrVar = [0, 0, 0]

        self.o_visa = None
        self.o_socket = None

        self.bConFlag = False

        self.oWatchDog = threading.Thread()
        self.bWdgFlag = False

        self.ui.oLcdVoltageMea.display('OL.  ')
        self.ui.oLcdCurrentMea.display('OL.  ')
        self.ui.oLcdVoltIn0.setEnabled(self.lVoltSel[0])
        self.ui.oLcdVoltIn1.setEnabled(self.lVoltSel[1])
        self.ui.oLcdVoltIn2.setEnabled(self.lVoltSel[2])
        self.ui.oLcdVoltIn3.setEnabled(self.lVoltSel[3])
        self.ui.oLcdCurrIn0.setEnabled(self.lCurrSel[0])
        self.ui.oLcdCurrIn1.setEnabled(self.lCurrSel[1])
        self.ui.oLcdCurrIn2.setEnabled(self.lCurrSel[2])
        self.ui.oButPwr.setEnabled(False)
        self.connectSignalsSlots()

    def refreshDevices(self):
        if self.ui.oRbutUsb.isChecked():
            self.o_visa = visa.ResourceManager()
            self.ui.oComboDev.clear()
            [self.ui.oComboDev.addItem(s_dev) for s_dev in self.o_visa.list_resources()]
            self.o_socket = None

        elif self.ui.oRbutEthernet.isChecked():
            self.ui.oComboDev.clear()
            self.o_visa = None
            self.ui.oComboDev.addItem('192.168.1.214')
            self.o_socket = _spd.SPD1000()

    def connectSignalsSlots(self):
        self.ui.oActAbout.triggered.connect(self.about)
        self.ui.oActExit.triggered.connect(self.close)
        self.ui.oButVoltSel.clicked.connect(self.setVoltInSel)
        self.ui.oButCurrSel.clicked.connect(self.setCurrInSel)
        self.ui.oDialVolt.sliderReleased.connect(self.setVoltInVar)
        self.ui.oDialCurr.sliderReleased.connect(self.setCurrInVar)
        self.ui.oRbutEthernet.clicked.connect(self.refreshDevices)
        self.ui.oRbutUsb.clicked.connect(self.refreshDevices)
        self.ui.oButConnect.clicked.connect(self.controlLinkUnlink)
        self.ui.oButPwr.clicked.connect(self.controlPowerOnOff)
        self.ui.oButLock.clicked.connect(self.controlLock)
        self.ui.oRbut2Wire.clicked.connect(self.control2Wire)
        self.ui.oRbut4Wire.clicked.connect(self.control4Wire)

    def updateOutput(self):
        if self.o_socket.spd_output:
            self.ui.oButPwr.setText('OFF')
            self.ui.oLabOnOff.setPixmap(QtGui.QPixmap(":/image/green.png"))
        else:
            self.ui.oButPwr.setText('ON')
            self.ui.oLabOnOff.setPixmap(QtGui.QPixmap(":/image/red.png"))

    def updateWireMode(self):
        if self.o_socket.spd_wires:
            self.ui.oRbut4Wire.setChecked(True)
            self.ui.oRbut2Wire.setChecked(False)
        else:
            self.ui.oRbut4Wire.setChecked(False)
            self.ui.oRbut2Wire.setChecked(True)

    def updateLock(self):
        if self.o_socket.spd_lock:
            self.ui.oLabLock.setPixmap(QtGui.QPixmap(":/image/lock.png"))
            self.ui.oButLock.setText('UNLOCK')
            self.ui.oButPwr.setEnabled(False)
        else:
            self.ui.oLabLock.setPixmap(QtGui.QPixmap(":/image/unlock.png"))
            self.ui.oButLock.setText('LOCK')
            self.ui.oButPwr.setEnabled(True)

    def updateMeas(self):
        self.ui.oLcdVoltageMea.display('{:05.2f}'.format(self.o_socket.spd_mea_volt))
        self.ui.oLcdCurrentMea.display('{:04.2f}'.format(self.o_socket.spd_mea_curr))

    def controlPowerOnOff(self):
        if not self.o_socket.spd_output:
            self.ui.oButPwr.setText('OFF')
            self.o_socket.spdSetup(b'OUTP CH1,ON')
        else:
            self.ui.oButPwr.setText('ON')
            self.o_socket.spdSetup(b'OUTP CH1,OFF')

    def controlLock(self):
        if not self.o_socket.spd_lock:
            self.ui.oButPwr.setEnabled(False)
            self.ui.oButLock.setText('UNLOCK')
            self.o_socket.spdSetup(b'*LOCK')
        else:
            self.ui.oButPwr.setEnabled(True)
            self.ui.oButLock.setText('LOCK')
            self.o_socket.spdSetup(b'*UNLOCK')

    def control2Wire(self):
        self.ui.oRbut4Wire.setChecked(False)
        self.ui.oRbut2Wire.setChecked(True)
        self.o_socket.spdSetup(b'MODE:SET 2W')

    def control4Wire(self):
        self.ui.oRbut4Wire.setChecked(True)
        self.ui.oRbut2Wire.setChecked(False)
        self.o_socket.spdSetup(b'MODE:SET 4W')

    def watchDogLoop(self):
        while self.bWdgFlag:
            self.o_socket.spdGetStage()
            self.updateOutput()
            self.updateWireMode()
            self.updateLock()
            self.updateMeas()
            time.sleep(0.01)

    def controlLinkUnlink(self):
        if not self.bConFlag:
            if self.o_visa:
                self.o_visa.open_resource(self.ui.oComboDev.currentText())
                self.o_visa.write('*IDN?')
                s_re = self.o_visa.read()
            elif self.o_socket:
                self.o_socket.spd_ip = self.ui.oComboDev.currentText()
                self.o_socket.spdConnect()
                s_re = self.o_socket.spdQuery(b'*IDN?')
                self.ui.oButPwr.setEnabled(True)
            else:
                s_re = ''

            o_re = re.search(r'Siglent[\W]+Technologies,([SPD13][\w]+)', s_re)
            if o_re:
                print(o_re.group(1))
                self.bConFlag = not self.bConFlag
                self.ui.oButConnect.setText('Disconnect')
                self.ui.oLabCon.setPixmap(QtGui.QPixmap(":/image/green.png"))
                self.oWatchDog = threading.Thread(target=self.watchDogLoop)
                self.bWdgFlag = True
                self.oWatchDog.start()

        else:
            self.bWdgFlag = False
            while self.oWatchDog.is_alive():
                continue

            self.ui.oButConnect.setText('Connect')
            if self.o_visa:
                self.o_visa.close()
            elif self.o_socket:
                self.o_socket.spdClose()

            self.bConFlag = not self.bConFlag
            self.ui.oLabCon.setPixmap(QtGui.QPixmap(":/image/red.png"))
            self.ui.oLabOnOff.setPixmap(QtGui.QPixmap(":/image/red.png"))
            self.ui.oLcdVoltageMea.display('OL.  ')
            self.ui.oLcdCurrentMea.display('OL.  ')
            self.ui.oButPwr.setEnabled(False)

    def setCurrInSel(self):
        self.lCurrSel.insert(0, self.lCurrSel.pop())
        self.ui.oLcdCurrIn0.setEnabled(self.lCurrSel[0])
        self.ui.oLcdCurrIn1.setEnabled(self.lCurrSel[1])
        self.ui.oLcdCurrIn2.setEnabled(self.lCurrSel[2])

    def setCurrInVar(self):
        for i_idx, b_flag in enumerate(self.lCurrSel):
            if b_flag:
                i_curr_set = self.ui.oDialCurr.value()
                self.lCurrVar[i_idx] = i_curr_set if i_curr_set <= self.lCurrMax[i_idx] else self.lCurrVar[i_idx]

                if self.lCurrVar[0] == self.lCurrMax[0]:
                    self.lCurrVar[1] = 0
                    self.lCurrVar[2] = 0

                break

        self.ui.oLcdCurrIn0.display(self.lCurrVar[0])
        self.ui.oLcdCurrIn1.display(self.lCurrVar[1])
        self.ui.oLcdCurrIn2.display(self.lCurrVar[2])
        self.o_socket.spdSetup(
            b'CH1:CURR {}.{}{}'.format(
                self.lCurrVar[0], self.lCurrVar[1], self.lCurrVar[2]))

    def setVoltInSel(self):
        self.lVoltSel.insert(0, self.lVoltSel.pop())
        self.ui.oLcdVoltIn0.setEnabled(self.lVoltSel[0])
        self.ui.oLcdVoltIn1.setEnabled(self.lVoltSel[1])
        self.ui.oLcdVoltIn2.setEnabled(self.lVoltSel[2])
        self.ui.oLcdVoltIn3.setEnabled(self.lVoltSel[3])

    def setVoltInVar(self):
        for i_idx, b_flag in enumerate(self.lVoltSel):
            if b_flag:
                i_volt_set = self.ui.oDialVolt.value()
                self.lVoltVar[i_idx] = i_volt_set if i_volt_set <= self.lVoltMax[i_idx] else self.lVoltVar[i_idx]

                if self.lVoltVar[0] == self.lVoltMax[0]:
                    self.lVoltVar[1] = 0
                    self.lVoltVar[2] = 0
                    self.lVoltVar[3] = 0

                break
        self.ui.oLcdVoltIn0.display(self.lVoltVar[0])
        self.ui.oLcdVoltIn1.display(self.lVoltVar[1])
        self.ui.oLcdVoltIn2.display(self.lVoltVar[2])
        self.ui.oLcdVoltIn3.display(self.lVoltVar[3])
        self.o_socket.spdSetup(
            b'CH1:VOLT {}{}.{}{}'.format(
                self.lVoltVar[0], self.lVoltVar[1],
                self.lVoltVar[2], self.lVoltVar[3]))

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
