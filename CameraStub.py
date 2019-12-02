import os

class Camera:
    def __init__(self):
        i = 0

    def takePhoto(self):
        print('')
        print('***CAMERA STUB IS TAKING PHOTO***')
        print('')

        CHOICE = 6

        if CHOICE == 0:
            images = os.scandir('Images/Full_Res/')
            for fname in images:
                if (str(fname)[27:len(str(fname))-6]) == '25':
                    return str(fname)[11:len(str(fname))-2]

        elif CHOICE == 1:
            return '3x3 hsv tester.png'

        elif CHOICE == 2:
            return '3x3 hsv tester.jpg'

        elif CHOICE == 3:
            return '4x4 tester.jpg'

        elif CHOICE == 4:
            return '40x40 tester.jpg'

        elif CHOICE == 5:
            return '5x5 for basic edges.jpg'

        elif CHOICE == 6:
            return '8x8.jpg'

        elif CHOICE == 7:
            return '20x20.jpg'