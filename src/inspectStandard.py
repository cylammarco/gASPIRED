import sys
import socket
import pickle
import json

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 54321              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

target_name = sys.argv[1]
group_name = sys.argv[2]
ftype = sys.argv[3]

args = [target_name, group_name, ftype]
data = pickle.dumps(['inspectStandard', args])

s.sendall(data)
s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

incoming = b''
while True:
    block = s.recv(65536)
    if not block:
        break
    incoming += block

s.close()
# stdout
print(pickle.loads(incoming))
