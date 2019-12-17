import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..', 'node_modules/ASPIRED'))

import json
import pickle
import numpy as np
from aspired import aspired
import warnings
warnings.filterwarnings("ignore")

# Echo server program
import socket

HOST = ''            # Symbolic name meaning all available interfaces
PORT = 54321              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
#print('Server started on localhost:50007')

while True:
    conn, addr = s.accept()
    #print('Connected by', addr)
    incoming = b''
    while True:
        block = conn.recv(65536)
        if not block:
            break
        incoming += block
    
    conn.close()

    incoming = pickle.loads(incoming)
    func = incoming[0]
    args = incoming[1]

    if func == "apIdentifyScience":

        position_min_science, position_max_science, Saxis_science, fittype_science, order_science, lines_science = args
        f_science = json.loads(lines_science)

        x_len_science = f_science['hdu']['naxis1']
        y_len_science = f_science['hdu']['naxis2']

        # reshape data
        img_science = np.fromiter(f_science['data'].values(), dtype=float).reshape((y_len_science, x_len_science))
        img_science[np.isnan(img_science)] = 0.

        spatial_mask_science = np.arange(position_min_science, position_max_science)

        # trace spectrum
        spectrum_science = aspired.TwoDSpec(img_science,
            Saxis=Saxis_science,
            spatial_mask=spatial_mask_science,
            n_spec=1,
            cr=True,
            silence=True
        )

        # Extract the spectrum
        spectrum_science.ap_trace_iraf(
            nsteps=20,
            fittype=fittype_science,
            order=order_science,
            bigbox=8,
            display=False
            )

        my_science = spectrum_science.trace[0]
        my_sigma_science = spectrum_science.trace_sigma[0][0]

        my_science = np.around(my_science, decimals=3)
        my_sigma_science = np.around(my_sigma_science, decimals=3)

        # format into a json
        json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')
        if Saxis_science == 1:
            my_json_ap_science = json.dumps([{"mu": my_science[i], "sig": my_sigma_science} for i in range(x_len_science)])
        else:
            my_json_ap_science = json.dumps([{"mu": my_science[i], "sig": my_sigma_science} for i in range(y_len_science)])

        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json_ap_science))
        conn.close()

    if func == "apIdentifyStandard":

        position_min_standard, position_max_standard, Saxis_standard, fittype_standard, order_standard, lines_standard = args
        f_standard = json.loads(lines_standard)

        x_len_standard = f_standard['hdu']['naxis1']
        y_len_standard = f_standard['hdu']['naxis2']

        # reshape data
        img_standard = np.fromiter(f_standard['data'].values(), dtype=float).reshape((y_len_standard, x_len_standard))
        img_standard[np.isnan(img_standard)] = 0.

        spatial_mask_standard = np.arange(position_min_standard, position_max_standard)

        # trace spectrum
        spectrum_standard = aspired.TwoDSpec(img_standard,
            Saxis=Saxis_standard,
            spatial_mask=spatial_mask_standard,
            n_spec=1,
            cr=True,
            silence=True
        )

        # Extract the spectrum
        spectrum_standard.ap_trace_iraf(
            nsteps=20,
            fittype=fittype_standard,
            order=order_standard,
            bigbox=8,
            display=False
            )

        my_standard = spectrum_standard.trace[0]
        my_sigma_standard = spectrum_standard.trace_sigma[0][0]

        my_standard = np.around(my_standard, decimals=3)
        my_sigma_standard = np.around(my_sigma_standard, decimals=3)

        # format into a json
        json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')
        if Saxis_standard == 1:
            my_json_ap_standard = json.dumps([{"mu": my_standard[i], "sig": my_sigma_standard} for i in range(x_len_standard)])
        else:
            my_json_ap_standard = json.dumps([{"mu": my_standard[i], "sig": my_sigma_standard} for i in range(y_len_standard)])

        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json_ap_standard))
        conn.close()

    if func == "apExtractScience":

        apwidth_science, skysep_science, skywidth_science, skydeg_science, optimal_science, crsigma_science, gain_science = args

        # extract spectrum
        if optimal_science == 'optimal':
            optimal_science = True
        else:
            optimal_science = False

        # Extract the spectrum
        my_json_spec_science = spectrum_science.ap_extract(
            apwidth=apwidth_science,
            skysep=skysep_science,
            skywidth=skywidth_science,
            skydeg=skydeg_science,
            optimal=optimal_science,
            display=True,
            verbose=True
            )

        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json_spec_science))
        conn.close()

        spectrum_science.ap_extract(
            apwidth=apwidth_science,
            skysep=skysep_science,
            skywidth=skywidth_science,
            skydeg=skydeg_science,
            optimal=optimal_science
            )

    if func == "apExtractStandard":

        apwidth_standard, skysep_standard, skywidth_standard, skydeg_standard, optimal_standard, crsigma_standard, gain_standard = args

        # extract spectrum
        if optimal_standard == 'optimal':
            optimal_standard = True
        else:
            optimal_standard = False

        # Extract the spectrum
        my_json_spec_standard = spectrum_standard.ap_extract(
            apwidth=apwidth_standard,
            skysep=skysep_standard,
            skywidth=skywidth_standard,
            skydeg=skydeg_standard,
            optimal=optimal_standard,
            display=True,
            verbose=True
            )

        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json_spec_standard))
        conn.close()

        spectrum_standard.ap_extract(
            apwidth=apwidth_standard,
            skysep=skysep_standard,
            skywidth=skywidth_standard,
            skydeg=skydeg_standard,
            optimal=optimal_standard
            )

    if func == "inspectStandard":

        target_name, group_name, ftype = args

        fluxcal = aspired.StandardFlux(
            target=target_name,
            group=group_name,
            ftype=ftype
        )
        fluxcal.load_standard()
        my_json_inspect_standard = fluxcal.inspect_standard(verbose=True)

        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json_inspect_standard))
        conn.close()

    if func == "waveCalibrate":
        pass
        '''
        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json_spec_standard))
        conn.close()
        '''

    if func == "fluxCalibrate":
        wavecal = type('', (), {})()
        wavecal.pfit_type = 'poly'
        wavecal.pfit = [6.79539614e-13, -1.55089700e-09,  6.97476117e-07,  8.00610791e-04,
        3.93644274e+00,  3.49811874e+03]

        science_reduced = aspired.OneDSpec(
            spectrum_science,
            wavecal,
            standard=spectrum_standard,
            wave_cal_std=wavecal,
            flux_cal=fluxcal
        )
        science_reduced.apply_wavelength_calibration('all')
        science_reduced.compute_sencurve(kind='cubic')
        my_json_inspect_sencurve = science_reduced.inspect_sencurve(verbose=True)

        science_reduced.apply_flux_calibration('all')
        my_json_science_reduced, my_json_standard_reduced = science_reduced.inspect_reduced_spectrum('all', verbose=True)

        my_json = json.dumps({"sense_curve": my_json_inspect_sencurve, "science_reduced": my_json_science_reduced, "standard_reduced": my_json_standard_reduced})

        # second back to client
        conn, addr = s.accept()
        conn.sendall(pickle.dumps(my_json))
        #conn.sendall(pickle.dumps([my_json_inspect_sencurve, my_json_science_reduced, my_json_standard_reduced]))
        conn.close()
