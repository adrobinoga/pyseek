#!/usr/bin/env python

'''pyseek thermal camera library - viewer example'''

import Tkinter
import pyseek
from pyseek.lib.PGM import PGM_write
from PIL import ImageTk
import sys, os, time

def show_frame(seek, first=False):
    global fps_t, fps_f
    
    from scipy.misc import toimage

    arr = seek.get_array()
    disp_img = toimage(arr)
    
    if first:
        root.geometry('%dx%d' % (disp_img.size[0], disp_img.size[1]))
    tkpi = ImageTk.PhotoImage(disp_img)
    label_image.imgtk = tkpi
    label_image.configure(image=tkpi)
    label_image.place(x=0, y=0, width=disp_img.size[0], height=disp_img.size[1])
    
    now = int(time.time())
    fps_f += 1
    if fps_t == 0:
        fps_t = now
    elif fps_t < now:
        print '\rFPS: %.2f' % (1.0 * fps_f / (now-fps_t)),
        sys.stdout.flush()
        fps_t = now
        fps_f = 0

    label_image.after(1, show_frame, seek)    # after 1ms, run show_frame again


seek = pyseek.PySeek()
seek.open()
    
root = Tkinter.Tk()
root.title('Seek Thermal camera')
root.bind("<Escape>", lambda e: root.quit())

label_image = Tkinter.Label(root)
label_image.pack()

fps_t = 0
fps_f = 0

show_frame(seek, first=True)
root.mainloop() # UI has control until user presses <<Escape>>
