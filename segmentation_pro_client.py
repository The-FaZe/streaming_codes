import numpy as np
import multiprocessing as mp
from time import sleep
from TCP import Frames_rcv
import cv2

#For testing
def main(fun,args=()):
    try:
        client = TCP.set_client('192.168.1.112', 6666)
        frame = Frames_rcv(client)    # setting up the object
        frame.start()                 # initializing the capture thread
        while frame.is_alive():                    # Real time processing loop
            frame_ = frame.get_frame(False)     # Getting a fraf in form of BGR
            fun(frame_)   
        print ('No More frames to capture ')   # Printing there is no frames when breaking out of the loop
        frame.frames.close()
        frame.join()                            # waiting for the capture thread to terminate
        print('The programe is exiting ')
        cv2.destroyAllWindows()                 # clearing the windows
    except (KeyboardInterrupt,IOError)as e:
        frame.key.value = False                 # breaking the capture thread
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
