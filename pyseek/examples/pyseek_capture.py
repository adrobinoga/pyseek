#!/usr/bin/env python

'''pyseek thermal camera library - capture example'''

import pyseek
from pyseek.lib.PGM import PGM_write
from pyseek.lib.heatmap import thermal_map

seek = pyseek.PySeek()
seek.open()
for i in range(100):
    img = seek.get_array()
    colour = thermal_map(img)

    filename = 'seek-%u.pgm' % i
    PGM_write(filename, img)
    print("Saved %s" % filename)
    
    filename = 'seek-%u.png' % i
    colour.save(filename)
    print("Saved colour %s" % filename)
