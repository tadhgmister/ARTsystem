import cv2

class Camera:

    # Defines the 8 pixels around the pixel
    ### Note: the order it checks them in is important
    ### specifically the first 4 pixels are before the last 4
    grid = [[1, 0], [-1, 0], [0, -1], [0, 1], [-1, -1], [-1, 1], [1, -1], [1, 1]]

    def __init__(self):
        print('hi')