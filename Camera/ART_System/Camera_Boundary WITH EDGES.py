################################################## from sh import gphoto2 as gp
from matplotlib.image import imread
from PIL import Image
import numpy as np
import signal
import os
import subprocess


class Camera:

    grid = [[1,0],[-1,0],[0,-1],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]]
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
        self.threshold = 0
        # we will analyse every few pixels for speed (then look at the others, if that main pixel is valid) here the main pixel is every X pixels
        self.pxlGrid = 21  # Note: has to be an odd number
        self.light = np.zeros((2, 3), dtype=np.bool)
        self.coords = []
        self.blockCoords = []


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
            self.inImage = imread('test LED shots-027.JPG')
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



        # FIRST, we analyse the image to find the valid pixels

        [self.h, self.w, self.colors] = self.inImage.shape
        self.light = np.zeros((self.h, self.w), dtype=np.bool)
        edges = []
        rightEdges = []

        # We will look at every X number to speed things up,
        # but must remember to look at the other pixels & REMEMBER FAIL CASES!
        # (if the last pixel analysed near the X is bad then still look at the ones near it)
        for x in np.arange(self.pxlGrid,self.w-self.pxlGrid, self.pxlGrid):
            for y in np.arange(self.pxlGrid,self.h-self.pxlGrid, self.pxlGrid):
                if int(np.sum(self.inImage[y,x,:])) > self.threshold: # if the pixel's brightness is above the threshold

                    if [y, x] not in self.blockCoords:

                        for xOffset in np.arange(x - self.pxlGrid, x + self.pxlGrid + 1, self.pxlGrid):
                            for yOffset in np.arange(y - self.pxlGrid, y + self.pxlGrid + 1, self.pxlGrid):
                                if int(np.sum(self.inImage[yOffset, xOffset, :])) <= self.threshold or (yOffset == y and xOffset == x):

                                    if [yOffset, xOffset] not in self.blockCoords:

                                        # Finally we can start analysing the image
                                        self.blockCoords.append([yOffset, xOffset])
                                        for xx in range(xOffset - ((self.pxlGrid - 1) // 2), xOffset + ((self.pxlGrid - 1) // 2 + 1)):
                                            for yy in range(yOffset - ((self.pxlGrid - 1) // 2), yOffset + ((self.pxlGrid - 1) // 2 + 1)):
                                                if int(np.sum(self.inImage[yy, xx, :])) > self.threshold:

                                                    # Now, with the valid pixels we will:
                                                    self.light[yy, xx] = True

                                                    # for edges
                                                    if int(np.sum(
                                                            self.inImage[yy - 1, xx, :])) <= self.threshold or int(
                                                            np.sum(
                                                                self.inImage[yy + 1, xx, :])) <= self.threshold or int(
                                                            np.sum(
                                                                self.inImage[yy, xx - 1, :])) <= self.threshold or int(
                                                            np.sum(self.inImage[yy, xx + 1, :])) <= self.threshold:
                                                        # save edges to their own list
                                                        edges.append([yy,xx])

                                                        # right edges only
                                                        if int(np.sum(self.inImage[yy,xx-1,:])) <= self.threshold:
                                                            rightEdges.append([yy, xx])



        # NOW to find & separate the individual LED edges

        LEDedges = []
        e = []

        while len(edges) > 0:
            [y,x] = edges[0]
            edges.remove([y,x])
            e.append([y,x])
            going = True
            while going:
                oldY = y
                oldX = x

                for i in self.grid:
                    yy = y + i[0]
                    xx = x + i[1]
                    if [yy,xx] in edges:
                        y = yy
                        x = xx
                        e.append([y,x])
                        edges.remove([yy,xx])
                        break

                if oldY == y and oldX == x:
                    LEDedges.append(e.copy())
                    e.clear()
                    going = False

        for e in LEDedges:
            if len(e) <= 3:
                print('ERROR in separating the edges, probably bad threshold, or vehicle too far away')
                break




































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
                                
                                if [yy,xx] in edges:
                                    self.img[yy,xx,0] = 255
                                    self.img[yy,xx,1] = 0
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

        for e in LEDedges[0]:
            [yy,xx] = e
            self.img[yy, xx, 0] = 0
            self.img[yy, xx, 1] = 0
            self.img[yy, xx, 2] = 255
        for e in LEDedges[1]:
            [yy, xx] = e
            self.img[yy, xx, 0] = 0
            self.img[yy, xx, 1] = 255
            self.img[yy, xx, 2] = 0
        for e in LEDedges[2]:
            [yy, xx] = e
            self.img[yy, xx, 0] = 255
            self.img[yy, xx, 1] = 0
            self.img[yy, xx, 2] = 0
        for e in LEDedges[3]:
            [yy, xx] = e
            self.img[yy, xx, 0] = 255
            self.img[yy, xx, 1] = 0
            self.img[yy, xx, 2] = 255

        for e in rightEdges:
            [yy, xx] = e
            self.img[yy, xx, 0] = 255
            self.img[yy, xx, 1] = 255
            self.img[yy, xx, 2] = 0

        Image.fromarray(self.img, 'RGB').save('1.png')
        Image.fromarray(self.img, 'RGB').show()