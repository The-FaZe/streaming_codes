# a class to determine the decision array
from random import shuffle
import numpy as np
from math import gcd
import threading
import cv2
import multiprocessing as mp
from collections import deque

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
                    return
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
    
    def __init__(self,fps_old,fps_new,id_):
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

    def exit(self):
        self.key = 0   # breaking the capture loop
        self.join()     # waiting for the capture thread to terminate smoothly
        self.frames.close()
        print ('No More frames to capture ')


class Cap_Process(mp.Process):
    
    def __init__(self,fps_old,fps_new,id_):
        self.frames = mp.Queue(0)
        self.key = mp.Value('b',True)
        mp.Process.__init__(self)
        self.index =decision(fps_old,fps_new)
        self.id_ =id_
        self.start()
        
    def run(self):
        try:
            vid_cap = cv2.VideoCapture(self.id_)
            success, frame_ = vid_cap.read()
            
            if not success:
                print ('No Camera is detected ')
                vid_cap.release()
                self.frames.put(True)
                return
            
            while (success and self.key.value):
                
                if self.index.index():
                    self.frames.put(frame_)
                    
                success, frame_ = vid_cap.read()
                
            vid_cap.release()
            print('The secound process is terminated ')
        except KeyboardInterrupt :
            vid_cap.release()
            print('The secound process is terminated ')

    def get(self,rgb = True):
        frame_ = self.frames.get()      # Getting a frame from the queue
        if rgb:
            frame_ = frame[...,::-1]    # Converting from BGR to RGB 
        return frame_ 			# Returning the frame as an output

    def exit(self):
        self.key.value = False   # breaking the capture loop
        self.join()     # waiting for the capture thread to terminate smoothly
        self.frames.close()
        print ('No More frames to capture ')
            

