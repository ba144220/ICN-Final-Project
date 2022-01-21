
import sys
import socket
import threading
import time
import traceback

import numpy as np
import cv2
import pydub 
import pygame
from pygame.locals import *

from VideoStream import VideoStream
from Bcolors import Bcolors
from Rtsp import Rtsp
from RtpPacket import RtpPacket

class ClientProcess:
    SETUP = 'SETUP'
    PLAY = 'PLAY'
    PAUSE = 'PAUSE'
    TEARDOWN = 'TEARDOWN'
    ASKFILENAME = 'ASKFILENAME'

    # states
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    # status codes
    BAD_REQUEST = 400
    OK = 200
    FILE_NOT_FOUND = 404
    CONNECTION_ERROR = 500
    NOT_IMPLEMENTED = 501


    def __init__(self, clientRtspSocket, clientAddr, rtpPort, fileList):
        self.clientRtspSocket = clientRtspSocket
        self.clientAddr = clientAddr
        self.rtpPort = rtpPort
        self.sendRtpEvent = None
        self.fileList = fileList


    def run(self):
        self.recv_rtsp_req()

    def recv_rtsp_req(self):
        while True:
            try:
                undecodedData = self.clientRtspSocket.recv(256)
            except:
                print(Bcolors.FAIL + '[server] Client '+ str(self.clientAddr) + ' connection error' + Bcolors.ENDC)
                self.clientRtspSocket.close()
                if self.sendRtpEvent != None:
                    self.sendRtpEvent.set()
                    self.rtpSocket.close()
                return
            
            if undecodedData:
                print(Bcolors.OKCYAN +'[server] Receive RTSP from '+ str(self.clientAddr) + ': '+ Bcolors.ENDC)
                self.handle_rtsp_req(undecodedData)
            else:
                print(Bcolors.FAIL + '[server] Client '+ str(self.clientAddr) + ' disconnected' + Bcolors.ENDC)
                self.clientRtspSocket.close()
                if self.sendRtpEvent != None:
                    self.sendRtpEvent.set()
                    self.rtpSocket.close()
                return
                
    
    def handle_rtsp_req(self, undecodedData):
        ''' handel rtsp requesets '''
        data = undecodedData.decode()
        print(data)
        try:
            requestType = data.split(' ')[0]
            seqNum = data.split('\n')[1].split(' ')[1]

        except:
            rtsp = Rtsp()
            print(Bcolors.FAIL + '[client process] cannot resolve RTSP' + Bcolors.ENDC)
            self.clientRtspSocket.send(rtsp.replyRtsp(rtsp.BAD_REQUEST, 0, 0))

        try:
            if requestType == self.SETUP and self.state==self.INIT:
                fileName = data.split(' ')[1]
                clientRtpPort = int(data.split('\n')[2].split(' ')[1])
                self.handle_setup(fileName, clientRtpPort)
                self.state = self.READY

            elif requestType == self.PLAY and self.state==self.READY:
                self.state = self.PLAYING  
                self.handle_play(seqNum)

            elif requestType == self.PAUSE and self.state==self.PLAYING:
                self.handle_pause(seqNum)
                self.state = self.READY

            elif requestType == self.TEARDOWN and (self.state==self.READY or self.state==self.PLAYING):
                self.handle_teardown(seqNum)
                self.state = self.INIT
            
            elif requestType == self.ASKFILENAME:
                self.handle_askfilename(seqNum)

            else:
                rtsp = Rtsp()
                print(Bcolors.FAIL + '[client process] bad request' + Bcolors.ENDC)
                self.clientRtspSocket.send(rtsp.replyRtsp(rtsp.BAD_REQUEST, 0, 0))
        except:
            rtsp = Rtsp()
            print(Bcolors.FAIL + '[client process] bad request' + Bcolors.ENDC)
            traceback.print_exc(file=sys.stdout)

            self.clientRtspSocket.send(rtsp.replyRtsp(rtsp.BAD_REQUEST, 0, 0))

    ''' RTSP Requests Handlers '''
    def handle_setup(self, fileName, clientRtpPort):
        """ Setup RTP socket """
        try:
            self.clientRtpPort = clientRtpPort
            self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rtpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.rtpSocket.bind(('', self.rtpPort))
        except:
            print(Bcolors.FAIL + '[server] Cannot init RTP socket' + Bcolors.ENDC)
            return
        
        """ init video stream """
        self.videoStream = VideoStream(fileName )

    def handle_play(self, seqNum):
        print(Bcolors.WARNING + "[server] Receive a PLAY request" + Bcolors.ENDC)
        rtsp = Rtsp()
        self.clientRtspSocket.send(rtsp.replyRtsp(rtsp.OK, 0, 0))
        print('chk')

        ''' Create a thread for sending RTP packets '''
        self.state = self.PLAYING
        self.sendRtpEvent = threading.Event()
        self.sendRtpThread = threading.Thread(target=self.send_rtp)
        self.sendRtpThread.start()
    
    def handle_pause(self, seqNum):
        print(Bcolors.BOLD+Bcolors.OKCYAN+"PAUSE"+Bcolors.ENDC)
        rtsp = Rtsp()
        self.clientRtspSocket.send(rtsp.replyRtsp(rtsp.OK, seqNum, 0))
        self.sendRtpEvent.set()
        
    def handle_teardown(self, seqNum):
        print(Bcolors.BOLD+Bcolors.OKCYAN+"TEARDOWN"+Bcolors.ENDC)
        rtsp = Rtsp()
        self.clientRtspSocket.send(rtsp.replyRtsp(rtsp.OK, seqNum, 0))
        self.state = self.INIT

 
        self.sendRtpEvent.set()
        self.videoStream.set_current_frameNumber(0)

    def handle_askfilename(self, seqNum):
        print(Bcolors.BOLD+Bcolors.OKCYAN+"ASK FILE NAME"+Bcolors.ENDC)
        rtsp = Rtsp()
        tmp = rtsp.replyRtsp(rtsp.OK, seqNum, 0).decode()
        tmp = tmp +  '\nFiles: ' + ','.join(self.fileList)
        
        
        self.clientRtspSocket.send(tmp.encode())
        self.state = self.INIT


    def send_rtp(self):
        send = True
        count = 0

        if self.sendRtpEvent.isSet():
            return

        totalFrameNumber, totalAudioNumber, frameRate = self.videoStream.get_basic_info()
        if totalAudioNumber > 0:
            print(totalFrameNumber/totalAudioNumber)
    
        while send:
            if totalAudioNumber > 0:
                count = (count + 1)%(totalFrameNumber//totalAudioNumber)
            else:
                count = 1


            # Stop sending if the event is set(due to PAUSE or TEARDOWN)
            if self.sendRtpEvent.isSet():
                break


            dataTuple = self.videoStream.get_next_frame()
            if not dataTuple:
                self.videoStream.set_current_frameNumber(0)
                self.clientRtpSocket.close()
                return

            data, frameNumber = dataTuple


            if count==0 and totalAudioNumber != 0:
                if self.sendRtpEvent.isSet():
                    return
                audio = self.videoStream.get_next_audio()
                if not audio:
                    self.videoStream.set_current_frameNumber(0)
                    self.clientRtpSocket.close()
                    return
                for i in range(len(audio)):

                    rtpPacket = RtpPacket()
                    if i==len(audio)-1:
                        rtpPacket.encode(2,0,0,0,1,10,totalFrameNumber - frameNumber - 1,0,audio[i])
                    else:
                        rtpPacket.encode(2,0,0,0,0,10,totalFrameNumber - frameNumber - 1,0,audio[i])
                    self.rtpSocket.sendto(rtpPacket.getPacket(), (clientAddr, port))

            if(frameNumber>=totalFrameNumber-1):
                send = False
                self.state = self.INIT            
            
            if data:
                
                for i in range(len(data)):
                    if self.sendRtpEvent.isSet():
                        return
                    rtpPacket = RtpPacket()
                    if i == len(data)-1:
                        rtpPacket.encode(2,0,0,0,1,0,totalFrameNumber - frameNumber - 1,0,data[i])
                    else:
                        rtpPacket.encode(2,0,0,0,0,0,totalFrameNumber - frameNumber - 1,0,data[i])
                    
                    try:
                        port = int(self.clientRtpPort)
        
                        clientAddr = self.clientAddr[0]
                        
                        self.rtpSocket.sendto(rtpPacket.getPacket(), (clientAddr, port))
                    except:
                        print(Bcolors.FAIL + "[server] Connection Error" + Bcolors.ENDC)  
                        print('-'*60)
                        traceback.print_exc(file=sys.stdout)
                        print('-'*60)
                        self.clientRtpSocket.close()
                        return
                time.sleep(1/frameRate*0.85)

        return




            
    

