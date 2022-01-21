
import sys
import threading
import socket
import traceback
import numpy as np
import cv2

import pygame
from pygame.locals import *

from Bcolors import Bcolors
from RtpPacket import RtpPacket
from Rtsp import Rtsp
import random


class Client:

    def __init__(self, rtspServerHost, rtspServerPort):
        self.rtspConnected = False
        self.rtpConnected = False
        self.rtspServerHost = rtspServerHost
        self.rtspServerPort = int(rtspServerPort)
        
        self.rtpPort = random.randint(5000,60000)
        
        self.rtpThread = threading.Thread(target=self.receive_rtp_packet)
        self.rtpThread.start()

        self.fileList = []

        # pygame init
        pygame.mixer.pre_init(44100, -16, 2)
        pygame.init()

        

    def run(self):
        while True:
            
            undecodedData = self.rtspSocket.recv(256)
            print(Bcolors.WARNING+ 'Server Reply: ' + undecodedData.decode() + Bcolors.ENDC)
            data = undecodedData.decode()
            
            try:
                if data.split('\n')[3].split(' ')[1]:
                    self.fileList = data.split('\n')[3].split(' ')[1].split(',')
            except:
                pass



        # connect to rtsp server
        #self.connect_rtsp_server()

    def connect_rtsp_server(self):
        try:
            self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rtspSocket.connect((self.rtspServerHost, self.rtspServerPort))
        except:
            traceback.print_exc(file=sys.stdout)
            print(Bcolors.FAIL + '[client] Connection failed' + Bcolors.ENDC)
            return
        self.rtspConnected = True
        print(Bcolors.OKGREEN +'[client] Successfully connect to RTSP server' + Bcolors.ENDC)

        self.runThread = threading.Thread(target=self.run)
        self.runThread.daemon = True
        self.runThread.start()

        #self.get_file_list()


        # newThread = threading.Thread(target = self.send_rtsp_request)
        # newThread.start()

    # def send_rtsp_request(self):
    #     if not self.rtspConnected:
    #         return
    #     while True:
    #         cmd = input(Bcolors.BOLD+Bcolors.OKCYAN+"Enter Command: "+Bcolors.ENDC)
    #         outdata = cmd.encode()
    #         if cmd == 'quit':
    #             self.rtspSocket.close()
    #             self.rtspConnected = False
    #             return
    #         elif cmd == 'setup':
    #             rtsp = Rtsp()
    #             outdata = rtsp.setup(self.fileName, 0, self.rtpPort)
                
    #         elif cmd == 'play':
    #             rtsp = Rtsp()
    #             outdata = rtsp.play(self.fileName, 0, 0)
          
    #         elif cmd == 'pause':
    #             rtsp = Rtsp()
    #             outdata = rtsp.pause(self.fileName,0,0)
    #         elif cmd == 'teardown':
    #             rtsp = Rtsp()
    #             outdata = rtsp.teardown(self.fileName,0,0)
                
    #         self.rtspSocket.send(outdata)

    def setup(self, fileName):
        if not self.rtspConnected:
            return
        rtsp = Rtsp()
        outdata = rtsp.setup(fileName, 0, self.rtpPort)

        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rtpSocket.bind(('', self.rtpPort))
        self.rtpConnected = True

        self.rtspSocket.send(outdata)
    
    def play(self, fileName):
        if not self.rtspConnected:
            return
        rtsp = Rtsp()
        outdata = rtsp.play(fileName, 0, 0)     
        self.rtspSocket.send(outdata)   
    def pause(self, fileName):
        if not self.rtspConnected:
            return
        rtsp = Rtsp()
        outdata = rtsp.pause(fileName,0,0)    
        self.rtspSocket.send(outdata)     

    def teardown(self, fileName):
        if not self.rtspConnected:
            return
        rtsp = Rtsp()
        outdata = rtsp.teardown(fileName,0,0)    
        self.rtspSocket.send(outdata)  
        self.rtpConnected = False

    def shutdown(self):
        if self.rtspConnected:
            self.rtspSocket.close()
            self.rtspConnected = False
        return          

    def get_file_list(self):
        self.rtspSocket.send('ASKFILENAME RTSP/1.0\nCseq: 0'.encode())
        while True:
            
            undecodedData = self.rtspSocket.recv(256)
            print(Bcolors.WARNING+ 'Server Reply: ' + undecodedData.decode() + Bcolors.ENDC)
            data = undecodedData.decode()
            
            try:
                if data.split('\n')[3].split(' ')[1]:
                    self.fileList = data.split('\n')[3].split(' ')[1].split(',')
                return self.fileList
            except:
                pass


    def receive_rtp_packet(self):
        if not self.rtpConnected:
            return None
        print(Bcolors.OKGREEN + 'Receiving RTP packets' + Bcolors.ENDC)

        self.audioBuf = bytearray()
        self.videoBuf = bytearray()

        while True:
            indata, addr = self.rtpSocket.recvfrom(65536)
            #print(Bcolors.WARNING + 'Received Something' + Bcolors.ENDC)
            rtpPacket = RtpPacket()
            rtpPacket.decode(indata)

            if rtpPacket.getSequenceNumber() < 5:
                print(Bcolors.WARNING+'[client] Last frame' + Bcolors.ENDC)
                self.rtpSocket.close()
                self.rtpConnected = False
                return -1
            
            if rtpPacket.getPayloadType()==0:
                if rtpPacket.getMarker()==1:
                    self.videoBuf = self.videoBuf + rtpPacket.getPayload()
                    frame = self.decode_jpeg(self.videoBuf)
                    self.videoBuf = bytearray()
                    return frame, "IMAGE"
                else:
                    self.videoBuf = self.videoBuf + rtpPacket.getPayload()

            elif rtpPacket.getPayloadType()==10:
                if rtpPacket.getMarker()==1:
                    # play the audio
                    self.audioBuf = self.audioBuf + rtpPacket.getPayload()
                    return self.audioBuf, "AUDIO"
                else:
                    self.audioBuf = self.audioBuf + rtpPacket.getPayload()





    def decode_jpeg(self, data):
        data = np.frombuffer(data, dtype=np.uint8)
        try:
            image = cv2.cvtColor(cv2.imdecode(data, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
            return image
        except:
            pass
        
        
