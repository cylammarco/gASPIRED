import sys
sys.path.append('ASPIRED')

import json
import numpy as np
from ASPIRED import twodspec


lines = sys.stdin.readlines()[0]
data = json.loads(lines)

f = data['spectrum']
trace = data['myTrace']

mu = np.array([j[str(i)]['mu'] for i, j in enumerate(trace)])
sigma = np.array([j[str(i)]['sig'] for i, j in enumerate(trace)])

x_len = f['hdu']['naxis1']
y_len = f['hdu']['naxis2']

# reshape data
img = np.fromiter(f['data'].values(), dtype=float).reshape((y_len, x_len))
img[np.isnan(img)] = 0.

# extract spectrum
spec, sky, err = twodspec.ap_extract(img, mu, sigma)

# format into a json
json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')
my_json = json.dumps([{i: {"spec": spec[i], "sky": sky[i], "err": err[i]}} for i in range(x_len)])

# stdout
print(my_json)
