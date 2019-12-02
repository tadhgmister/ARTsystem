try:
    from CameraStub import Camera
except ImportError:
    from .CameraStub import Camera

try:
    from ServoStub import Servo
except ImportError:
    from .ServoStub import Servo

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.interpolate import UnivariateSpline


class ImgProc:

    co = {'r':0, 'g':60, 'b':115}

    def __init__(self, debbugMODE):
        self.mode = debbugMODE

        # INIT BOUNDARY CLASSES
        self.servo = Servo()
        self.camera = Camera()

        self.status = 'standby'

    # returns the camera calculated position of the car
    # FOR TEST it returns a random location between 22cm and 624cm, and orientation between 0 and 3.14rad
    def getPos(self, vehicleX, vehicleY, vehicleOrientation):
        self.status = 'processing'

        # TAKING & OPENING IMAGE w/ variables
        f = self.camera.takePhoto()
        img = cv2.imread('Images/Full_Res/' + f, cv2.IMREAD_COLOR)
        h,w = img.shape[:2]
        # TODO add step to remove distortion
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Ranges:       NOTE: jpg vs. png seems to be +-1 value (looks like division or rounding err)
        #
        # hue = 0-180 (for cv2) 0-359/360 (for photoshop)       hue: (ph/360) = (cv/180)
        # sat = 0-255 (for cv2) 0-100% (for photoshop)          sat: (ph/100) = (cv/255)
        # val = 0-255 (for cv2) 0-100% (for photoshop)          val: (ph/100) = (cv/255)
        #
        # TODO WATCH FOR GRAYS!   ex.     4x4 tester.jpg     pxl(3,1) decripted as [165 5 100]  -   but in ph = 0,0,39      ????

        ################################################################################################################

        # FINDING & SEPERATING EACH COLOUR
        # TODO test & define colour limits - make them adaptable? - set them for every new environment?
        # they are equal to (tagret color's hue) & (tagret color's saturation) & (tagret color's brightness)
        colors = {}
        colors['r'] = ((img[:, :, 0] < 5) | (img[:, :, 0] > 170)) & (img[:, :, 1] > 128) & (img[:, :, 2] > 128)
        colors['g'] = ((img[:, :, 0] > 40) & (img[:, :, 0] < 75)) & (img[:, :, 1] > 128) & (img[:, :, 2] > 128)
        colors['b'] = ((img[:, :, 0] > 100) & (img[:, :, 0] < 130)) & (img[:, :, 1] > 128) & (img[:, :, 2] > 128)


        # NOW TO USE A LOOPING FLOOD FUNCTION TO SEPERATE EACH COLOUR


        state = {'r': 1, 'g': 2, 'b': 3}

        # grid is used to track what state of every pixel while separating them
        grid = np.zeros((h, w), np.uint8)

        sections = {}
        sections['r'] = []
        sections['g'] = []
        sections['b'] = []

        for i in sections:
            grid[:, :] = (colors[i] * state[i])
            while True:
                # loop will brake when all the colours have been grouped into their shapes
                if len(np.where(grid == state[i])[0]) == 0:
                    break
                # This creates an array of the [x,y] of just the valid pixels
                refY, refX = np.where(grid == state[i])
                mask = np.zeros((h+2, w+2), np.uint8)
                # this makes a mask of only the pixels that are touching each other
                cv2.floodFill(grid, mask, (refX[0],refY[0]), 0, 0, 0)
                # deletes the extra edges of the mask
                mask = np.delete(mask, 0, axis=0)
                mask = np.delete(mask, len(mask)-1, axis=0)
                mask = np.delete(mask, 0, axis=1)
                mask = np.delete(mask, len(mask), axis=1)
                # lastly we add that mask to our list
                sections[i].append(mask * state[i])



        # TODO THIS SECTION IS TO CHECK IF THERE IS ANY SEPARATED SHAPES THAT ARE ALL FROM THE LED &then it will combine them

        for i in sections:
            changes = True
            while changes:
                changes = False
                shapesToRemove = []
                newShapes = []
                #print('\n\n', i, ' = \n\n')
                for s in range(0, len(sections[i])):
                    if changes:
                        break

                    shape = sections[i][s]
                    # print('-----------------------------------------------\n',shape,'\n---------------------->\n')
                    Ycurrent, Xcurrent = np.where(shape == state[i])
                    maxCurrent = len(Ycurrent)-1
                    # each shape will look at every other shape & check
                    for sOther in range(0, len(sections[i])):
                        if changes:
                            break

                        shapeOther = sections[i][sOther]
                        # just checking that the shape is not comparing to it's self (cause that will always result in a true & break the algorythm)
                        if shape is not shapeOther:
                            Yother, Xother = np.where(shapeOther == state[i])
                            maxOther = len(Yother)-1

                            Ysimilar = False
                            Xsimilar = False
                            # to compare the shapes:
                            if (min(Ycurrent) >= min(Yother)) and (max(Ycurrent) <= max(Yother)):
                                Ysimilar = True
                            elif (min(Ycurrent) <= min(Yother)) and (max(Ycurrent) >= min(Yother) and max(Ycurrent) <= max(Yother)):
                                Ysimilar = True
                            elif (min(Ycurrent) >= min(Yother) and min(Ycurrent) <= max(Yother)) and (max(Ycurrent) >= max(Yother)):
                                Ysimilar = True

                            if (min(Xcurrent) >= min(Xother)) and (max(Xcurrent) <= max(Xother)):
                                Xsimilar = True
                            elif (min(Xcurrent) <= min(Xother)) and (max(Xcurrent) >= min(Xother) and max(Xcurrent) <= max(Xother)):
                                Xsimilar = True
                            elif (min(Xcurrent) >= min(Xother) and min(Xcurrent) <= max(Xother)) and (max(Xcurrent) >= max(Xother)):
                                Xsimilar = True

                            # finally, if valid then the new shape will be saved
                            # and the for loops will exit and restart
                            if Xsimilar and Ysimilar:
                                changes = True
                                sections[i].pop(s)
                                sections[i].pop(sOther-1)
                                sections[i].append(shape+shapeOther)



        if self.mode >= 1 and False:
            count = 0
            for i in sections:
                for s in sections[i]:
                    count += 1
            print(count)



        # NOW TO select the shape with the the biggest area & call them LEDs
        LEDs = {}

        # green
        currBiggest = sections['g'][0]
        for shape in sections['g']:
            y,x = np.where(shape == state['g'])
            yBig,xBig = np.where(currBiggest == state['g'])
            if len(yBig) < len(y):
                currBiggest = shape
        LEDs['g'] = currBiggest

        # blue
        currBiggest = sections['b'][0]
        for shape in sections['b']:
            y, x = np.where(shape == state['b'])
            yBig, xBig = np.where(currBiggest == state['b'])
            if len(yBig) < len(y):
                currBiggest = shape
        LEDs['b'] = currBiggest

        # red
        # Note: since there is 2 this one is a little more complex
        currBiggest = sections['r'][0]
        currSecBiggest = sections['r'][0]
        for shape in sections['r']:
            y, x = np.where(shape == state['r'])
            yBig, xBig = np.where(currBiggest == state['r'])
            ySecBig, xSecBig = np.where(currSecBiggest == state['r'])
            if len(yBig) < len(y):
                currBiggest = shape
            elif len(ySecBig) < len(y):
                currSecBiggest = shape

        # now to find which one is on top
        yBig, xBig = np.where(currBiggest == state['r'])
        ySecBig, xSecBig = np.where(currSecBiggest == state['r'])
        if min(yBig) < min(ySecBig):
            LEDs['rHigh'] = currBiggest
            LEDs['rLow'] = currSecBiggest
        else:
            LEDs['rHigh'] = currSecBiggest
            LEDs['rLow'] = currBiggest

        if LEDs['rHigh'] == LEDs['rLow']:
            print('err') # TODO make my error cases WAY better

        # since we have 2 reds now we need to update the states
        state = {'rHigh': 1, 'rLow': 1, 'g': 2, 'b': 3}

        # TODO check if the shapes are the correct shape (and no weird indents and stuff)

        # TODO check if each led has relatively the same width & shape

        # NOW TO FIND THE CENTRAL POINT OF EACH LED
        LEDpoints = {}

        for i in LEDs:
            print(LEDs[i],'\n')
            y,x = np.where(LEDs[i] == state[i])
            yDiff = (((max(y) - min(y)) + 1) + min(y)) / 2
            xDiff = (((max(x) - min(x)) + 1) + min(x)) / 2
            print('Diff:\t', yDiff, '\t', xDiff)







        # TO SHOW IMAGE FOR DEBUGGING ------------------------------------------
        if self.mode >= 1:
            img[:, :, 0] = colors['r'] * 180 + colors['g'] * 60 + colors['b'] * 115
            img[:, :, 1] = colors['r'] * 220 + colors['g'] * 220 + colors['b'] * 220
            img[:, :, 2] = colors['r'] * 255 + colors['g'] * 255 + colors['b'] * 255

        if self.mode >= 1:
            for i in sections:
                color = 30
                #print('\n\n',i,' = \n\n')
                for a in sections[i]:
                    color += 80
                    if color > 200:
                        color = 30

                    for y in range(0, len(a[:,0])):
                        for x in range(0, len(a[0,:])):
                            if a[y, x] == 1:
                                img[y, x, 0] = self.co[i]
                                img[y, x, 1] = color
                                img[y, x, 2] = color

            if self.mode >= 1:
                img[:, :, 0] = (LEDs['rLow'] * 0) + (LEDs['rHigh'] * 0) + (LEDs['g'] * 30) + (LEDs['b'] * 115)  # ??? why does green only look good at 30 ??????????
                img[:, :, 1] = (LEDs['rLow'] * 255) + (LEDs['rHigh'] * 255) + (LEDs['g'] * 255) + (LEDs['b'] * 255)
                img[:, :, 2] = (LEDs['rLow'] * 255) + (LEDs['rHigh'] * 255) + (LEDs['g'] * 255) + (LEDs['b'] * 255)

            # to display final img
            # self.printPxls(img)
            self.showImgMatPlt(img)
            self.savePIL(img)
        # -----------------------------------------------------------------------

        ################################################################################################################

        # TODO measure them

        # TODO check calculated ones are close enough
        x = 25.0
        y = 600.0
        orientation = 3.141592653 / 2
        return x, y, orientation





    #     # First is to Import
    #     # ----------------------------------
    #
    #
    #
    #     # ----------------------------------
    #     LEDs = self.camera.takePhoto()
    #
    #     # SUDO get from camera:
    #     orientation = self.servo.getAngle()
    #     x, y = LEDs[0]
    #     self.status = 'standby'
    #     return [x, y, orientation]

    # if any class wants to know what state the camera is in,
    # this class will give it
    def getStatus(self):
        return self.status

    def calibrate(self):
        # TODO make calibration
        print('hi')

    def makePattern(self, f):
        #img = cv2.imread('Images/Full_Res/' + f, cv2.IMREAD_COLOR)
        img = cv2.imread('Images/Full_Res/' + f, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape[:2]
        # edges = cv2.Canny(img, 100, 200)
        # # kernel = np.ones((2, 2), np.uint8)
        # # edges = cv2.erode(edges, kernel)
        #
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gray = np.float32(gray)
        # corners = cv2.cornerHarris(gray,2,3,0.04)
        # #corners = cv2.dilate(corners, None)
        # img[corners > 0.01 * corners.max()] = [0, 0, 255]
        # print(img)
        # print(corners)
        # print(edges)

        for y in range(0, len(img[:,0,0])-1):
            for x in range(0, len(img[0, :, 0]) - 1):




        # plt.imshow(edges, cmap='hsv', interpolation='bicubic')
        # plt.show()

        plt.subplot(121),plt.imshow(img,cmap = 'gray')
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(edges,cmap = 'gray')
        plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
        plt.show()




    # FOR TESTING
    def scaleImg(self, img, amount):
        # SCALING IS JUST FOR PROCESSING TIME - WARNING IT RUINS MEASUREMENTS
        scale_percent = 500  # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        return img

    def showImgMatPlt(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img, cmap='hsv', interpolation='bicubic')
        plt.show()

    def printPxls(self, img):
        for y in range(0,img.shape[0]):
            for x in range(0,img.shape[1]):
                print('x=',x,' y=',y,' = ',img[y,x,:])
            print('')

        print('')
        print('HUE =\n', img[:, :, 0], '\n')
        print('SAT =\n', img[:, :, 1], '\n')
        print('VAL =\n', img[:, :, 2], '\n')

    def savePIL(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        Image.fromarray(img, 'RGB').save('1.png')

    def showPIL(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        Image.fromarray(img, 'RGB').show()


# class LED():