import socket
import sys
import time


# import pyvisa as visa


# 0 | 0: CV mode            1: CC mode
# 4 | 0: Output OFF         1: Output ON
# 5 | 0: 2W mode            1: 4W mode
# 6 | 0: TIMER OFF          1: TIMER ON
# 8 | 0: digital display    1: waveform di s play


class SPD1000:

    def __init__(self):
        self.spd_ip = ''
        self.spd_port = 5025
        self.spd_socket = socket.socket()
        self.spd_mode = False
        self.spd_output = False
        self.spd_wires = False
        self.spd_timer = False
        self.spd_disp = False
        self.spd_lock = False
        self.spd_mea_volt = 0.0
        self.spd_mea_curr = 0.0

    def spdConnect(self):
        try:
            self.spd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print ('Failed to create socket.')
            return

        try:
            self.spd_socket.connect((self.spd_ip, self.spd_port))
        except socket.error:
            print ('failed to connect to ip ' + self.spd_ip)
            return

    def spdSetup(self, cmd):
        try:
            self.spd_socket.sendall(cmd + b'\n')
            time.sleep(0.1)
        except socket.error:
            print ('Send failed')
            sys.exit()

    def spdQuery(self, cmd):
        try:
            self.spd_socket.sendall(cmd + b'\n')
            time.sleep(0.1)
        except socket.error:
            print ('Send failed')
            sys.exit()
        while True:
            reply = self.spd_socket.recv(4096)
            if reply:
                return reply.strip()

    def spdClose(self):
        self.spd_socket.close()

    def spdGetStage(self):
        s_res = int(self.spdQuery(b'SYST:STAT?'), 16)
        self.spd_mode = True if (s_res & 0x001) else False
        self.spd_output = True if (s_res & 0x010) else False
        self.spd_wires = True if (s_res & 0x020) else False
        self.spd_timer = True if (s_res & 0x040) else False
        self.spd_disp = True if (s_res & 0x100) else False
        s_res = self.spdQuery(b'*LOCK?').lower()
        self.spd_lock = True if 'lock' == s_res else False
        s_res = float(self.spdQuery(b'MEAS:VOLT?'))
        self.spd_mea_volt = s_res
        s_res = float(self.spdQuery(b'MEAS:CURR?'))
        self.spd_mea_curr = s_res
