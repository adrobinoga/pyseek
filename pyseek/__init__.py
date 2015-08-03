'''pyseek thermal camera library'''

'''
 This is based on pyseek by Fry-kun, which has these credits:
 
 "Many thanks to the folks at eevblog, especially (in no particular order) 
   miguelvp, marshallh, mikeselectricstuff, sgstair and many others
     for the inspiration to figure this out"

'''

import usb.core
import usb.util
from PIL import Image
from scipy.misc import toimage
import numpy, sys

class PySeekError(IOError):
    '''pyseek thermal camera error'''
    pass

class PySeek:
    '''pyseek thermal camera control'''

    def __init__(self):
        self.calibration = None
        self.dev = None
        self.debug = False

    def send_msg(self, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        '''send a message to the camera'''
        ret = self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout)
        if ret != len(data_or_wLength):
            raise PySeekError()

    def receive_msg(self, bRequest, wValue, wIndex, data_or_wLength):
        '''receive a message from camera'''
        return self.dev.ctrl_transfer(0xC1, bRequest, wValue, wIndex, data_or_wLength)

    def deinit(self):
        '''Deinit the device'''
        msg = '\x00\x00'
        for i in range(3):
            self.send_msg(0x41, 0x3C, 0, 0, msg)

    def open(self):
        '''find and open the camera. Raise PySeekError on error'''
        # find our Seek Thermal device  289d:0010
        self.dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)
        if not self.dev:
            raise PySeekError()

        # set the active configuration. With no arguments, the first configuration will be the active one
        self.dev.set_configuration()

        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]

        custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        ep = usb.util.find_descriptor(intf, custom_match=custom_match)   # match the first OUT endpoint
        assert ep is not None

        # Setup device
        try:
            msg = '\x01'
            self.send_msg(0x41, 0x54, 0, 0, msg)
        except Exception as e:
            self.deinit()
            msg = '\x01'
            self.send_msg(0x41, 0x54, 0, 0, msg)

        #  Some day we will figure out what all this init stuff is and
        #  what the returned values mean.
        self.send_msg(0x41, 0x3C, 0, 0, '\x00\x00')
        ret1 = self.receive_msg(0x4E, 0, 0, 4)
        ret2 = self.receive_msg(0x36, 0, 0, 12)

        self.send_msg(0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')
        ret3 = self.receive_msg(0x58, 0, 0, 0x40)

        self.send_msg(0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')
        ret4 = self.receive_msg(0x58, 0, 0, 0x40)

        self.send_msg(0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')
        ret5 = self.receive_msg(0x58, 0, 0, 0x18)

        self.send_msg(0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')
        ret6 = self.receive_msg(0x58, 0, 0, 0x0C)

        self.send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
        ret7 = self.receive_msg(0x3D, 0, 0, 2)

        self.send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
        self.send_msg(0x41, 0x3C, 0, 0, '\x01\x00')
        ret8 = self.receive_msg(0x3D, 0, 0, 2)

    def cal_ok(self, x, y):
        value = self.calibration[x][y]
        return value != 0 and value < 15000

    def get_array(self):
        '''return next image from the camera as a numpy array. Raise PySeekError on error'''
        tries = 100
        while tries:
            tries -= 1
            # Send read frame request
            self.send_msg(0x41, 0x53, 0, 0, '\xC0\x7E\x00\x00')
            try:
                ret9  = self.dev.read(0x81, 0x3F60, 1000)
                ret9 += self.dev.read(0x81, 0x3F60, 1000)
                ret9 += self.dev.read(0x81, 0x3F60, 1000)
                ret9 += self.dev.read(0x81, 0x3F60, 1000)
            except usb.USBError as e:
                raise PySeekError()

            #  Let's see what type of frame it is
            #  1 is a Normal frame, 3 is a Calibration frame
            #  6 may be a pre-calibration frame
            #  5, 10 other... who knows.
            status = ret9[20]
            if self.debug:
                print ('%5d'*21 ) % tuple([ret9[x] for x in range(21)])
                print(status, len(ret9))

            if status == 1:
                #  Convert the raw calibration data to a string array
                calimg = Image.fromstring("I", (208,156), ret9, "raw", "I;16")

                #  Convert the string array to an unsigned numpy int16 array
                im2arr = numpy.asarray(calimg)
                self.calibration = im2arr.astype('uint16')

            if status == 3 and self.calibration is not None:
                #  Convert the raw image data to a string array
                img = Image.fromstring("I", (208,156), ret9, "raw", "I;16")

                #  Convert the string array to an unsigned numpy int16 array
                im1arr = numpy.asarray(img)
                im1arrF = im1arr.astype('uint16')

                if self.debug:
                    #  Subtract the calibration array from the image array and add an offset
                    print("Calibration:")
                    for x in range(30):
                        for y in range(10):
                            sys.stdout.write("%4u " % self.calibration[x][y])
                        print("")
                    print("Data:")
                    for x in range(30):
                        for y in range(10):
                            sys.stdout.write("%4u " % im1arrF[x][y])
                        print("")
                    

                ret = (im1arrF-self.calibration) + 800

                # for some strange reason there are blank lines and
                # gaps. This is a rough attempt to fill those in.
                # it still leaves some speckling
                for x in range(156):
                    for y in range(208):
                        if not self.cal_ok(x,y):
                            if x > 0 and self.cal_ok(x-1,y):
                                ret[x][y] = ret[x-1][y]
                            elif x < 155 and self.cal_ok(x+1,y):
                                ret[x][y] = ret[x+1][y]
                            elif y > 0 and self.cal_ok(x,y-1):
                                ret[x][y] = ret[x][y-1]
                            elif y < 207 and self.cal_ok(x,y+1):
                                ret[x][y] = ret[x][y+1]

                return ret

        raise PySeekError()

    def get_image(self):
        '''return next image from the camera as a scipy image. Raise PySeekError on error'''
        a = self.get_array()
        return toimage(a)

