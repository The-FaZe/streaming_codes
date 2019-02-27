import Network
import multiprocessing as mp
from time import time
import threading
from socket import socket
import Segmentation

class rcv_frames_thread(threading.Thread):
    def __init__(self,connection=socket()
        ,status=True,w_max=30):
        
        self.connection = connection
        
        self.frames = Segmentation.thrQueue()
        
        self.key  = True

        self.status = status

        threading.Thread.__init__(self)

        if self.status:  # If the flag is true then initialize the mean object 
            self.m = Segmentation.mean(w_max)

        self.start()



    def run(self):
        try:
            msglen_sum = 0 #the size of total frames received 
            y = time() #Total time of the receiving
            # The loop to receive frames from the connection
            #self.key is a flag to be used by the main process to break the loop and terminate the parallel process
            while (self.key):
                x = time() # start recording the time of receiving each frame 
                frame_,msglen = Network.recv_frame(self.connection) # receiving a frame 
                msglen_sum += msglen # updating the size of the total frames received
                
                #adding the (frame received,the size of the frame and the total time it took to receive it) in the shared memory buffer
                self.frames.put([frame_,msglen,time()-x]) 

            #calculating and printing the average speed of the connection 
            print('The secound process is terminated \n',
                  'The total average Rate is ',msglen_sum/((time()-y)*1000),'KB/s')
            self.frames.close() 
            self.connection.close() #closing the connection if the for loop is broken

        #breaking the connection and terminating the process if there is an error , interruption or connection break 
        except ( KeyboardInterrupt,IOError,OSError)as e:
            print('The secound process is terminated \n',   #calculating and printing the average speed of the connection 
                  'The total average Rate is ',msglen_sum/((time()-y)*1000),'KB/s')
            self.connection.close() #closing the connection if the for loop is broken
            self.frames.close() #declaring that there is no data will be added to the queue from this process
        return



    #The method is responsible for consuming data from the queue ,decoding it
    # printing status on it and converting it into RGB if desired 
    def get(self):
        frame_ = self.frames.get() #blocking until getting the data with time out of 60 s 
        if frame_ is 0:
            return 0
        frame_ , msglen , spf = frame_
        frame_ = Network.decode_frame(frame_) #decoding the frames 
        
        if self.status: #printing status if desired 
            [msglen_rate,spf] = self.m.mean([msglen,spf])
            Segmentation.add_status(frame_,s1 = 'size :'+str(msglen/1000)+'KB'
                             ,s2 = 'FPS :'+str(1/spf)
                             ,s3= 'Rate :'+str(msglen_rate/(spf*1000))+'KB/s')

        return frame_                                   #Returning the frame as an output

    # The method is responsible for Quiting the program swiftly with no daemon process
    # the method is to be using in the main process code 
    def close(self):
        self.key = False # breaking the while loop of it's still on in the parallel process(run)
        self.frames.close() # declaring there is no frames will be put on the shared queue from the main process
        self.join() # waiting for the parallel process to terminate
        print('The program has been terminated ')




class send_frames_thread(threading.Thread):
    def __init__(self,connection=socket()):
        self.key = True
        self.frames = Segmentation.thrQueue()
        self.connection = connection
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        try:
            while (self.key):

                Network.send_frame(self.connection,self.frames.get())

            self.frames.close()
            self.connection.close()
            print('sending Frames is stopped ')

        except(KeyboardInterrupt,IOError,OSError):
            self.frames.close()
            self.connection.close()
            print('sending Frames is stopped')

    def put(self,frame):
        return self.frames.put(frame)

    def close(self):
        self.key = False # breaking the while loop of it's still on in the parallel process(run)
        self.frames.close() # declaring there is no frames will be put on the shared queue from the main process
        self.join() # waiting for the parallel process to terminate




# A class inherited from the multiprocessing module
# The class is a client receiving frames from the server processing of the received frame is on the main process
# receiving of the frame is on another process 
class client_rcv_frames_process(mp.Process):
    # IP and port of the server as input to the class
    # mean window to calculate FPS and the speed of receiving data
    # Status is the flag for writing on the image the status of connection 
    def __init__(self,ip,port,status=True,w_max=30): 
        self.client = Network.set_client(ip, port) #setting the connection from the client end 
        self.frames = mp.Queue(0) # Setting the Queue object(Shared memory between process) 
        self.key  = mp.Value('b',True) #the flag across process to manage closing from the parallel process smoothly

        # invoking the base class constructor (defining the class as a multiprocessing class
        # inheriting the prvious initializations from the code besides the shared memory frames Queue and key
        mp.Process.__init__(self)
        self.status = status 
        if self.status:  # If the flag is true then initialize the mean object 
            self.m = Segmentation.mean(w_max)

    # The method in the multiprocessing class that's run in another parallel process
    # it's designed to listen and receive data(frames) from the established connection
    # and close the queue and client when it's done receiving data from the connection because of error or an interrupt 
    def run(self):
        try:
            msglen_sum = 0 #the size of total frames received 
            y = time() #Total time of the receiving
            # The loop to receive frames from the connection
            #self.key.value is a flag to be used by the main process to break the loop and terminate the parallel process
            while (self.key.value):
                x = time() # start recording the time of receiving each frame 
                frame_,msglen = Network.recv_frame(self.client) # receiving a frame 
                msglen_sum += msglen # updating the size of the total frames received

                
                #adding the (frame received,the size of the frame and the total time it took to receive it) in the shared memory buffer
                self.frames.put([frame_,msglen,time()-x]) 

            #calculating and printing the average speed of the connection 
            print('The secound process is terminated \n',
                  'The total average Rate is ',msglen_sum/((time-y)*1000),'KB/s')
            self.client.close() #closing the connection if the for loop is broken
            self.frames.close() #declaring that there is no data will be added to the queue from this process 


        #breaking the connection and terminating the process if there is an error , interruption or connection break 
        except ( KeyboardInterrupt,IOError,OSError)as e:
            
            self.frames.close() #declaring that there is no data will be added to the queue from this process 
            print('The secound process is terminated \n',   #calculating and printing the average speed of the connection 
                  'The total average Rate is ',msglen_sum/((time()-y)*1000),'KB/s')
            self.client.close() #closing the connection if the for loop is broken
        return

    #The method is responsible for consuming data from the queue ,decoding it
    # printing status on it and converting it into RGB if desired 
    def get(self,rgb = True):
        frame_ , msglen , spf = self.frames.get(True,timeout=60) #blocking until getting the data with time out of 60 s 
        frame_ = decode_frame(frame_) #decoding the frames 
        
        if self.status: #printing status if desired 
            [msglen_rate,spf] = self.m.mean([msglen,spf])
            add_status(frame_,s1 = 'size :'+str(msglen/1000)+'KB'
                             ,s2 = 'FPS :'+str(1/spf)
                             ,s3= 'Rate :'+str(msglen_rate/(spf*1000))+'KB/s')
        if rgb: #converting the order of color to RGB
            b,g,r  = cv2.split(frame_)                  # get b,g,r
            frame_ = cv2.merge([r,g,b])       	        # switch it to rgb

        return frame_                                   #Returning the frame as an output
    

    # The method is responsible for Quiting the program swiftly with no daemon process
    # the method is to be using in the main process code 
    def close(self):
        self.key.value = False # breaking the while loop of it's still on in the parallel process(run)
        self.frames.close() # declaring there is no frames will be put on the shared queue from the main process
        self.join() # waiting for the parallel process to terminate
        print('The program has been terminated ')
