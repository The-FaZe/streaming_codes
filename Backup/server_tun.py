import socket
from time import sleep
import paramiko

print("start python code........")
shclient = paramiko.client.SSHClient()
sshclient.load_system_host_keys()
sshclient.set_missing_host_key_policy(paramiko.client.WarningPolicy())
transport=sshclient.connect(hostname="login01").get_transport()
port=transport.request_port_forward(ip='localhost',port=0)
print("port: ",port)
print ('starting up on localhost : {}'.format(port))
connection = transport.accept(None)
data = connection.recv(1024).decode('utf-8')
message = 'Have a nice day'
message = message.encode('utf-8')
print (data)
connection.sendall(message)
sleep(10)
connection.close()
