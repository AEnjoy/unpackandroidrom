-  ozip2zip
Convert Oppo ozip firmware file to zip files


Welcome to Androidiya -  Please Subscribe if you haven't

Please subscribe for more https://www.youtube.com/channel/UC0dMbs2KSS5GvBMRoyQZ4Ow/featured?disable_polymer=1

I am Tahir, I just found this code online which worked for me. I spend several housr to find a solution to convert Oppo firmware from ozip ro zip file b ut only this code worked for me on Linux. I didn't write this code and I don't know how wrote this code. I am just sharing it because it works.

I was able to convert Oppo F5 firmware to zip file with this.

**How to use it**

Open terminal and use thse commands to Install Python
```
   sudo apt install python3
   sudo apt install python3-pip
   pip3 install pycrypto
```
Now create a new directory and move .ozip firmware file, ozipdecrypt.py, and ofp_libextract.py in this same folder.

Run  
```
   ./ozipdecrypt.py *.ozip
```
or 
```
./ozipdecrypt.py firmwarefilename.ozip
```
It will take a minute ot two to convert, depends on the file size.

**With this code you can convert**

Oppo,Realme

[ stock recovery ozip --> custom recovery flashable to zip ]

Supported devices list for .ozip to .zip 

OPPO:-  
- A77
- R11
- R11s
- R11s Plus
- R9s
- R9s Plus
- FindX
- FindX
- K1
- Reno
- K3
- A9
- Reno 10x zoom PCCM00
- A1
- A83t
- R17 Pro

REALME:-
- Realme 2 = Rename the .ozip file to .zip and flash via recovery
- Realme C1 = Rename the .ozip file to .zip and flash via recovery
- Realme 1
- Realme C2
- Realme 2 pro
- Realme U1 RMX1831
- Realme 3 RMX1825EX
- Realme 3 Pro
- Realme X
- Realme X2
- Realme 5
- Realme 5 = Rename the .ozip file to .zip and flash via recovery
