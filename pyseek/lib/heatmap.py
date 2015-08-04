'''map a greyscale thermal image to a color heatmap'''

import numpy, PIL

def thermal_map(rawimage, green_threshold=0.4, blue_threshold=0.75, clip_high=None, clip_low=None):
    '''take a greyscale thermal image and return a colour heatmap'''

    (width,height) = rawimage.shape
    minv = numpy.amin(rawimage)
    maxv = numpy.amax(rawimage)

    if clip_high is None:
        clip_high = maxv

    # remove the bottom part of the range to reduce noise
    if clip_low is None:
        clip_low = minv + (clip_high-minv)/20.0

    # create blank RGB image
    rgb = numpy.empty((width,height,3), dtype=numpy.uint8)

    # clip input to range
    clipped = numpy.clip(rawimage, clip_low, clip_high)

    # scale to 0..1
    scaled = (clipped - clip_low) / (clip_high - clip_low)

    # red component linear with input
    r = scaled

    # green as triangle function about green_threshold
    g = numpy.where((scaled>green_threshold), 1.0 - (scaled - green_threshold)/(1.0-green_threshold), 0)
    g += numpy.where((scaled<=green_threshold), 1.0 - (green_threshold-scaled)/green_threshold, 0)

    # blue as triangle function about blue_threshold
    b = numpy.where((scaled>blue_threshold), 1.0 - (scaled - blue_threshold)/(1.0-blue_threshold), 0)
    b += numpy.where((scaled<=blue_threshold), 1.0 - (blue_threshold-scaled)/blue_threshold, 0)

    # fill in RGB array
    rgb[...,0] = r*255
    rgb[...,1] = g*255
    rgb[...,2] = b*255

    ret = PIL.Image.fromarray(rgb, 'RGB')
    return ret
