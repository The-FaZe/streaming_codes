import numpy as np
import multiprocessing as mp
from time import sleep
import TCP 
import cv2

#the presented code is a mutithread class consists of 2 modules 
#	The first module is run on a parallel thread to the main thread and tasked to select the snippets in a random way 
#	then saving the selected snippets into the memory.
#The presented code is capped at the actual FPS of the camera.
class Frames_rcv(mp.Process):       # defining a thread class

    def __init__(self, ip, port):
        self.frames = mp.Queue(0)          # Allocating a name for the captured frames
        self.key  = mp.Value('b',True)     # Key to kill the process in the 2nd thread(parallel thread to the main) using the main thread.
        mp.Process.__init__(self)
        self.ip = ip                       #The FPS of the camera
        self.port = port                   #The FPS of the output

    # A module to select and save the selected frames into an array (runs in a parallel thread to the main thread of the main code)
    def run(self):
        client = TCP.set_client(self.ip,self.port)
        #Capturing loop designed to break, If the key is set to 0 or there's an error accessing the camera
        while (self.key.value):
            frame_,_ = TCP.recv_frame(client)
            self.frames.put(frame_)				 # Closing the camera after breaking the loop
        print('The secound process is terminated ')
        self.frames.put(True)
        return
    
    #This module is to fetch first frame which saved in the memory then erasing it(run in the main thread with the main code)
    def get_frame(self,rgb = True):
        frame_ = self.frames.get(True,30)
        print(len(frame_))
        frame_ = TCP.decode_frame(frame_)
        if rgb:
            b,g,r  = cv2.split(frame_)                  # get b,g,r
            frame_ = cv2.merge([r,g,b])       	        # switch it to rgb
        return frame_ 					#Returning the frame as an output

    
#For testing
def main(fun,args=()):
    frame = Frames_rcv('192.168.1.112',6666)    # setting up the object
    frame.start()                               # initializing the capture thread
    try:
        while frame.is_alive():                    # Real time processing loop
            frame_ = frame.get_frame(False)     # Getting a fraf in form of BGR
            if frame_ is True:
                break
            
            fun(frame_)
            
        print ('No More frames to capture ')   # Printing there is no frames when breaking out of the loop
        frame.frames.close()
        frame.join()                            # waiting for the capture thread to terminate
        print('The programe is exiting ')
        cv2.destroyAllWindows()                 # clearing the windows
        sleep(2)
    except KeyboardInterrupt:
        frame.key.value = False                 # breaking the capture thread
        sleep(0.5)
        frame.terminate()
        frame.join()                            # waiting for the capture thread to terminate
        frame.frames.close()
        cv2.destroyAllWindows()                 # clearing the windows
        print('The program has been terminated ')
def test(frame_,):
    frame_ = cv2.flip(frame_,0)         # The rest of code here(Any kind of processing is here)
    cv2.imshow('frame',frame_)          # The rest of code here(Any kind of processing is here)
    cv2.waitKey(30)
#Main For Testing
if __name__ == '__main__':
    main(test)
