from astropy.io import fits
import cv2
import numpy as np
import matplotlib.pyplot as plt


# FITS FILES:
# FILE_PATH = 'data/double_double.fits'
# FILE_PATH = 'data/first_light.fits'
# FILE_PATH = 'data/polaris_plate.fits'
# FILE_PATH = 'data/vega_defocus_and_coma_corrected.fits'
# FILE_PATH = 'data/vega_defocus_corrected.fits'
FILE_PATH = 'data/ttmp240612.fits'


def main():
    print('main call.')
    hdul = fits.open(FILE_PATH)
    print(hdul.info())
    hdr = hdul[0].header
    print(repr(hdr))
    # exposure = hdr['EXPTIME']
    # object = hdr['OBJECT']
    # print(f'\nEXPOSURE: {exposure}')
    # print(f'OBJECT: {object}')
    data = hdul[0].data
    row = data[0]
    print(f'Row size: {row.shape}')
    print(f'Iterate over rows and find min value for each')
    list_min = []
    cnt = 0
    min_last = 50
    for i in range(0,1440):
        min = np.min(data[i])
        list_min.append(min)
        # cnt = (cnt + 1) if (min < min_last) else cnt
        cnt = (cnt + 1) if (min < 50) else cnt
        min_last = min
    print(list_min)
    print(np.min(list_min))
    print(cnt)

    hdul.close()



if __name__ == "__main__":
    main()