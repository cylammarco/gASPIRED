from functools import partial

import numpy as np
from scipy import signal
from scipy import interpolate as itp
from scipy.optimize import curve_fit
from astropy.io import fits
from matplotlib import pyplot as plt
try:
    from astroscrappy import detect_cosmics
except:
    warn(AstropyWarning(
        'astroscrappy is not present, so ap_trace will clean ' +
        'cosmic rays with a 2D-median filter of size 5.'
        ))
    detect_cosmics = partial(signal.medfilt2d, kernel_size=5)

try:
    from matplotlib import pyplot as plt
except:
    warn(AstropyWarning(
        'matplotlib is not present, diagnostic plots cannot be generated.'
        ))


def _gaus(x, a, b, x0, sigma):
    """
    Simple Gaussian function, for internal use only
    Parameters
    ----------
    x : float or 1-d numpy array
        The data to evaluate the Gaussian over
    a : float
        the amplitude
    b : float
        the constant offset
    x0 : float
        the center of the Gaussian
    sigma : float
        the width of the Gaussian

    Returns
    -------
    Array or float of same type as input (x).
    """

    return a * np.exp(-(x - x0)**2 / (2 * sigma**2)) + b


def _find_peaks(img, Saxis, Waxis, f_height, display=False):
    """
    Identify peaks assuming the spatial and spectral directions are
    aligned with the X and Y direction within a few degrees.
    ----------
    img : 2-d numpy array
        The data to evaluate the Gaussian over
    Saxis : int
        Set which axis the spatial dimension is along. 1 = Y axis, 0 = X.
        (Default is 1)
    Waxis : int
        The perpendicular axis of Saxis
    f_height : float
        The minimum intensity as a fraction of maximum height
    
    Returns
    -------
    peaks_y :
        Array or float of the pixel values of the detected peaks
    heights_y :
        Array or float of the integrated counts at the peaks 
    """
    
    # get the length in the spectral and spatial directions
    spec_size = np.shape(img)[Waxis]
    spatial_size = np.shape(img)[Saxis]

    # the valid y-range of the chip (an array of int)
    ydata = np.arange(spec_size)
    ztot = np.sum(img, axis=Saxis)

    # get the height thershold
    height = max(ztot) * f_height

    # identify peaks 
    peaks_y, heights_y = signal.find_peaks(ztot, height=height)
    heights_y = heights_y['peak_heights']

    # display disgnostic plot
    if display:
        # set a side-by-side subplot
        fig, (ax0, ax1) = plt.subplots(ncols=2, sharey=True, figsize=(10,10))
        fig.tight_layout()
        plt.subplots_adjust(bottom=0.08, wspace=0)

        # show the image on the left
        ax0.imshow(
            np.log10(img),
            origin='lower',
            interpolation="nearest",
            aspect='auto'
            )
        ax0.set_xlim(0, spatial_size)
        ax0.set_ylim(0, spec_size)
        ax0.set_xlabel('Spectral Direction / pixel')
        ax0.set_ylabel('Spatial Direction / pixel')

        # plot the integrated count and the detected peaks on the right
        ax1.plot(ztot, ydata)
        ax1.scatter(heights_y, ydata[peaks_y])
        ax1.set_xlim(min(ztot[ztot>0]),max(ztot))
        ax1.set_ylim(0, len(ztot))
        ax1.set_xlabel('Integrated Count')
        ax1.set_xscale('log')
        plt.show()
    
    return peaks_y, heights_y


def ap_trace(img, nsteps=20, fmask=(1, ), cosmic=True, n_spec=1,
             recenter=False, prevtrace=(0, ), bigbox=15, Saxis=1,
             nomessage=False):
    """
    Trace the spectrum aperture in an image
    Assumes wavelength axis is along the X, spatial axis along the Y.
    Chops image up in bins along the wavelength direction, fits a Gaussian
    within each bin to determine the spatial center of the trace. Finally,
    draws a cubic spline through the bins to up-sample the trace.
    Parameters
    ----------
    img : 2d numpy array
        This is the image, stored as a normal numpy array. Can be read in
        using astropy.io.fits like so:
        >>> hdu = fits.open('file.fits')  # doctest: +SKIP
        >>> img = hdu[0].data  # doctest: +SKIP
    nsteps : int, optional
        Keyword, number of bins in X direction to chop image into. Use
        fewer bins if ap_trace is having difficulty, such as with faint
        targets (default is 20, minimum is 4)
    fmask : array-like, optional
        A list of illuminated rows in the spatial direction (Y), as
        returned by flatcombine.
    recenter : bool, optional
        Set to True to use previous trace, but allow small shift in
        position. Currently only allows linear shift (Default is False)
    bigbox : float, optional
        The number of sigma away from the main aperture to allow to trace
    Saxis : int, optional
        Set which axis the spatial dimension is along. 1 = Y axis, 0 = X.
        (Default is 1)

    Returns
    -------
    my : array
        The spatial (Y) positions of the trace, interpolated over the
        entire wavelength (X) axis
    """

    # define the wavelength axis
    Waxis = 0
    # add a switch in case the spatial/wavelength axis is swapped
    if Saxis is 0:
        Waxis = 1
    if not nomessage:
        print('Tracing Aperture using nsteps=' + str(nsteps))

    # the valid y-range of the chip
    if (len(fmask) > 1):
        ydata = np.arange(np.shape(img)[Waxis])[fmask]
    else:
        ydata = np.arange(np.shape(img)[Waxis])

    # need at least 4 samples along the trace. sometimes can get away with very few
    if (nsteps < 4):
        nsteps = 4

    # clean cosmic rays
    if cosmic:
        img = detect_cosmics(img)

    peak_guess, peak_guess_height = _find_peaks(img, Saxis, Waxis, f_height, display=False)
    # Pick the brightest source on slit
    if brightest:
        ztot = np.sum(img, axis=Saxis)[ydata]
        yi = np.arange(np.shape(img)[Waxis])[ydata]
        peak_y = yi[np.nanargmax(ztot)]
        peak_guess = [np.nanmax(ztot), np.nanmedian(ztot), peak_y, 2.]

    # use middle of previous trace as starting guess
    if (recenter is True) and (len(prevtrace) > 10):
        peak_guess[2] = np.nanmedian(prevtrace)

    # fit a Gaussian to peak
    popt_tot, pcov = curve_fit(
        _gaus, yi[np.isfinite(ztot)], ztot[np.isfinite(ztot)], p0=peak_guess)

    # only allow data within a box around this peak
    ydata2 = ydata[np.where((ydata >= popt_tot[2] - popt_tot[3] * bigbox) &
                            (ydata <= popt_tot[2] + popt_tot[3] * bigbox))]
    yi = np.arange(np.shape(img)[Waxis])[ydata2]

    # define the X-bin edges
    xbins = np.linspace(0, np.shape(img)[Saxis], nsteps)
    ybins = np.zeros_like(xbins)
    ybins_sigma = np.zeros_like(xbins)
    for i in range(0, len(xbins) - 1):
        # fit gaussian w/i each window
        if Saxis is 1:
            zi = np.sum(
                img[ydata2,
                    int(np.floor(xbins[i])):int(np.ceil(xbins[i + 1]))],
                axis=Saxis)
        else:
            zi = np.sum(
                img[int(np.floor(xbins[i])):int(np.ceil(xbins[i +
                                                              1])), ydata2],
                axis=Saxis)
        pguess = [np.nanmax(zi), np.nanmedian(zi), yi[np.nanargmax(zi)], 2.]
        popt, pcov = curve_fit(_gaus, yi, zi, p0=pguess)
        # if gaussian fits off chip, then use chip-integrated answer
        if (popt[2] <= min(ydata) + 25) or (popt[2] >= max(ydata) - 25):
            ybins[i] = popt_tot[2]
            popt = popt_tot
        else:
            ybins[i] = popt[2]
            ybins_sigma[i] = popt[3]

    # recenter the bin positions, trim the unused bin off in Y
    mxbins = (xbins[:-1] + xbins[1:]) / 2.
    mybins = ybins[:-1]

    # run a cubic spline thru the bins
    ap_spl = itp.UnivariateSpline(mxbins, mybins, ext=0, k=3, s=0)

    # interpolate the spline to 1 position per column
    mx = np.arange(0, np.shape(img)[Saxis])
    my = ap_spl(mx)

    if not nomessage:
        print("> Trace gaussian width = " + str(popt_tot[3]) + ' pixels')

    return my, ybins_sigma
