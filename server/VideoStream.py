
import sys
import cv2
import numpy as np
import pydub
import math
sys.path.insert(1, '/Users/yuchihsu/Desktop/NTU/110-1/電腦網路導論/final project/ICN-Final-Project/utils')
from Bcolors import Bcolors


class VideoStream:
    def __init__(self, fileName):
        """ Read mp4 file"""
        try:
            cap = cv2.VideoCapture('./videos/' + fileName+ '.mp4')
            self.fileName = fileName
            
        except:
            print(Bcolors.FAIL+"[video_stream] Cannot find the file!!!"+Bcolors.ENDC)
            print(Bcolors.FAIL+"[video_stream] Usage: video_stream(<file_path>)"+Bcolors.ENDC)
            return

        self.test()

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        if int(major_ver)  < 3 :
            fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Frames per second using cap.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
        else :
            fps = cap.get(cv2.CAP_PROP_FPS)
            print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
        print('Frame Rate: ', round(fps))
        if round(fps)==0:
            self.frameRate = 24
        else:
            self.frameRate = round(fps)
        


        """ Get the info of the file """
        self.frameNumber = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(Bcolors.WARNING +'='*10 + " Video File Info " + '='*10 + Bcolors.ENDC)
        print("Name: ", self.fileName)
        print("Frame Number: ", self.frameNumber)
        print("Frame Height: ", self.frameHeight)
        print("Frame Width: ", self.frameWidth)
        print(Bcolors.WARNING +'='*60+ Bcolors.ENDC)

        """ Convert mp4 file into bytes"""
        fc = 0
        ret = True
        self.frameBytes = []
        while (fc < self.frameNumber and ret):
            # print('[video_stream] Preprocessing Frame: ',fc)
            ret, frame = cap.read()
            _, fr = cv2.imencode('.JPEG', frame)
            fr = fr.tostring()
            # print('size: ',sys.getsizeof(fr))
            # print('-'*60)
            count = 0
            tmp = []
            while sys.getsizeof(fr) > count:
                tmp.append(fr[count: count+1500])
                count += 1500

            self.frameBytes.append(tmp)
            fc += 1
        cap.release()
        print(Bcolors.OKGREEN + '[video_stream] Preprocess file ' + self.fileName + ' completed' + Bcolors.ENDC )

        """ Set currentFrame to 0 """
        self.currentFrame = 0

    def get_basic_info(self):
        if self.hasAudio:
            return (self.frameNumber, len(self.audio), self.frameRate)
        else:
            return (self.frameNumber, 0, self.frameRate)
    
    
    def get_next_frame(self):
        if self.currentFrame >= self.frameNumber:
            print('[video_stream] Currect Frame: ', self.currentFrame)
            
            return None
            
        frame = self.frameBytes[self.currentFrame] # type of frame is bytes
        fn = self.currentFrame 
        self.currentFrame += 1
        if self.currentFrame == self.frameNumber:
            self.currentFrame = 0
        return frame, fn

    def set_current_frameNumber(self, target):
        """ Set self.currentFrame """
        if target >= self.frameNumber or target < 0:
            print(Bcolors.FAIL + "[video_stream] Target is out of range!!!" + Bcolors.ENDC)
        self.currentFrame = target
        self.currentAudio = target // 15 # 一秒30幀 = 0.5s for 15 frames

    def get_currect_frame_number(self):
        return self.currentFrame-1
    def get_total_frame_number(self):
        return self.frameNumber

    def read(self, fileName, normalized=False):
        
        """MP3 to numpy array"""
        a = pydub.AudioSegment.from_mp3(fileName)
        y = np.array(a.get_array_of_samples())
        if a.channels == 2:
            y = y.reshape((-1, 2))
        if normalized:
            return a.frame_rate, np.float32(y) / 2**15
        else:
            return a.frame_rate, y
    
    def test(self):
        try:
            audio_file = 'videos/' + self.fileName + '.mp3'
            sr, x = self.read(audio_file)
            byteArray = x.tobytes()

            count = 0
            res = []

            while len(byteArray) >= count+90000:
                halfSec = byteArray[count: count+90000]
                temp = []
                for i in range(60):
                    temp.append(halfSec[i*1500:(i+1)*1500])
                res.append(temp)
                count+=88200
            self.audio = res
            self.currentAudio = 0
            self.hasAudio = True
        except:
            self.hasAudio = False
            return

    def get_next_audio(self):
        self.currentAudio += 1
        return self.audio[self.currentAudio-1]
    
    


    
    








    
