import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..', 'node_modules/ASPIRED'))

import json
import numpy as np
from aspired import standard

target = sys.argv[1]
source = sys.argv[2]
exp_time = float(sys.argv[3])

lines = sys.stdin.readlines()[0]
data = json.loads(lines)

spec_std = data['spec_std']
wave_std = data['wave_std']
spec_sci = data['spec_sci']
wave_sci = data['wave_sci']

senscurve = standard.get_sencurve(wave_std, spec_std, target, source, exp_time)
sensitivity = senscurve(wave_sci)
calibrated_spec = spec_sci * sensitivity * 1e16

# format into a json
json.encoder.FLOAT_REPR = lambda o: format(o, '.6f')
my_json = json.dumps([{"sensitivity": sensitivity[i], "calibrated_spec": calibrated_spec[i]} for i in range(len(wave_sci))])

# stdout
print(my_json)
