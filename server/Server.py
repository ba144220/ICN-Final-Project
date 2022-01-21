import socket
import sys
import threading


from Bcolors import Bcolors
from ClinetProcess import ClientProcess

class Server:

    def __init__(self, rtspPort=3000, fileList=[]):
        try:
            self.rtspPort = rtspPort
            self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rtspSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.rtspSocket.bind(('', self.rtspPort))
            self.nextRtpPort = rtspPort + 1
            self.fileList = fileList
        except:
            print(Bcolors.FAIL + '[server] Cannot init RTSP socket' + Bcolors.ENDC)
            print(Bcolors.FAIL + '[server] Usage: server(rtspPort)' + Bcolors.ENDC)
            return

        ''' Initialize Properties '''
        print(Bcolors.OKGREEN + '[server] RTSP server started at PORT: ' + Bcolors.BOLD + str(self.rtspPort) + Bcolors.ENDC)
        print(Bcolors.OKGREEN + '[server] wait for connection...\n\n'+ Bcolors.ENDC)   
        self.rtspSocket.listen(5)      

        ''' Main Loop (waiting for clients to connect) '''
        self.main()

    def main(self):
        while True:
            # listen to any client to connect 
            c, addr = self.rtspSocket.accept()
            print(Bcolors.OKGREEN + '[server] Connect to client: ' + str(addr) + Bcolors.ENDC)   
            
            # create a new thread for the new client
            threading.Thread(target = self.client_process, args=(c,addr)).start()
    
    def client_process(self, clientRtspSocket, clientAddr):
        """ Run Client Processes """

        clientProcess = ClientProcess(clientRtspSocket, clientAddr, self.nextRtpPort, self.fileList)
        clientProcess.run()
        self.nextRtpPort += 1


