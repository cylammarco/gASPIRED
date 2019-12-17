import sys
import socket
import pickle
import json

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 54321              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

obstype = sys.argv[1]
position_min = int(float(sys.argv[2]))
position_max = int(float(sys.argv[3]))
Saxis = int(float(sys.argv[4]))
fittype = sys.argv[5]
order = int(float(sys.argv[6]))

lines = sys.stdin.readlines()[0]

if obstype == "ScienceJS9":
    obs = "apIdentifyScience"
elif obstype == "StandardJS9":
    obs = "apIdentifyStandard"
else:
    raise ValueError("Unknown obstype \'" + obstype + "\'")

args = [position_min, position_max, Saxis, fittype, order, lines]
data = pickle.dumps([obs, args])

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
