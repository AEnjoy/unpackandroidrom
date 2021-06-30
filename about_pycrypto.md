# pycrypto依赖可能遇到的安装问题

## 1.error: Microsoft Visual C++ 14.0 is required. Get it with "Build Tools for Visual Studio"

下载Build Tools for Visual Studio:

https://visualstudio.microsoft.com/downloads/

## 2.winrand.c ... ..\pyconfig.h(59): fatal error C1083: 无法打开包括文件: “io.h”: No such file or directory

安装完整Visual Studio,选择c/c++桌面开发

## 3.其它问题

### 1.提交issue给我

### 2.安装pycryptodome

### 3.不能定义Crypto?No Module named Crypto

> #### 找到你的python包的安装目录,
>
> #### lib\site-packages把crypto改为Crypto

# 替代方案

安装pycryptodome

打开requirements.txt,将pycrypto更改为pycryptodome

