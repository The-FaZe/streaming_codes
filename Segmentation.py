# a class to determine the decision array
from random import shuffle
import numpy as np
from math import gcd
import threading
import cv2
import multiprocessing as mp
from collections import deque
import Network
import Streaming
# A class to generate random index that segment the real time stream
# then pick snippets out of every segment in real time behaviour 
class decision():
    
    #A method to construct the decision array as soon as it's called
    
    def __init__(self,fpso,fpsn):
        GCD  = gcd(fpso,fpsn)           #Calculating greatest common divisor
        L    = fpso//GCD                #The number of frames in 1 segment
        n    = fpsn//GCD                #The number of  snippets in 1 segment


        #Decision array is to determine keeping the frame or dropping it,
        #that number of ones determines number of (selected frames(snippets) - the very first frame) in a seg
        # converting the numpy array to list datatype (more efficient in this case)
        
        self.array    = np.append(np.zeros(L-n),np.ones(n-1)).tolist()
        shuffle(self.array)             #Shuffling the instants those frames are captured in
        self.array.append(1)            #Adding the first frame index in the begining of the of the Decision array
        self.backup = self.array.copy() #the back-up for the list for generating a new one when it's totally consumed 

    # A method to get the current index and generating new array when it's totally consumed 
    def index(self):
        index_ = self.array.pop()           # getting the index from the end of the array 
        if not len(self.array):             # If there is no elements in the list start generating new one 
            self.array = self.backup.copy() # Copy the elements from the backup list
            shuffle(self.array)             # Shuffle the array to select in diferent locations 
        return index_

class thrQueue():
    
    def __init__(self):
        self.cond_ = threading.Condition()
        self.queue_ = deque()
        self.exit_ = False

    def get(self):
        with self.cond_:
            while not len(self.queue_)  :
                self.cond_.wait()
                if self.exit_:
                    return 0
            item = self.queue_.popleft()
        return item
        
    def put(self,item):
        with self.cond_:
            self.queue_.append(item)
            self.cond_.notifyAll()

    def close(self):
        self.exit_=True
        with self.cond_:
            self.cond_.notifyAll()
        self.queue_.clear()
        
        

class Cap_Thread(threading.Thread):
    
    def __init__(self,fps_old,fps_new,port,id_=0):
        self.frames = thrQueue()
        self.key = True
        threading.Thread.__init__(self)
        self.index =decision(fps_old,fps_new)
        self.id_ =id_
        self.start()
        
    def run(self):

        vid_cap = cv2.VideoCapture(self.id_)
        success, frame_ = vid_cap.read()
        
        if not success:
            print ('No Camera is detected ')
            vid_cap.release()
            self.frames.put(True)
            return
        print("The camera is detected")
        while (success and self.key):
            
            if self.index.index():
                self.frames.put(frame_)
                
            success, frame_ = vid_cap.read()
        vid_cap.release()
        print('The secound process is terminated ')

    def get(self,rgb = True):
        frame_ = self.frames.get()      # Getting a frame from the queue
        if rgb:
            frame_ = frame[...,::-1]    # Converting from BGR to RGB 
        return frame_ 			# Returning the frame as an output

    def close(self):
        self.key = 0   # breaking the capture loop
        self.join()     # waiting for the capture thread to terminate smoothly
        self.frames.close()
        print ('No More frames to capture ')


class Cap_Process(mp.Process):
    
    def __init__(self,fps_old,fps_new,id_,port,ip="",Tunnel=True,rgb=True):
        self.frames = mp.Queue(0)
        self.key = mp.Value('b',True)
        self.rgb = rgb
        self.index =decision(fps_old,fps_new)
        self.id_ =id_
        self.port = port
        self.ip = ip
        self.Tunnel = Tunnel
        mp.Process.__init__(self)
        self.start()
    def run(self):
        try:
            client = Network.set_client(port=self.port,
                ip=self.ip,Tunnel=self.Tunnel)
            vid_cap = cv2.VideoCapture(self.id_)
            success, frame_ = vid_cap.read()
            if not success:
                print ('No Camera is detected ')
                vid_cap.release()
                send_frames.close()
                self.frames.put(True)
                return
            print("The camera is detected")

            send_frames = Streaming.send_frames_thread(client)
            
            while (success and self.key.value and send_frames.isAlive()):
                if self.rgb:
                    frame_ = frame[...,::-1]    # Converting from BGR to RGB  
                
                if self.index.index():
                    send_frames.put(cv2.resize(frame_,(224,224)))
                    self.frames.put(frame_)
                    
                success, frame_ = vid_cap.read()
            self.frames.put(True)
            client.close()
            print("The program cut the connection")
            send_frames.close()
            vid_cap.release()
            print("The program broke the connection to the camera")
        except (KeyboardInterrupt,IOError,OSError) :
            self.frames.put(True)
            client.close()
            print("The program cut the connection")
            vid_cap.release()
            send_frames.close()
            print("The program broke the connection to the camera")

    def get(self,rgb = True):
        frame_ = self.frames.get()      # Getting a frame from the queue
		# Returning the frame as an output
        return frame_

    def close(self):
        self.key.value = False   # breaking the capture loop
        self.join()     # waiting for the capture thread to terminate smoothly
        self.frames.close()
        print ('No More frames to capture ')
            

# A module to generate the mean of the input in real time with window == max

class mean():
    def __init__(self,max = 30):
        self.queue = np.array([])
        self.max = max
    def mean(self,inp,dim=2):
        if self.queue.size is 0:
            self.queue = np.array(inp)
            self.queue = np.expand_dims(self.queue , axis=0)
        else:
            self.queue = np.concatenate((np.expand_dims(inp , axis=0)
                                         ,self.queue), axis=0)
            if (self.queue.shape[0] >= self.max):
                self.queue = self.queue[0:self.max-1]
        return np.mean(self.queue, axis=0)




# A method to add status on the image the frame_ is the incoming image and s1,s2,s3 are the txt to put on the image

def add_status(frame_, s1='put your first  text'
                     , s2='put your second text'
                     , s3='put your third  text'):
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText1 = (5,10)
    bottomLeftCornerOfText2 = (5,20)
    bottomLeftCornerOfText3 = (5,30)

    fontScale              = 0.3
    fontColor              = (255,255,255)
    lineType               = 1
    cv2.putText(frame_,s1, bottomLeftCornerOfText1, 
    font, fontScale, fontColor, lineType)

    cv2.putText(frame_,s2, bottomLeftCornerOfText2, 
    font, fontScale, fontColor, lineType)

    cv2.putText(frame_,s3, bottomLeftCornerOfText3, 
    font, fontScale, fontColor, lineType)

