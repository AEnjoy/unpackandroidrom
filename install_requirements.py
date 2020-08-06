#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
执行此文件将自动安装requirements.txt中的依赖
'''
import sys
f=open('requirements.txt')
for i in f:os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple '+i)
f.close()
