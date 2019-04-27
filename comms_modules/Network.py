import socket
from time import time,sleep
import cv2
from struct import unpack,pack
import numpy as np
import multiprocessing as mp
from threading import Thread
import subprocess as sp
from paramiko.client import SSHClient,WarningPolicy


def tunneling_cmd_hpc_server(user,path,local_port):
    port = sp.run(["shuf","-i8000-9999","-n1"],capture_output=True)
    port =port.stdout.strip().decode()
    s = "localhost:"+port+":localhost:"+port
    tun_sp=sp.run(["ssh","-R",s,"login01","-N","-f"])
    if path is None:
        s="ssh -L {}:localhost:{} {}@login01.c2.hpc.bibalex.org -N".format(local_port,port,user)
    else:
        s="ssh -L {}:localhost:{} {}@login01.c2.hpc.bibalex.org -N -i {}".format(local_port,port,user,path)
    print("copy the following command \n",s)
    return int(port),tun_sp



def set_server(port,n,Tunnel,user,path):
    if Tunnel:
        ip = "localhost"
        port,s=tunneling_cmd_hpc_server(user=user,path=path,local_port=port) 
    else:
        ip =socket.gethostbyname(socket.gethostname())              # Getting the local ip of the server
        s = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #specifying socket type is IPV4"socket.AF_INET" and TCP "SOCK_STREAM"
    server_address = (ip,port)      # saving ip and port as tuple
    sock.bind(server_address)       # attaching the socket to the pc (code)
    print ('starting up on',server_address[0],':',server_address[1])
    sock.listen(n)     # start waiting for 1 client to connection 
    print('step#1')
    connection, client_address = sock.accept() #accepting that client and hosting a connection with him
    print('client_address is ',client_address[0],client_address[1])
    connection2, client_address = sock.accept() #accepting that client and hosting a connection with him
    print('client_address is ',client_address[0],client_address[1])
    connection = (connection,connection2)
    return connection,s  #returning the connection object for further use





# A method to set the client part to set up the connection
# (Ip is the ip of the server we want to connection with)
# Port is the port that the server is listening on
def set_client(port,ip="localhost",Tunnel=False,numb_conn=2):
    client = []
    if Tunnel:
        server_address = ("0.0.0.0",port)
        sshclient = SSHClient()
        sshclient.load_system_host_keys()
        sshclient.set_missing_host_key_policy(WarningPolicy())
        sshclient.connect(hostname="login01.c2.hpc.bibalex.org",username="alex039u4",passphrase="Kaiki is the best grill even in monogatori fagoteri"
            ,key_filename=r"C:\Users\PlebChan\AppData\Roaming\SPB_16.6\.ssh\id_rsa")
        for i in range(numb_conn):
            client.append(sshclient.get_transport().open_channel(kind='direct-tcpip',src_addr=server_address,dest_addr=server_address))
            client[i].setblocking(True)
    else:
        server_address = (ip,port)
        for i in range(numb_conn):
            client.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            client[i].setblocking(True)
            client[i].connect(server_address)
    print('The {} connection has been started'.format(numb_conn)) # printing when the connection is successful 

    return client #returning the connection object for further use


# A method to receive any kind of hex file knewing its size (msglen)
# the receiving is done on the both end (client and server) (TCP connection is full duplex communication )
# the connection of the receiving end must be assigned and the max buffer len
def recv_msg(connection,msglen,bufferlen):
    try:
        rcvdlen = 0#the total size of the received packets for the file 
        msg = [];# allocating a None list for the packets to concatenate onto

        #Receving Loop for the packets related of the file(msg)
        while(rcvdlen < msglen):
            
            chunk = connection.recv(min(msglen - rcvdlen, bufferlen)) #receiving chunks (Packets) capped at the bufferlen as max
            
            if (len(chunk) is 0) : # resing an error if there is no packets received 
                raise OSError("socket connection broken")
            
            msg.append(chunk) #concatenating the current received chunk to the total previously received chunks 
            rcvdlen += len(chunk)#updating the total received chunk len 
        msg=b''.join(msg)   #joining the total chunks together as bytes 
        return msg #retrning the msg as o/p
    except ( KeyboardInterrupt,IOError,OSError)as e:
        connection.close()
        raise e



# A method to send frame from either end of the communication with specifying the connection object
# the img input is a pure image without any encoding
# the encoding used here is JPEG then getting the size of the encoded image
# Then sending the size of the image in 4 bytes-size-msg then sending the actual encoded img afterwards
def send_frame(connection,img,Quality=90):
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),Quality] # object of the parameters of the encoding (JPEG with 90% quality) 
    _ ,enc_img = cv2.imencode('.jpg',img,encode_param) # encoding the img in JPEG with specified quality 
    buff = len(enc_img) # Getting the len of the encoded image  
    buff = pack('>L',buff) #converting the size into 4 bytes(struct) length msg ,(L means unsigned long),(> means big endian)
    enc_img1 = enc_img.tostring() #converting the encoded image array into bytes(struct) of the actual memory
    connection.sendall(buff) #sending the size of the frame(img)
    connection.sendall(enc_img1)#sending the actual img 


# A method to recieved a frame from either side of the connection
# connecion is the socket object of the connection from either side(receiving end)
def recv_frame(connection):
    msglen = recv_msg(connection,4,4)# sending the lenght of the enc
    msglen = unpack(">L", msglen)[0]#converting the size again into an unsigned Long 
    frame = recv_msg(connection,msglen,2048)# receiving the complete frame with packet maximum of 2.048 KB and with len of the received length 
    return frame,msglen # returning the frame as bytes and its length


# Converting the frame from bytes(struct) into array then decoding it 
def decode_frame(frame):
    frame = np.frombuffer(frame,dtype='uint8') # converting the frame into an array again  
    frame = cv2.imdecode(frame,1) # decoding the frame into raw img
    return frame #returning the decoded frame
