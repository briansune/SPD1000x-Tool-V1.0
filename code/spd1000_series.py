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

