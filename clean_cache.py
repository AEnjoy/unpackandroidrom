#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,platform
print('开始清理缓存')
os.rmdir('__pycache__')
if platform.system()=='Windows':
    os.system('rd /s /q META-INF output rom system system_') 
    os.system('del /f /s /q *.img payload.bin system.new.dat.br system.transfer.list system.new.dat')
if platform.system()=='Linux':
    os.system('rm -rf META-INF output rom system system_') 
    os.system('rm -rf *.img ')
    os.system('rm payload.bin system.new.dat.br system.transfer.list system.new.dat')