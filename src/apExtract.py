import sys
sys.path.append('ASPIRED')

import json
import numpy as np
from ASPIRED import twodspec

apwidth = int(float(sys.argv[1]))
Saxis = int(float(sys.argv[2]))
skysep = int(float(sys.argv[3]))
skywidth = int(float(sys.argv[4]))
skydeg = int(float(sys.argv[5]))
optimal = sys.argv[6]
cr_sigma = float(sys.argv[7])
gain = float(sys.argv[8])
rn = float(sys.argv[9])

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
if optimal == 'optimal':
    optimal = True
else:
    optimal = False
spec, sky, err = twodspec.ap_extract(
	img, mu, apwidth=apwidth, trace_sigma=sigma, Saxis=Saxis, skysep=skysep,
	skywidth=skywidth, skydeg=skydeg, optimal=optimal, cr_sigma=cr_sigma,
	gain=gain, rn=rn, silence=True, display=False
	)

# format into a json
json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')
if Saxis == 1:
    my_json = json.dumps([{i: {"spec": spec[i], "sky": sky[i], "err": err[i]}} for i in range(x_len)])
else:
    my_json = json.dumps([{i: {"spec": spec[i], "sky": sky[i], "err": err[i]}} for i in range(y_len)])

# stdout
print(my_json)
