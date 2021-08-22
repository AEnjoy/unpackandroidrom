#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#       make.py
#       By : 神郭
import os,zipfile,platform
from shutil import copy,copytree
def main():
    print('''make:
    [1]:下载Python库Lib依赖 [2]:安装pyinstaller [3]:同步源代码(需要先安装git) 
    [4]:编译可执行文件      [5]:清理工作目录     [6]:Exit
    ''')
    a=int(input('>>>'))
    if a==1:
        l=['lz4','ConfigParser','protobuf','brotli','pycryptodome',
        'docopt','Crypto','zstandard','google','checker','glob2']
        for i in l:os.system('pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple '+i)
        main()
        return
    if a==2:
        os.system('pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller')
        main()
        return
    if a==3:
        os.system('git pull')
        main()
        return
    if a==4:
        os.system('pyinstaller -F main.py')
        copy('Project.txt', 'dist'+os.sep+'Project.txt')
        copy('about_pycrypto.md', 'dist'+os.sep+'about_pycrypto.md')
        copy('README.md', 'dist'+os.sep+'README.md')
        copy('requirements.txt', 'dist'+os.sep+'requirements.txt')
        copy('README_LGKDZ.txt', 'dist'+os.sep+'README_LGKDZ.txt')
        copy('README_ozip.md', 'dist'+os.sep+'README_ozip.md')
        copy('README_unpayload.md', 'dist'+os.sep+'README_unpayload.md')
        copy('README_simg2img.txt', 'dist'+os.sep+'README_simg2img.txt')        
        copytree('pic', 'dist'+os.sep+'pic')
        z = zipfile.ZipFile(platform.system()+'_'+platform.machine()+'.zip', 'w',compression=zipfile.ZIP_DEFLATED,allowZip64=True) 
        for d in os.listdir('dist'):
            z.write('dist'+os.sep+d)
        for c in os.listdir('dist'+os.sep+'pic'):
            z.write('dist'+os.sep+'pic'+os.sep+c)            
        z.close()
        main()
        return
    if a==5:
        l1=['main.spec','main.zip']
        l2=['__pycache__','build','dist','logs','temp']
        for i in l1:
            try:os.remove(i)
            except:pass
        for i in l2:
            try:os.rmdir(i)
            except:pass
        main()
        return
    if a==6:exit()
if __name__ == '__main__':
    main()