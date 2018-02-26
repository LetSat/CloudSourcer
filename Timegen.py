#!/usr/bin/env python2

import wget, cv2, sys, os
import CloudSourcer
from subprocess import call

USERNAME = 'cjgriscom'
PASSWORD = 'dbg392'

MONTH = 1
DAY_ST = 1
DAY_END = 31

servers = {
    '140.7E': (frozenset({0, 600}),     CloudSourcer.SATELLITE_140_7E_MTSAT), \
    '57E':    (frozenset({600}),        CloudSourcer.SATELLITE_57E_MET), \
    '0E':     (frozenset({600, 1500}),  CloudSourcer.SATELLITE_0E_MSG), \
    '75W':    (frozenset({1500, 1800}), CloudSourcer.SATELLITE_75W_GOES_E), \
    '135W':   (frozenset({0, 1800}),    CloudSourcer.SATELLITE_135W_GOES_W)
}

huginBatches = (
    (   0, ('135W',   '140.7E'  )),
    ( 600, ('140.7E', '57E',    '0E')),
    (1500, ('0E',     '75W'     )),
    (1800, ('75W',    '135W'    ))
)

for (time, satellites) in huginBatches:
    
    for day in range(DAY_ST, DAY_END + 1):
        panoSrc = "RawPanos/%s_%s_%s.tif" % (time, MONTH, day)
        if os.path.exists(panoSrc):
            print "\nSkip %s" % panoSrc
        else:
            try:
                for s in satellites:
                    f = CloudSourcer.FreeServer(USERNAME,PASSWORD, servers[s][1])
                    img = f.getImage(2016, MONTH, day, time)
                    mercyOne = "Sources/%s_%s.png" % (s, time)
                    cv2.imwrite(mercyOne, img)
                    print ""
                    print "Exported pano source: " + mercyOne
                    
                call(["hugin_executor", "--threads=5", "--stitching", "--prefix=%s" % panoSrc, "Time%s.pto" % time])
                print "\nCompleted %s" % panoSrc
            except:
                print "\nFailed %s" % panoSrc
            
