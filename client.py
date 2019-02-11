import socket
from time import sleep
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.1.112',32792)
client.connect(server_address)
message = 'Hi from the client'
message = message.encode('utf-8')
client.send(message)
data = client.recv(1024).decode('utf-8')
print (data)
sleep(10)
client.close()
