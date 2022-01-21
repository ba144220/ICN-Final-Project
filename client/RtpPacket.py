import time

HEADER_SIZE = 12

class RtpPacket:
    
    def __init__(self):
        self.header = bytearray(HEADER_SIZE)
        self.isInit = False
    
    def encode(self,ver, p, x, cc, m, pt, seqNum, ssrc, payload):
        timestamp = int(time.time()) # time.time() returns a float(32 bits)

        self.header[0] = ver<<6 | p<<5 | x<<4 | cc
        self.header[1] = (m<<7 | pt)%256
        self.header[2] = (seqNum >> 8)%256
        self.header[3] = seqNum % 256

        self.header[4] = (timestamp >> 24)%256
        self.header[5] = (timestamp >> 16)%256
        self.header[6] = (timestamp >> 8)%256
        self.header[7] = timestamp % 256

        self.header[8] = (ssrc >> 24)%256
        self.header[9] = (ssrc >> 16)%256
        self.header[10] = (ssrc >> 8)%256
        self.header[11] = ssrc % 256     

        self.payload = payload   

        self.isInit = True

    def decode(self, byteArray):
        
        self.header = bytearray(byteArray[0:HEADER_SIZE])
        self.payload = byteArray[HEADER_SIZE:]

        self.isInit = True
    

    # self.header[0]
    def getVersion(self):
        if self.isInit:
            return int((self.header[0]>>6)%4)
        else:
            return -1
    def getPadding(self):
        if self.isInit:
            return int((self.header[0]>>5)%2)
        else:
            return -1
    def getExtension(self):
        if self.isInit:
            return int((self.header[0]>>4)%2)  
        else:
            return -1  
    def getContributorCount(self):
        if self.isInit:
            return int((self.header[0])%16)    
        else:
            return -1

    # self.header[1]
    def getMarker(self):
        if self.isInit:
            return int((self.header[1]>>7)%2)    
        else:
            return -1   
    def getPayloadType(self):
        if self.isInit:
            return int((self.header[1])%128)    
        else:
            return -1   

    # self.header[2:4]
    def getSequenceNumber(self):
        if self.isInit:
            return int(self.header[2]*256 + self.header[3])    
        else:
            return -1       
    # self.header[4:8]
    def getTimeStamp(self):
        if self.isInit:
            return int(self.header[4]<<24 | self.header[5]<<16 | self.header[6]<<8 | self.header[7])    
        else:
            return -1      
    # self.header[8:12]
    def getSynchronizedSourceIdentifier(self):
        if self.isInit:
            return int(self.header[8]<<24 | self.header[9]<<16 | self.header[10]<<8 | self.header[11])    
        else:
            return -1 

    def getPayload(self):
        if self.isInit:
            return self.payload
        else:
            return None
    def getPacket(self):
        if self.isInit:
            return self.header + self.payload
        else:
            return None        
