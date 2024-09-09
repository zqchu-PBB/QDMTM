import subprocess
import os.path
directory=os.path.dirname(os.path.abspath(__file__))
subprocess.call(["pyuic5", os.path.join(directory,"GUI.ui"),">",os.path.join(directory,"GUI.py")],shell=True)