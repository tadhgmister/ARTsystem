try:
    from CameraStub import Camera
except ImportError:
    from .CameraStub import Camera

try:
    from ServoStub import Servo
except ImportError:
    from .ServoStub import Servo

import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.interpolate import UnivariateSpline

class ProcessingError(Exception):
    pass
ANGLE_TOLERANCE = math.pi/6 #30deg, if we measure more than this difference between tail and side lights then we will error
RED_X_TOLERANCE = 0.1 #if red lights are detected more than this percent of x/y offsets then throw an error, if red leds are upright then this should be 0.
class ImgProc:
    #TODO: CORRECT THIS DISTANCE
    TAIL_LIGHT_DISTANCE = 30
    "distance from the red center led to the tail blue led in cm"
    #TODO: CORRECT THIS POSITION
    SIDE_LIGHT_DISTANCE = 10
    "distance from the red center led to the side green led in cm"
    #TODO CORRECT THIS NUMBER
    RED_LIGHT_CM_DISTANCE = 20
    "distance between high and low LED in cm"

    FOV_ANGLE_HEIGHT = math.radians(15.3)
    """angle that the camera can see in the vertical
    this can vary slightly based on plane of focus and is calculated based on properties of the lens
    it might make more sense to collect sample data for car distance to how many pixels apart the red LEDs appear and do interpolation instead of
    calculating it based on this and trig."""
    CANVAS_HEIGHT_PX = 3840
    """height of the photos taken in pixels, used to find the distance the car is from the tower"""

    co = {'r':0, 'g':60, 'b':115}

    @classmethod
    def convert_red_px_to_dist(cls,px_dist):
        """returns how far away the car is from the tower in cm based on how far apart the red LEDs appear in the photo"""
        # see FOV_angle_calculation for where the following equation comes from
        # tan(FOV/2) = (canvas_height_cm/2) / dist_from_tower
        # dist_from_tower = (canvas_height_cm/2)/tan(FOV/2) = (1/2tan(FOV/2)) * canvas_height_cm
        # =  (1/2tan(FOV/2)) * canvas_height_px * (cm/px)
        # = (canvas_height_px/2tan(FOV/2)) * (red_led_dist_cm / red_led_dist_px)
        return cls.CANVAS_HEIGHT_PX / (2*math.tan(cls.FOV_ANGLE_HEIGHT/2)) * cls.RED_LIGHT_CM_DISTANCE / px_dist

    def __init__(self, debbugMODE):
        self.mode = debbugMODE

        # INIT BOUNDARY CLASSES
        self.servo = Servo()
        self.camera = Camera()

        self.status = 'standby'

    def getPos(self, vehicleX, vehicleY, vehicleOrientation, *, raise_on_error=False):
        """takes a photo of the car and returns a tuple (x,y,facing) for the position as calculated by the photo
        if raise_on_error is passed as true then an error will be raised if something goes wrong, otherwise the error is logged
        and the calculated position is returned instead.
        """
        try:
            return self.getPos_internal(vehicleX, vehicleY, vehicleOrientation)
        except ProcessingError as e:
            if raise_on_error:
                raise e #just reraise error
            #otherwise just issue a warning and return the position we originally got as input
            import warnings
            warnings.warn(f"ERROR IN FINDING LEDS: {e}")
            return (vehicleX,vehicleY,vehicleOrientation)
        except NotImplementedError:
            print("CASE THAT IS NOT IMPLEMENTED WAS HIT", e)
            print("RETURNING CALCULATED NOT MEASURED POSITION")
            return (vehicleX, vehicleY, vehicleOrientation)
        except Exception:
            # if something else went wrong give full traceback
            import traceback
            traceback.print_exc(limit=-2)
            return (vehicleX, vehicleY, vehicleOrientation)

    def getPos_internal(self, vehicleX, vehicleY, vehicleOrientation):
        """internal for getPos, this will throw an error if something is off."""
        #first turn to face where the car is calculated to be
        camera_angle = math.atan2(vehicleY, vehicleX)
        #self.servo.setAngle(camera_angle)
        #next take the picture and find the led positions in the image.
        #f = self.camera.takePhoto()
        [ledsX, ledsY] = self.identifyLEDS()
        if set(ledsX.keys()) != set(ledsY.keys()):
            #sanity check, this way we can just check one of the lists and we know the other list holds it too.
            raise ValueError("mathew you messed up, x and y positions aren't consistent")
        elif 'rHigh' not in ledsX or 'rLow' not in ledsX:
            raise ProcessingError("cannot see both red leds")
        elif 'g' not in ledsX:
            raise NotImplementedError("need to consider special case where we calculate TAIL light and work if close to 45 or 90")
        elif 'b' not in ledsX:
            raise NotImplementedError("need to consider special case where we calculate SIDE light and work if close to 45 or 90")
        #otherwise we have all leds to do trig on
        # ORIENTATION OF THE CAR:
        # G   R (front up)
        #    
        #
        #     B
        
        # first we will calculate the distance from the tower using the red leds.
        red_light_pixel_dist = ledsY['rHigh'] - ledsY['rLow']
        car_dist_from_tower = self.RED_LIGHT_PX_TO_DISTANCE * red_light_pixel_dist
        #the x offset is expected to be very small so if this is high we probably have an issue.
        red_light_x_offset = ledsX['rHigh'] - ledsX['rLow']
        if red_light_x_offset/red_light_pixel_dist > RED_X_TOLERANCE:
            raise ProcessingError("red lights were more than {:.0%} offset in x direction".format(RED_X_TOLERANCE))
        
        measuredX = math.cos(camera_angle) * car_dist_from_tower
        measuredY = math.sin(camera_angle) * car_dist_from_tower

        # if car is facing away from camera, green light will be to the left (less value) and we are looking for cosine
        #so we can do acos(redx-greenx) 
        side_light_cos = (ledsX['g'] - ledsX['rHigh']) * self.SIDE_LIGHT_DISTANCE / (red_light_pixel_dist * self.RED_LIGHT_CM_DISTANCE)
        tail_light_sin = (ledsX['b'] - ledsX['rHigh']) * self.SIDE_LIGHT_DISTANCE / (red_light_pixel_dist * self.RED_LIGHT_CM_DISTANCE)

        acute_angle_from_side = math.acos(abs(side_light_cos))
        acute_angle_from_tail = math.asin(abs(tail_light_sin))
        #sanity check that different angles are not totally off (we )
        if abs(acute_angle_from_side - acute_angle_from_tail) > ANGLE_TOLERANCE:
            raise ProcessingError("angle measured using side light and tail light are not consistent.")
        # calculate an average, hopefully they are pretty close so we don't have to worry about this as much.
        ave_acute_angle = (acute_angle_from_side + acute_angle_from_tail) / 2
        #which quandrent the car is facing is based on whether the blue and green light are to right or left of red lights
        # the cases that need to be considered are outlined in the file LEDCameraCases.jpeg
        if side_light_cos < 0 and tail_light_sin > 0:
            # first quadrent, no offset
            ange_relative_camera = ave_acute_angle
        elif side_light_cos > 0 and tail_light_sin > 0:
            # both lights are to the right, car is facing toward camera and to the left
            ange_relative_camera = math.pi - ave_acute_angle
        elif side_light_cos > 0 and tail_light_sin < 0:
            # side light is to the right and tail light is to the left
            # car is facing toward camera and to the left, 3rd quadrent
            ange_relative_camera = math.pi + ave_acute_angle
        else:
            assert side_light_cos < 0 and tail_light_sin < 0, "tadhg messed up the quadrant cases, or we hit exactly 0 angle case"
            ange_relative_camera = 2*math.pi - ave_acute_angle
            
        measuredOrientation = (camera_angle + ange_relative_camera)%(2*math.pi)

        return (measuredX, measuredY, measuredOrientation)




    # returns the camera calculated position of the leds
    # FOR TEST it returns a random location between 22cm and 624cm, and orientation between 0 and 3.14rad
    def identifyLEDS(self, imgFilename=None):
        self.status = 'processing'

        img = cv2.imread('/home/pi/Desktop/towerPi/img/capt0000.jpg', cv2.IMREAD_COLOR)
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
            elif len(ySecBig) <= len(y):
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

        # if LEDs['rHigh'] == LEDs['rLow']:
        #     print('err') # TODO make my error cases WAY better

        # since we have 2 reds now we need to update the states
        state = {'rHigh': 1, 'rLow': 1, 'g': 2, 'b': 3}

        # TODO check if the shapes are the correct shape (and no weird indents and stuff)

        # TODO check if each led has relatively the same width & shape

        # TODO check if the LEDs are
        # NOW TO FIND THE CENTRAL POINT OF EACH LED
        LEDpoints = {}

        LEDYcoords = {}
        LEDXcoords = {}

        for i in LEDs:
            print(LEDs[i],'\n')
            y,x = np.where(LEDs[i] == state[i])
            ycenter = (max(y) - min(y))/2 + min(y)
            xcenter = (max(x) - min(x))/2 + min(x)
            LEDYcoords[i] = ycenter
            LEDXcoords[i] = xcenter

        return LEDXcoords, LEDYcoords


    ### DEBUGGING, CAN IGNORE UNREACHABLE CODE, THIS IS INTENDED TO BE RUN AS PART OF getPos
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
        edges = cv2.Canny(img, 100, 200)
        # kernel = np.ones((2, 2), np.uint8)
        # edges = cv2.erode(edges, kernel)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)
        corners = cv2.cornerHarris(gray,2,3,0.04)
        #corners = cv2.dilate(corners, None)
        img[corners > 0.01 * corners.max()] = [0, 0, 255]
        print(img)
        print(corners)
        print(edges)

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