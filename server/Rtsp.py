

from http.client import BAD_REQUEST, NOT_IMPLEMENTED


class Rtsp:
    BAD_REQUEST = 400
    OK = 200
    FILE_NOT_FOUND = 404
    CONNECTION_ERROR = 500
    NOT_IMPLEMENTED = 501

    def setup(self, fileName, rtspSeq, rtpPort):
        """
        C->S: SETUP rtsp://example.com/media.mp4/streamid=0 RTSP/1.0
            CSeq: 3
            Client_port: 8000

        S->C: RTSP/1.0 200 OK
            CSeq: 3
            Client_port: 8000
            Server_port: 9000
            Ssrc: 1234ABCD
            Session: 12345678
        """
        req = "SETUP " + str(fileName) + " RTSP/1.0\n"
        req += "CSeq: " + str(rtspSeq) + '\n'
        req += "Client_port: " + str(rtpPort) 

        return req.encode()

    def play(self, fileName, rtspSeq, session, startAt=0):
        """
        C->S: PLAY rtsp://example.com/media.mp4 RTSP/1.0
            CSeq: 4
            Range: npt=5-20
            Session: 12345678

        S->C: RTSP/1.0 200 OK
            CSeq: 4
            Session: 12345678
            RTP-Info: url=rtsp://example.com/media.mp4/streamid=0;seq=9810092;rtptime=3450012
        """
        req = "PLAY " + str(fileName) + " RTSP/1.0\n"
        req += "CSeq: " + str(rtspSeq) + '\n'
        req += "Range: " + str(startAt) + '\n'
        req += "Session: " + str(session)
        
        return req.encode()

    def pause(self, fileName, rtspSeq, session):
        """
        C->S: PAUSE rtsp://example.com/media.mp4 RTSP/1.0
            CSeq: 5
            Session: 12345678

        S->C: RTSP/1.0 200 OK
            CSeq: 5
            Session: 12345678
        """
        req = "PAUSE " + str(fileName) + " RTSP/1.0\n"
        req += "CSeq: " + str(rtspSeq) + '\n'
        req += "Session: " + str(session)
        
        return req.encode()
    
    def teardown(self, fileName, rtspSeq, session):
        """
        C->S: TEARDOWN rtsp://example.com/media.mp4 RTSP/1.0
            CSeq: 8
            Session: 12345678

        S->C: RTSP/1.0 200 OK
            CSeq: 8
        """
        req = "TEARDOWN " + str(fileName) + " RTSP/1.0\n"
        req += "CSeq: " + str(rtspSeq) + '\n'
        req += "Session: " + str(session)

        return req.encode()
    

    def replyRtsp(self, code, seq, session):
        """Send RTSP reply to the client."""
        if code == self.OK:
            #print "200 OK"
            reply = 'RTSP/1.0 200 OK\n'
            reply += 'CSeq: ' + str(seq) + '\n'
            reply += 'Session: ' + str(session)
            return reply.encode() 
		# Error messages
        elif code == self.BAD_REQUEST:
            reply = 'RTSP/1.0 400 BAD REQUEST\n'       
            return reply.encode()               
        elif code == self.FILE_NOT_FOUND:
            reply = 'RTSP/1.0 404 NOT FOUND\n'       
            return reply.encode()   
        elif code == self.CONNECTION_ERROR:
            reply = 'RTSP/1.0 500 CONNECTION ERROR\n'         
            return reply.encode()
        elif code == self.NOT_IMPLEMENTED :
            reply = 'RTSP/1.0 501 NOT IMPLEMENTED\n'         
            return reply.encode()
        

