import socket
from time import sleep,time
import cv2
from struct import unpack,pack
import numpy as np
import multiprocessing as mp


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

def send_frame(connection,img,Quality=90):
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),Quality]
    _ ,enc_img = cv2.imencode('.jpg',img,encode_param)
    buff = len(enc_img)
    print(buff)
    buff = pack('>Q',buff)
    enc_img1 = enc_img.tostring()
    connection.send(buff)
    connection.sendall(enc_img1)
    return

def recv_frame(connection):
    msglen = connection.recv(8)
    print(len(msglen))
    msglen = unpack(">Q", msglen)[0]
    chunklen = []
    rcvdlen = 0
    frame = [];
    while(rcvdlen < msglen):
        x = time()
        chunk = connection.recv(min(msglen - rcvdlen, 2048))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        frame.append(chunk)
        rcvdlen = rcvdlen+len(chunk)
    frame=b''.join(frame)
    return frame,msglen

def decode_frame(frame):
    frame = np.frombuffer(frame,dtype='uint8')
    frame = cv2.imdecode(frame,1)
    return frame
    
class Frames_rcv(mp.Process):       

    def __init__(self,ip,port):
        self.client = TCP.set_client(ip, port)
        self.frames = mp.Queue(0)
        self.key  = mp.Value('b',True)     
        mp.Process.__init__(self)

    def run(self):
        try:
            while (self.key.value):
                msglen = []
                x = time()
                frame_,msglen = TCP.recv_frame(self.client)
                self.frames.put([frame_,msglen,time()-y])	    # Closing the camera after breaking the loop
            print('The secound process is terminated ')
            self.client.close()
        except (KeyboardInterrupt,IOError)as e:
            print('The secound process is terminated ')
            self.client.close()
        return
    
    def get_frame(self,rgb = True):
        [frame_,msglen,spf] = self.frames.get(True,30)
        print(msglen  ,  spf)
        frame_ = TCP.decode_frame(frame_)
        if rgb:
            b,g,r  = cv2.split(frame_)                  # get b,g,r
            frame_ = cv2.merge([r,g,b])       	        # switch it to rgb
        return frame_                                   #Returning the frame as an output

    
    def exit(self):
        self.key.value = False                 # breaking the capture thread
        self.terminate()
        self.frames.close()
        self.frames.join()
        self.join()                            # waiting for the capture thread to terminate
        print('The program has been terminated ')
