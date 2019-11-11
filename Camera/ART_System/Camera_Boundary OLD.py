from sh import gphoto2 as gp
import signal, os, subprocess, time


def killgphoto2Process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the line that has what we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)
    
    # TO TEST IT
    
    #p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    #out, err = p.communicate()
    #
    #bad = False
    #for line in out.splitlines():
    #    if b'gvfsd-gphoto2' in line:
    #        print('kill gphoto2 - ERROR')
    #        bad = True
    #
    #if bad == False:
    #    print('kill gphoto2 - we are ok!')

def captureFullImage():
    os.chdir('/home/pi/Desktop/ART_System/Images/Full_Res')
    gp(['--set-config', '/main/imgsettings/imageformat=0'])
    #files = os.scandir()
    
    try:
        gp(['--capture-image-and-download'])#, '--force-overwrite'])
    except:
        print('ERROR: couldn\'t take photo')

    #newfiles = os.scandir()
    #if files == newfiles:
    #    print('ERROR: couldn\'t focus')
    
# iso = 
# shutter_speed = str(gp(['--get-config', '/main/capturesettings/shutterspeed']))
# aperture = str(gp(['--get-config', '/main/capturesettings/aperture']))
# print(iso)
# print(shutter_speed)
# print(aperture)
    
    
    
    
#_____________________________________________________________________________________________________________________________________________________________________________________



# gphoto2 will auto start up when the camera is connected (we want to kill this as only 1 program can interact with the DSLR at a time)
killgphoto2Process()
captureFullImage()
time.sleep(30)







