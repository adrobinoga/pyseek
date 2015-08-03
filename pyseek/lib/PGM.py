'''16 bit PGM read/write code'''

import numpy

class PGMError(Exception):
	'''PGMLink error class'''
	def __init__(self, msg):
            Exception.__init__(self, msg)

def PGM_read(filename):
    '''read a 8/16 bit PGM image, returning a numpy array'''
    f = open(filename, mode='rb')
    fmt = f.readline()
    if fmt.strip() != 'P5':
        raise PGMError('Expected P5 image in %s' % filename)
    dims = f.readline()
    dims = dims.split(' ')
    width = int(dims[0])
    height = int(dims[1])
    line = f.readline()
    if line[0] == '#':
        # discard comment
        line = f.readline()
    line = line.strip()
    if line == "65535":
        eightbit = False
    elif line == "255":
        eightbit = True
    else:
        raise PGMError('Expected 8/16 bit image image in %s - got %s' % (filename, line))
    if eightbit:
        rawdata = numpy.fromfile(f, dtype='uint8')
        rawdata = numpy.reshape(rawdata, (height,width))
    else:
        rawdata = numpy.fromfile(f, dtype='uint16')
        rawdata = rawdata.byteswap(True)
        rawdata = numpy.reshape(rawdata, (height, width))
    f.close()
    return rawdata.byteswap(True)


def PGM_write(filename, rawdata):
    '''write a 8/16 bit PGM image given a numpy array'''
    if rawdata.dtype == numpy.dtype('uint8'):
        numvalues = 255
    elif rawdata.dtype == numpy.dtype('uint16'):
        numvalues = 65535
    else:
        raise PGMError("Invalid array data type '%s'" % rawdata.dtype)
    shape = rawdata.shape
    if len(shape) != 2:
        raise PGMError("Invalid array shape '%s'" % shape)
    height = shape[0]
    width = shape[1]
    
    f = open(filename, mode='wb')
    f.write('''P5
%u %u
%u
''' % (width, height, numvalues))

    rawdata = rawdata.byteswap(True)
    rawdata = rawdata.tofile(f)
    f.close()

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    print("Reading %s" % filename)
    a = PGM_read(filename)

    filename = filename + ".test"
    print("Writing %s" % filename)
    PGM_write(filename, a)
