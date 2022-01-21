import socket
import sys
import threading

sys.path.insert(1, '/Users/yuchihsu/Desktop/NTU/110-1/電腦網路導論/final project/ICN-Final-Project/utils')

from Bcolors import Bcolors
from Server import Server

FILE_LIST = [
    'blackpink_640x360', 
    'blackpink_1280x720', 
    'chorus_320x180', 
    'chorus_640x360',
    'goodbye_sengen_1280x720',
    'piano_master_534x360',
    'sponge_bob_1068x720'

    ]

if __name__ == "__main__":
    server = Server(fileList=FILE_LIST)