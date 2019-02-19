import os
import sys
import json
import numpy as np
from astropy.io import fits

# Set HDU index 
i = 0

# Get working directory path
dir_path = os.path.dirname(os.path.realpath(__file__))
#print(os.path.join(dir_path, 'FITS_example/example.fits'))

# Open FITS file, using the supplied HDU index
fitsfile = fits.open(os.path.join(dir_path, 'FITS_example/example.fits'))[i]

# Load header and data
header = fitsfile.header
image = np.ndarray.tolist(fitsfile.data)

output = {
    "NAXIS1": header['NAXIS1'],
    "NAXIS2": header['NAXIS2'],
    "data": image
    }

print(json.dumps(output), flush=True)
sys.stdout.close()

