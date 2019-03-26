import os
import sys
import json
from astropy.io import fits
from aptrace import *

# Get data
filepath = sys.argv[1]
x_len = int(sys.argv[2])
y_len = int(sys.argv[3])
#print(filepath, flush=True)

data = json.load(open(filepath, "r"))
#print(data, flush=True)

img = np.zeros((y_len, x_len))

x = 0
y = 0
for key, value in data.items():
    img[y][x] = value
    x += 1
    if (x%x_len == 0):
        y += 1
        x = 0

img[np.isnan(img)] = 0.

#print(img, flush=True)

# Ignore 5 pixels on either side
trace = ap_trace(img, fmask=np.arange(y_len), nomessage=True)
spec = trace[0]
spec_json = json.dumps([ {i: j} for i, j in enumerate(spec)])

print(spec_json, flush=True)
