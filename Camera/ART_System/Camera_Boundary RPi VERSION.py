################################################## from sh import gphoto2 as gp
from matplotlib.image import imread
from PIL import Image
import numpy as np
import signal
import os
import subprocess


class Camera:

    def __init__(self): \
        ##################################################
        # # gphoto2 will auto start up when the camera is connected
        # # (we want to kill this as only 1 program can interact with the DSLR at a time)
        # p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        # out, err = p.communicate()
        # # Search for the line that has what we want to kill
        # for line in out.splitlines():
        #     if b'gvfsd-gphoto2' in line:
        #         pid = int(line.split(None,1)[0])
        #         os.kill(pid, signal.SIGKILL)
        ##################################################
                
        ################################################## print(gp(['--auto-detect']))


        [self.h, self.w, self.colors] = [2,3,3]

        # arbitrary number for now
        self.threshold = 500
        # we will analyse every few pixels for speed (then look at the others, if that main pixel is valid) here the main pixel is every X pixels
        self.pxlGrid = 21  # Note: has to be an odd number
        self.light = np.zeros((2, 3), dtype=np.bool)
        self.coords = []
        self.blockCoords = []
        self.edges = []


    def getPosition(self):
        self.takeFullResPhoto()
        self.processImage()

    def takeFullResPhoto(self):
        print('taking photo..')
        # deletes any current files
        # files = os.listdir('/home/pi/Desktop/ART_System/Images/Full_Res')
        # for f in files:
        #     os.remove('/home/pi/Desktop/ART_System/Images/Full_Res/' + f)

        # set save location & inImage type
        os.chdir('C:/Users/Matthew/Documents/School/Year 4/SYSC 3010/Project/Camera/ART_System/Images/Full_Res')
        # (0=fineQualityJPG, which is equivilent to 11 or 12 when exporting in photoshop)
        ################################################## gp(['--set-config', '/main/imgsettings/imageformat=0'])

        # takes image
        ################################################# try:
            #################################################gp(['--capture-image-and-download'])
            # , '--force-overwrite']) # overwrite is needed sometimes for consistentcy?
        #################################################except:
        #################################################    print('ERROR: couldn\'t take photo')

        # sometime it is called the wrong name/does load/doesn't delete
        # (because gphoto/camera's dont always send the proper bits on time, so these next lines compensates for it)
        # only ok, if 1 file in library
        files = os.listdir(
            'C:/Users/Matthew/Documents/School/Year 4/SYSC 3010/Project/Camera/ART_System/Images/Full_Res')
        if len(files) > 2:
            print('ERROR: too many files') #################################################
        #else:
        try:
            print('reading in image..')
            self.inImage = imread('001.jpg')
            ################################################# self.inImage = imread('/home/pi/Desktop/ART_System/Images/Full_Res/' + files[0])
        except:
            print('ERROR: couldn\'t open image')

        # NEED TO ADD IN FAIL CASES
        # worst case senario -> ask user to confirm good image every time
        #                    -> might want to add in tether mode if so
   
   
   
    def processImage(self):
        print('processing image..')
        # important to remember it is y,x NOT x,y (h,w NOT w,h)
        # (i have kept it this way in this class, for saving img purposes)
        [self.h, self.w, self.colors] = self.inImage.shape
        self.light = np.zeros((self.h, self.w), dtype=np.bool)

        # We will look at every X number to speed things up,
        # but must remember to look at the other pixels & REMEMBER FAIL CASES!
        # (if the last pixel analysed near the X is bad then still look at the ones near it)
        for x in np.arange(self.pxlGrid,self.w-self.pxlGrid, self.pxlGrid):
            for y in np.arange(self.pxlGrid,self.h-self.pxlGrid, self.pxlGrid):
                if int(np.sum(self.inImage[y,x,:])) > self.threshold: # if the pixel's brightness is above the threshold

                    if [y, x] not in self.blockCoords:
                        self.blockCoords.append([y, x])
                        # if we have NOT already looked at it, then
                        # we will analyse the block around it
                        for xx in range(x - ((self.pxlGrid - 1) // 2), x + ((self.pxlGrid - 1) // 2 + 1)):
                            for yy in range(y - ((self.pxlGrid - 1) // 2), y + ((self.pxlGrid - 1) // 2 + 1)):
                                if int(np.sum(self.inImage[yy, xx, :])) > self.threshold:
                                    self.light[yy, xx] = True

                                    # we will save all the pixels above the threshold,
                                    # to more easilly process them later
                                    if [yy, xx] in self.coords:
                                        print('ERROR: we are repeating pixel -see blockCoords to fix this')
                                    self.coords.append([yy, xx])

                                    # for edges
                                    if int(np.sum(self.inImage[yy - 1, xx, :])) <= self.threshold or int(
                                            np.sum(self.inImage[yy + 1, xx, :])) <= self.threshold or int(
                                            np.sum(self.inImage[yy, xx - 1, :])) <= self.threshold or int(
                                            np.sum(self.inImage[yy, xx + 1, :])) <= self.threshold:
                                        self.edges.append([yy, xx])

                        # now checking if it's an edge case & if we need to fill in more pixels:
                        for xOffset in np.arange(x - self.pxlGrid, x + self.pxlGrid + 1, self.pxlGrid):
                            for yOffset in np.arange(y - self.pxlGrid, y + self.pxlGrid + 1, self.pxlGrid):
                                # Note: these for loops analyse the current main pixel, but thats ok,
                                # cause to get here it has to be ove the threshold,
                                # so it will never be analysed here (cause it would need to be under the threshold)
                                if int(np.sum(self.inImage[yOffset, xOffset, :])) <= self.threshold or (yOffset == 0 and xOffset == 0):

                                    # so we dont analyse it twice
                                    if [yOffset, xOffset] not in self.blockCoords:
                                        self.blockCoords.append([yOffset, xOffset])
                                        # if a block's main pixel next to it is not over the threshold,
                                        # then it is an edge case
                                        # so then we will analyse
                                        for xx in range(xOffset - ((self.pxlGrid - 1) // 2),
                                                        xOffset + ((self.pxlGrid - 1) // 2 + 1)):
                                            for yy in range(yOffset - ((self.pxlGrid - 1) // 2),
                                                            yOffset + ((self.pxlGrid - 1) // 2 + 1)):
                                                if int(np.sum(self.inImage[yy, xx, :])) > self.threshold:
                                                    self.light[yy, xx] = True

                                                    # also save location for later
                                                    if [yy, xx] in self.coords:
                                                        print('ERROR: we are repeating pixel -blockCoords to fix this')
                                                    self.coords.append([yy, xx])

                                                    # for edges
                                                    if int(np.sum(self.inImage[yy - 1, xx, :])) <= self.threshold or int(
                                                            np.sum(self.inImage[yy + 1, xx, :])) <= self.threshold or int(
                                                            np.sum(self.inImage[yy, xx - 1, :])) <= self.threshold or int(
                                                            np.sum(self.inImage[yy, xx + 1, :])) <= self.threshold:
                                                        self.edges.append([yy, xx])

        #_______________________________________________________________________________________________________________

        # TEMP - SAVING
        print('saving..')
        
        # CONVERTING LIGHT TO IMG
        [h, w, colors] = self.inImage.shape
        self.img = np.zeros((h, w, colors), dtype=np.uint8)
        pxlGrid = 21
        for x in np.arange(pxlGrid,w-pxlGrid, pxlGrid):
            for y in np.arange(pxlGrid,h-pxlGrid, pxlGrid):
                if self.light[y,x]: 
                    # if the pixel is above the threshold
                    # we will analyse the block around it
                    for xx in range(x-((pxlGrid-1)//2), x+((pxlGrid-1)//2 +1)):
                        for yy in range(y-((pxlGrid-1)//2), y+((pxlGrid-1)//2 +1)):
                            if self.light[yy,xx]:
                                self.img[yy,xx,0] = 255
                                self.img[yy,xx,1] = 255
                                self.img[yy,xx,2] = 255
                                
                                if [yy,xx] in self.edges:
                                    self.img[yy,xx,0] = 255
                                    self.img[yy,xx,1] = 190
                                    self.img[yy,xx,2] = 0
                                
                    # now checking if it's an edge case & if we need to fill in more pixels:
                    for xOffset in np.arange(x-pxlGrid,x+pxlGrid+1, pxlGrid):
                        for yOffset in np.arange(y-pxlGrid,y+pxlGrid+1, pxlGrid):
                            # note these for loops analyse the current main pixel, but thats ok,
                            # cause to get here it has to be ove the threshold, so it will never be analysed here
                            # (cause it would need to be under the threshold)
                            if self.light[yOffset,xOffset] != True:
                                # if a block's main pixel next to it is not over the threshold, then it is an edge case
                                # so then we will analyse 
                                for xx in range(xOffset-((pxlGrid-1)//2), xOffset+((pxlGrid-1)//2 +1)):
                                    for yy in range(yOffset-((pxlGrid-1)//2), yOffset+((pxlGrid-1)//2 +1)):
                                        if self.light[yy,xx]:
                                            self.img[yy,xx,0] = 255
                                            self.img[yy,xx,1] = 255
                                            self.img[yy,xx,2] = 255
                                            
                                        if [yy,xx] in self.edges:
                                            self.img[yy,xx,0] = 255
                                            self.img[yy,xx,1] = 190
                                            self.img[yy,xx,2] = 0

        Image.fromarray(self.img, 'RGB').save('1.png')
        #__________________________________________________________________________________________________________________________
        
    # def processImageRecursion(self,y,x):
    #     if [y,x] in self.blockCoords:
    #         return
    #     else:
    #         self.blockCoords.append([y,x])
    #
    #         for xx in range(x-((self.pxlGrid-1)//2), x+((self.pxlGrid-1)//2 +1)):
    #             for yy in range(y-((self.pxlGrid-1)//2), y+((self.pxlGrid-1)//2 +1)):
    #                 if int(np.sum(self.inImage[yy,xx,:])) > self.threshold:
    #                     self.light[yy,xx] = True
    #
    #         # now checking if it's an edge case & if we need to fill in more pixels:
    #         for xOffset in np.arange(x-self.pxlGrid,x+self.pxlGrid+1, self.pxlGrid):
    #             for yOffset in np.arange(y-self.pxlGrid,y+self.pxlGrid+1, self.pxlGrid):
    #                 self.processImageRecursion(yOffset,xOffset)