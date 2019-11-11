from sh import gphoto2 as gp
from matplotlib.image import imread
from PIL import Image
import numpy as np
import signal, os, subprocess, time

class Camera:
    
    def __init__(self):
        # gphoto2 will auto start up when the camera is connected (we want to kill this as only 1 program can interact with the DSLR at a time)
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        # Search for the line that has what we want to kill
        for line in out.splitlines():
            if b'gvfsd-gphoto2' in line:
                pid = int(line.split(None,1)[0])
                os.kill(pid, signal.SIGKILL)
                
        print(gp(['--auto-detect']))



    def getPosition(self):
        self.takeFullResPhoto()
        self.processImage()
        
        
    def takeFullResPhoto(self):
        print('taking photo..')
        # deletes any current files
        files = os.listdir('/home/pi/Desktop/ART_System/Images/Full_Res')
        for f in files:
            os.remove('/home/pi/Desktop/ART_System/Images/Full_Res/' + f)

        # set save location & inImage type (0=fineQualityJPG, which is equivilent to 11 or 12 when exporting in photoshop)
        os.chdir('/home/pi/Desktop/ART_System/Images/Full_Res')
        gp(['--set-config', '/main/imgsettings/imageformat=0'])

        # takes image
        try:
            gp(['--capture-image-and-download'])#, '--force-overwrite']) # overwrite is needed sometimes for consistentcy?
        except:
            print('ERROR: couldn\'t take photo')

        # only ok, if 1 file in library
        files = os.listdir('/home/pi/Desktop/ART_System/Images/Full_Res') # sometime it is called the wrong name/does load/doesn't delete (because gphoto is bad, so this compensates for it)
        if len(files) > 1:
            print('ERROR: too many files')
        else:
            try:
                print('reading in image..')
                self.inImage = imread('/home/pi/Desktop/ART_System/Images/Full_Res/' + files[0])
            except:
                print('ERROR: couldn\'t open image')

        # NEED TO ADD IN FAIL CASES
        # worst case senario -> ask user to confirm good image every time
        #                    -> might want to add in tether mode if so
   
   
   
    def processImage(self):
        print('processing image..')
        # important to remember it is y,x NOT x,y (h,w NOT w,h)
        # (i have kept it this way in this class, for saving img purposes)
        [h, w, colors] = self.inImage.shape

        # arbitrary number for now
        threshold = 500
        # we will analyse every few pixels for speed (then look at the others, if that main pixel is valid) here the main pixel is every 7 pixels
        pxlGrid = 21 # Note: has to be an odd number
        self.img = np.zeros((h, w, colors), dtype=np.uint8)
        self.light = np.zeros((h, w), dtype=np.bool)
        
        blockCoords = []
        # using every 7 for speed, but must remember to look at the other pixels & REMEMBER FAIL CASES! (if the last pixel analysed near the 7 is bad then still look at the ones near it)
        for x in np.arange(pxlGrid,w-pxlGrid, pxlGrid):
            for y in np.arange(pxlGrid,h-pxlGrid, pxlGrid):
                if int(self.inImage[y,x,0]) + int(self.inImage[y,x,1]) + int(self.inImage[y,x,2]) > threshold: 
                    
                    #if [y,x] not in blockCoords:
                        
                    
                    # if the pixel is above the threshold
                    # we will analyse the block around it
                    for xx in range(x-((pxlGrid-1)//2), x+((pxlGrid-1)//2 +1)):
                        for yy in range(y-((pxlGrid-1)//2), y+((pxlGrid-1)//2 +1)):
                            if int(self.inImage[yy,xx,0]) + int(self.inImage[yy,xx,1]) + int(self.inImage[yy,xx,2]) > threshold:
                                self.img[yy,xx,0] = 255
                                self.img[yy,xx,1] = 255
                                self.img[yy,xx,2] = 255
                    
                    # we will save all the blocks above the threshold, to more easilly process them later
                    blockCoords.append([y,x])
                    
                    # now checking if it's an edge case & if we need to fill in more pixels:
                    for xOffset in np.arange(x-pxlGrid,x+pxlGrid+1, pxlGrid):
                        for yOffset in np.arange(y-pxlGrid,y+pxlGrid+1, pxlGrid):
                            if int(self.inImage[yOffset,xOffset,0]) + int(self.inImage[yOffset,xOffset,1]) + int(self.inImage[yOffset,xOffset,2]) <= threshold: # note these for loops analyse the current main pixel, but thats ok, cause to get here it has to be ove the threshold, so it will never be analysed here (cause it would need to be under the threshold)
                                # if a block's main pixel next to it is not over the threshold, then it is an edge case
                                # so then we will analyse 
                                for xx in range(xOffset-((pxlGrid-1)//2), xOffset+((pxlGrid-1)//2 +1)):
                                    for yy in range(yOffset-((pxlGrid-1)//2), yOffset+((pxlGrid-1)//2 +1)):
                                        if int(self.inImage[yy,xx,0]) + int(self.inImage[yy,xx,1]) + int(self.inImage[yy,xx,2]) > threshold:
                                            self.img[yy,xx,0] = 255
                                            self.img[yy,xx,1] = 255
                                            self.img[yy,xx,2] = 255
                                
                                # also save block location for later
                                blockCoords.append([yOffset,xOffset])

        #__________________________________________________________________________________________________________________________

        # TEMP - SAVING
        print('saving..')
        Image.fromarray(self.img, 'RGB').save('my.png')
        
        #__________________________________________________________________________________________________________________________
        
        

# TEMP FOR TESTING

cam = Camera()
cam.getPosition()