# CloudSourcer: Filter unwanted data from geostationary
#               satellite data from http://www.sat.dundee.ac.uk
# v1.0
# Intended for use in POVRay-Renderer
# 24 Feb 2018 - Initial Implementation v1.0
# 25 Feb 2018 - Revised for use in panorama generation v1.1
# 25 Feb 2018 - Restructured v1.1
# Chandler Griscom

import cv2
import numpy as np

import wget
import sys, os, math, random
    
# Define satellite parameters: URL Code, 
#                              Width, Height
SATELLITE_140_7E_MTSAT = \
            ('http://%s:%s@www.sat.dundee.ac.uk/xrit/140.7E/MTSAT/%s/%s/%s/%s/%s_%s_%s_%s_MTSAT3_3_S1.jpeg', \
             5500, 5500)
    
SATELLITE_57E_MET = \
            ('http://%s:%s@www.sat.dundee.ac.uk/xrit/057.0E/MET/%s/%s/%s/%s/%s_%s_%s_%s_MET7_1_S1.jpeg', \
             5032, 5000)
    
SATELLITE_0E_MSG = \
            ('http://%s:%s@www.sat.dundee.ac.uk/xrit/000.0E/MSG/%s/%s/%s/%s/%s_%s_%s_%s_MSG3_1_S1.jpeg', \
             3712, 3712)

SATELLITE_75W_GOES_E = \
            ('http://%s:%s@www.sat.dundee.ac.uk/xrit/075.0W/GOES/%s/%s/%s/%s/%s_%s_%s_%s_GOES13_1_S1.jpeg', \
             2816, 3248)

SATELLITE_135W_GOES_W = \
            ('http://%s:%s@www.sat.dundee.ac.uk/xrit/135.0W/GOES/%s/%s/%s/%s/%s_%s_%s_%s_GOES15_1_S1.jpeg', \
             2816, 3248)

class FreeServer:
    
    def __init__(self, username, password, satelliteID):
        self.username = username
        self.password = password
        self.satelliteID = satelliteID
    
    def getImage(self, year, month, day, time):
        url = self.__getURLFromID(year, month, day, time)
        filename = wget.download(url)

        img = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2GRAY) 
        os.remove(filename)

        return img
    
    def __readImage(self, filename):
        return cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2GRAY)
    
    def __getURLFromID(self, yr, month, day, time):
        return self.satelliteID[0] % (self.username, self.password, yr, month, day, time, yr, month, day, time)
    
    def width(self):
        return self.satelliteID[1]
    
    def height(self):
        return self.satelliteID[2]
    


class Filter:
    
    def __init__(self, multFactor, filename):
        self.filename = filename
        self.multFactor = multFactor
        
    def build(self, panoFiles, debug=True):
        
        if debug:
            sys.stdout.write('[')
            sys.stdout.flush()
        
        img_gray = self.__readImage(panoFiles[0])

        last1 = img_gray
        last2 = img_gray
        last3 = img_gray

        (height, width) = img_gray.shape

        ones = np.zeros((height,width), np.uint32)
        ones[:,:] = 1

        average = np.zeros((height,width), np.uint32)
        average_img = np.zeros((height,width), np.uint8)

        casesTaken = 0

        random.shuffle(panoFiles)
        
        for pano in panoFiles:
            
            if not os.path.exists(pano):
                if debug:
                    sys.stdout.write('x')
                    sys.stdout.flush()
                continue
            elif os.path.getsize(pano) < 20000:
                if debug:
                    sys.stdout.write('x')
                    sys.stdout.flush()
                continue
            else:
                if debug:
                    sys.stdout.write('.')
                    sys.stdout.flush()
            
            img_gray = self.__readImage(pano)
            cv2.blur(img_gray,(5,5))
            
            if casesTaken >= 3:
                np.add(average, (ones*img_gray*last1*last2*last3)**.25, out=average, casting="unsafe")
            
            casesTaken += 1
            last3 = last2
            last2 = last1
            last1 = img_gray
        
        np.add(average_img, average / (casesTaken-3), out=average_img, casting="unsafe")
        
        self.average_img = (average_img*(self.multFactor)).astype(np.uint8)
        cv2.imwrite(self.filename, self.average_img)
        
        if debug:
            sys.stdout.write(']')
            sys.stdout.flush()
            
        return self.average_img
        
    def loadFromFile(self):
        self.average_img = cv2.cvtColor(cv2.imread(self.filename), cv2.COLOR_BGR2GRAY)
        return self.average_img
    
    def getFilteredPano(self, imageFile, clahe):
        img_gray = self.__readImage(imageFile)
        
        img_corr = cv2.subtract(img_gray, self.average_img);
        
        if clahe:
            clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(200, 200))
            return clahe.apply(img_corr)
        else:
            return img_corr
    
    def __readImage(self, filename):
        img = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2GRAY) 
        return img
    
    
