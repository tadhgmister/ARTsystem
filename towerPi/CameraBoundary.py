#from sh import gphoto2 as gp
import signal, os, subprocess, time

class Camera:
    def __init__(self, filepath):
        self.saveLocation = filepath
        
        # FIRST TO KILL ANY PROCESSES RUNNING ON THE CAMERA (so we can take it over)
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        # Search for the line that has what we want to kill
        for line in out.splitlines():
            if b'gvfsd-gphoto2' in line:
                pid = int(line.split(None,1)[0])
                os.kill(pid, signal.SIGKILL)
                
        # TO TEST IT
    
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        
        bad = False
        for line in out.splitlines():
            if b'gvfsd-gphoto2' in line:
                print('kill gphoto2 - ERROR')
                bad = True
        if bad == False:
            print('kill gphoto2 - we are ok!')
            
        subprocess.Popen(['gphoto2', '--auto-detect'], stdout=subprocess.PIPE)
        
    def takePhoto(self):
        # FIRST TO KILL ANY PROCESSES RUNNING ON THE CAMERA (so we can take it over)
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        # Search for the line that has what we want to kill
        for line in out.splitlines():
            if b'gvfsd-gphoto2' in line:
                pid = int(line.split(None,1)[0])
                os.kill(pid, signal.SIGKILL)
        os.chdir(self.saveLocation)
        
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        
        bad = False
        for line in out.splitlines():
            if b'gvfsd-gphoto2' in line:
                print('kill gphoto2 - ERROR')
                bad = True
        if bad == False:
            print('kill gphoto2 - we are ok!')
            
        print(subprocess.Popen(['gphoto2', '--auto-detect'], stdout=subprocess.PIPE))
        
        try:
            subprocess.Popen(['gphoto2', '--capture-image-and-download', '--force-overwrite'], stdout=subprocess.PIPE) #, '--force-overwrite'])
        except:
            print('ERROR: couldn\'t take photo')
            
        files = os.scandir()
        for f in files:
            print(str(f))
            
        return 'capt0000.jpg'