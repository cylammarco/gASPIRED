import sys
sys.path.append('ASPIRED')

import json
import numpy as np
from ASPIRED import twodspec

position_min = int(float(sys.argv[1]))
position_max = int(float(sys.argv[2]))
Saxis = int(float(sys.argv[3]))
fittype = sys.argv[4]
order = int(float(sys.argv[5]))
lines = sys.stdin.readlines()[0]
f = json.loads(lines)

x_len = f['hdu']['naxis1']
y_len = f['hdu']['naxis2']

# reshape data
img = np.fromiter(f['data'].values(), dtype=float).reshape((y_len, x_len))
img[np.isnan(img)] = 0.

spatial_mask = np.arange(position_min, position_max)

# trace spectrum
my, my_sigma = twodspec.ap_trace(
    img, nsteps=20, spatial_mask=spatial_mask, cosmic=True, n_spec=1, recenter=False, prevtrace=(0, ), 
    fittype=fittype, order=order, bigbox=8, Saxis=Saxis, silence=True, display=False
    )

my = np.around(my, decimals=3)
my_sigma = np.around(my_sigma, decimals=3)

# format into a json
json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')
if Saxis == 1:
    my_json = json.dumps([{i: {"mu": my[0][i], "sig": my_sigma[0][i]}} for i in range(x_len)])
else:
    my_json = json.dumps([{i: {"mu": my[0][i], "sig": my_sigma[0][i]}} for i in range(y_len)])

# stdout
print(my_json)
