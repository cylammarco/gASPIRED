import sys
import socket
import pickle
import json

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 54321              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

obstype = sys.argv[1]
apwidth = int(float(sys.argv[2]))
skysep = int(float(sys.argv[3]))
skywidth = int(float(sys.argv[4]))
skydeg = int(float(sys.argv[5]))
optimal = sys.argv[6]
crsigma = float(sys.argv[7])
gain = float(sys.argv[8])

if obstype == "ScienceJS9":
    obs = "apExtractScience"
elif obstype == "StandardJS9":
    obs = "apExtractStandard"
else:
    raise ValueError("Unknown obstype \'" + obstype + "\'")

args = [apwidth, skysep, skywidth, skydeg, optimal, crsigma, gain]
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
