import socket
from time import sleep
import paramiko
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip ="localhost"
server_address = (ip,6666)
sshclient = paramiko.client.SSHClient()
sshclient.load_system_host_keys()
sshclient.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
sshclient.connect(hostname="login01.c2.hpc.bibalex.org",username="alex039u4",passphrase="Kaiki is the best grill even in monogatori fagoteri"
	,key_filename=r"C:\Users\PlebChan\AppData\Roaming\SPB_16.6\.ssh\id_rsa")
client = sshclient.get_transport().open_channel(kind='direct-tcpip',src_addr=('localhost',6666),dest_addr=server_address)
message = 'Hi from the client'
message = message.encode('utf-8')
client.send(message)
data = client.recv(1024).decode('utf-8')
print (data)
client.close()
