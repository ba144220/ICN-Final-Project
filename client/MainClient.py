from os import sep
import sys
from PyQt5.QtWidgets import QApplication
from RtpPacket import RtpPacket
from Bcolors import Bcolors

#from client import Client
from ClientWindow import ClientWindow

file_list = ['blackpink_160_90', 'test_45_80', 'test_90_160', 'test_180_320', 'test_360_640' ,'chorus_160_90','chorus_320_180']

if __name__ == "__main__":
    serverHost = input(Bcolors.WARNING + "請輸入Server的IP Address: " + Bcolors.ENDC)
    serverPort = input(Bcolors.WARNING + "請輸入Server port: "+ Bcolors.ENDC)

    app = QApplication(sys.argv)
    #client = Client()
    client = ClientWindow(serverHost, serverPort)
    client.resize(800,600)
    client.show()
    sys.exit(app.exec_())
