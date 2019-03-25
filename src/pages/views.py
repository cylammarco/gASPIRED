from django.shortcuts import render
from django.http import JsonResponse
import json
import os
import sys

from astropy.io import fits
from pages.aptrace import *

# Create your views here.
def index(request):
    print("Loading pages/index.html")
    print(request)
    return render(request, 'pages/index.html')

def aptrace(request):
    #print("POST received!")
    data = json.loads(request.body)
    
    x_len = data['header']['NAXIS1']
    y_len = data['header']['NAXIS2']
    img = np.zeros((y_len, x_len))

    x = 0
    y = 0
    for key, value in data['data'].items():
        img[y][x] = value
        x += 1
        if (x%x_len == 0):
            y += 1
            x = 0

    img[np.isnan(img)] = 0.

    #print(img, flush=True)

    # Ignore 5 pixels on either side
    trace = ap_trace(img, fmask=np.arange(212)[5:-5], nomessage=True)
    spec = trace[0]
    spec_json = [ {i: j} for i, j in enumerate(spec)]

    #print(spec_json, flush=True)

    #return HttpResponse(json.dumps(data))
    return JsonResponse(spec_json, safe=False)