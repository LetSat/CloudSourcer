#!/usr/bin/env python2

import wget, cv2, sys, os
import CloudSourcer
from subprocess import call

MONTH = 1
DAY_ST = 1
DAY_END = 31

huginBatches = (
       0,
     600,
    1500,
    1800
)

for time in huginBatches:
    dayList = []
    for day in range(DAY_ST, DAY_END + 1):
        panoSrc = "RawPanos/%s_%s_%s.tif" % (time, MONTH, day)
        if os.path.exists(panoSrc):
            print "Use %s" % panoSrc
            dayList.append(panoSrc)
        else:
            print "Skip %s" % panoSrc
            
    filterFile = "FilteredPanos/filter_%s_%s.tif" % (time, MONTH)
    cs = CloudSourcer.Filter(1, filterFile)
    
    if os.path.exists(filterFile):
        print "Use filter %s" % filterFile
        cs.loadFromFile()
    else:
        print "Building filter %s" % filterFile
        cs.build(dayList)
        
    for day in range(DAY_ST, DAY_END + 1):
        panoSrc = "RawPanos/%s_%s_%s.tif" % (time, MONTH, day)
        filteredPano = "FilteredPanos/%s_%s_%s.tif" % (time, MONTH, day)
        if os.path.exists(panoSrc):
            print "Use %s" % panoSrc
            filteredImg = cs.getFilteredPano(panoSrc, True)
            cv2.imwrite(filteredPano, filteredImg)
            print "Exported %s " % filteredPano
        else:
            print "Skip %s" % filteredPano
        
    
            
