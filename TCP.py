import socket
from time import sleep
import cv2
from struct import unpack,pack
import numpy as np

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
    server_address = (ip,6666)
    client.connect(server_address)
    return client

def send_frame(connection,img):
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    _ ,enc_img = cv2.imencode('.jpg',img,encode_param)
    buff = len(enc_img)
    print(buff)
    buff = pack('>I',buff)
    enc_img1 = enc_img.tostring()
    connection.send(buff)
    connection.sendall(enc_img1)
    return

def recv_frame(connection):
    connection.settimeout(2)
    msglen = connection.recv(4)
    msglen = unpack(">I", msglen)[0]
    rcvdlen = 0
    frame = [];
    while(rcvdlen < msglen):
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
    

    
