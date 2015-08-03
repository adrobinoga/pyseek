#!/usr/bin/env python

'''pyseek thermal camera library - capture example'''

import pyseek
from pyseek.lib.PGM import PGM_write

seek = pyseek.PySeek()
seek.open()
for i in range(100):
    img = seek.get_array()
    PGM_write('seek-%u.pgm' % i, img)
