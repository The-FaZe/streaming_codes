import socket
from time import time,sleep
import cv2
from struct import unpack,pack
import numpy as np
import multiprocessing as mp


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

        
def set_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip =socket.gethostbyname(socket.gethostname())
    server_address = (ip,port)
    sock.bind(server_address)
    print ('starting up on',server_address[0],':',server_address[1])
    sock.listen(1)
    print('step#1')
    connection, client_address = sock.accept()
    print('client_address is ',client_address[0],client_address[1])
    return connection

def set_client(ip,port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip,port)
    client.connect(server_address)
    print('The connection has been started')
    return client

def recv_msg(connection,msglen,bufferlen):
    try:
        rcvdlen = 0
        msg = [];
        while(rcvdlen < msglen):
            chunk = connection.recv(min(msglen - rcvdlen, bufferlen))
            if (len(chunk) is 0) :
                raise OSError("socket connection broken")
            msg.append(chunk)
            rcvdlen += len(chunk)
        msg=b''.join(msg)        
        return msg
    except ( KeyboardInterrupt,IOError,OSError)as e:
        connection.close()
        raise e


def send_frame(connection,img,Quality=90):
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),Quality]
    _ ,enc_img = cv2.imencode('.jpg',img,encode_param)
    buff = len(enc_img)
    print(buff)
    buff = pack('>L',buff)
    enc_img1 = enc_img.tostring()
    connection.sendall(buff)
    connection.sendall(enc_img1)
    return

def recv_frame(connection):
    msglen = recv_msg(connection,4,4)
    msglen = unpack(">L", msglen)[0]
    frame = recv_msg(connection,msglen,2048)
    return frame,msglen

def decode_frame(frame):
    frame = np.frombuffer(frame,dtype='uint8')
    frame = cv2.imdecode(frame,1)
    return frame
    
class Frames_rcv(mp.Process):       

    def __init__(self,ip,port,status=True,w_max=30):
        self.client = set_client(ip, port)
        self.frames = mp.Queue(0)
        self.key  = mp.Value('b',True)     
        mp.Process.__init__(self)
        self.status = status
        if self.status:
            self.m = mean(w_max)

    def run(self):
        try:
            msglen_sum = 0
            y = time()
            while (self.key.value):
                x = time()
                frame_,msglen = recv_frame(self.client)
                msglen_sum += msglen
                self.frames.put([frame_,msglen,time()-x])	    # Closing the camera after breaking the loop
            print('The secound process is terminated \n',
                  'The total average Rate is ',msglen_sum/((time-y)*1000),'KB/s')
            self.client.close()
        except ( KeyboardInterrupt,IOError,OSError)as e:
            self.frames.close()
            print('The secound process is terminated \n',
                  'The total average Rate is ',msglen_sum/((time()-y)*1000),'KB/s')
            self.client.close()
        return
    
    def get_frame(self,rgb = True):
        frame_ , msglen , spf = self.frames.get(True,60)
        frame_ = decode_frame(frame_)
        
        if self.status:
            [msglen_rate,spf] = self.m.mean([msglen,spf])
            add_status(frame_,s1 = 'size :'+str(msglen/1000)+'KB'
                             ,s2 = 'FPS :'+str(1/spf)
                             ,s3= 'Rate :'+str(msglen_rate/(spf*1000))+'KB/s')
        if rgb:
            b,g,r  = cv2.split(frame_)                  # get b,g,r
            frame_ = cv2.merge([r,g,b])       	        # switch it to rgb

        return frame_                                   #Returning the frame as an output

    
    def exit(self):
        self.key.value = False                 # breaking the capture thread
        self.frames.close()
        self.join()                            # waiting for the capture thread to terminate
        print('The program has been terminated ')

