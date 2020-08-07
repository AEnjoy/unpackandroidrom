#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   adbshellpy_libunpakrom
#       By : 神郭
#  Version : 1.0
import sys,os,zipfile,urllib.request,tarfile,argparse

#sys.path.append(os.path.join(sys.path[0], "libromparse"))
import undz,unkdz,ozipdecrypt,rimg2sdat,sdat2img,payload_dumper

def get_saminfo(filename='AP_G9650ZCS6CSK2_CL17051143_QB26966166_REV01_user_low_ship_MULTI_CERT_meta_OS9.tar.md5',l=-1):
    """
    get samsumg rom info
    :return: last line or None for empty file
    """
    try:
        filesize = os.path.getsize(filename)
        if filesize == 0:
            return None
        else:
            with open(filename, 'rb') as fp:
                offset = -8
                while -offset < filesize:
                    fp.seek(offset, 2)
                    lines = fp.readlines()
                    if len(lines) >= 2:
                        print('a')
                        return lines[l]
                    else:
                        offset *= 2
                fp.seek(0)
                lines = fp.readlines()
                print('b')
                return lines[l]
    except FileNotFoundError:
        print(filename + ' 未找到!')
        return None

class adbshellpyinformation():
    import platform
    p=platform.system()
    try:from adbshell_alpha import branch
    except:
        try:from adbshell import branch
        except:branch='dev'
    uselinuxpkgmanagertoinstalladb=None
    adbfile=None
    aapt=None
    conf=None

class rominformation:
    '''
    brotli=None
    newdat=None
    olnyimg=None
    onlyfolder=None
    ozip=None
    androidVersion=
    flag:
    1.无效文件路径
    2.不支持格式
    3.线刷包找到
    4.卡刷包找到 ROM
    5.卡刷包找到 flashable
    '''
    type=None #1功能性卡刷包(如opengapps) 2ROM卡刷包 3线刷包
    def __init__(self,file=''):
        print('正在处理ROM信息...')
        '''获取ROM信息 输入的文件可以是线刷包,也可以是卡刷包'''
        size=os.path.getsize(file)
        if os.path.exists(file)==False or size==0:
            print('E:请选择一个正确的文件!!!')
            self.flag=1#无效文件路径
            return
        if file.find('payload.bin')>-1:
            self.abflag=True
            self.flag=3
            print('发现A/B(System As Root)更新文件(安卓10动态分区)')
            return
        if zipfile.is_zipfile(file)==False:
            if file.find('.kdz') > -1:
                print('May:发现LG .kdz文件!\n正在测试是否为 .kdz文件...')
                if lg_kd_kdz(file).islgkdzfile():
                    self.lgkdz=True
                    self.flag=3
                    self.type=3
                    print('发现LG .kdz文件!')
                    return
                else:
                    print('这个文件可能不是LG .kdz文件?')
                    self.flag=2
                    return
            if file.find('.dz') > -1:
                print('May:发现LG .dz文件!\n正在测试是否为 .dz文件...')
                if lg_kd_kdz(file).islgdzfile():
                    self.lgkd=True
                    self.flag=3
                    self.type=3  
                    print('发现LG .dz文件!')
                else:
                    print('这个文件可能不是LG .dz文件?')
                    self.flag=2                    
                    return
            print('无效不可读格式?')
            self.flag=2
            return
        if file.find('.ozip') > -1 and zipfile.is_zipfile(file)==True:
            with open(file,'rb') as fr:
                magic=fr.read(12)
                if magic==b"OPPOENCRYPT!" or magic[:2]==b"PK":
                    self.ozip=True
                    print('发现OPPO OZIP! 需要解密后才能读取ROM信息')
                fr.close()
                return
            print('这个ROM可能不是OPPO OZIP?!')
        if file.find('.tar.md5') > -1 and tarfile.is_tarfile(file):
            self.samsumgodinfile=True
            a=str(get_saminfo(file))
            if a:
                a=a.replace("b'",'')
                a=a.replace(".tar\\n'",'')
                li=a.split(' ')
                a=li[2].split('_')
                print('ROM类型:'+a[0]+'\n版本:'+a[1]+'\n发行标志:'+a[5]+'\n固件类型:offical')
                print('发现三星odin线刷文件!')
                return
            print('May:发现三星odin线刷文件?!')
        if zipfile.is_zipfile(file)==False:
            print('E:不支持的格式!!!!')
            self.flag=2
            return
        self.file=file
        z=zipfile.ZipFile(file)
        self.l=z.namelist()
        self.flag=4
        #z.close()
        if 'system.img' in self.l:
            self.olnyimg=True

        if 'system/framework/framework.jar' in self.l:
            self.onlyfolder=True

        if 'system.new.dat.br' in self.l and 'system.transfer.list' in self.l:
            self.brotil=True

        if 'system.new.dat' in self.l and 'system.transfer.list' in self.l:
            self.newdat=True

        if 'system.transfer.list' in self.l:
            z.extract('system.transfer.list')
            f = open('system.transfer.list', 'r')
            v = int(f.readline())
            f.close()
            if v == 1:
                print('Android Lollipop 5.0 检测到!\n')
                self.androidVersion='Lollipop 5.0 API 21'
            elif v == 2:
                print('Android Lollipop 5.1 检测到!\n')
                self.androidVersion='Lollipop 5.1 API 22'
            elif v == 3:
                print('Android Marshmallow 6.x 检测到!\n')
                self.androidVersion='Marshmallow 6.x API 23'
            elif v == 4:
                print('Android Nougat 7.x / Oreo 8.x 或更高版本检测到!\n')
                self.androidVersion='Nougat 7.x or higher API 24+'

        if 'payload.bin' in self.l:
            self.abflag=True
            self.flag=4
            print('发现A/B(System As Root)更新文件(安卓10动态分区)')
            if 'META-INF/com/android/android/metadata' in self.l:
                z.extract('META-INF/com/android/android/metadata')
                f=open('META-INF/com/android/android/metadata')
                l=[]
                for i in f:l.append(i.strip())
                f.close()
                os.remove('META-INF/com/android/android/metadata')
                for i in l:
                    x=i.split('=')
                    if x[0]=='post-build':
                        text=x[1]
                        self.info=text.split('/')
                        if len(self.info)==6:
                            print('ROM制造商:'+self.info[0]+'\n手机代号:'+self.info[1]+'\n版本:'+self.info[2]+'\nAndroid开发版本:'+self.info[3]+'\n固件版本:'+self.info[4]+'\n发行标志:'+self.info[5])
                            z.close()
                            return
                        else:
                            print('您的设备指纹可能已经被修改,无法获取ROM信息!!!')
            else:
                print('metadata文件不存在?!')
                z.close()
                return

        for names in self.l:#prop获取Android版本
            if names.find('build.prop') > -1:
                try:z.extract(names)
                except:pass
                if os.path.exists(names):
                    f=open(names)
                    l=[]
                    for i in f:l.append(i.strip())
                    f.close()
                    os.remove(names)
                    for i in l:
                        x=i.split('=')
                        '''
                        if x[0]=='ro.build.version.sdk':
                            try:
                                sdk=int(x[1])
                                if sdk < 21:print('W:您处理的ROM太老旧了哦,不支持显示版本及代号,仅支持显示API版本')
                                elif sdk==21:self.androidVersion='Lollipop 5.0'
                                elif sdk ==22:self.androidVersion='Lollipop 5.1'
                                elif sdk ==23:self.androidVersion='Marshmallow 6.0'
                                elif sdk ==24:self.androidVersion='Nougat 7.0'
                                elif sdk ==25:self.androidVersion='Nougat 7.1'
                                elif sdk ==26:self.androidVersion='Oreo 8.0'
                                elif sdk ==27:self.androidVersion='Oreo 8.1'
                                elif sdk ==28:self.androidVersion='Pie 9.0'
                                elif sdk ==29:self.androidVersion='Q 10.0'
                                elif sdk ==30:self.androidVersion='R 11.0'
                                self.androidVersion=self.androidVersion+ ' API: '+x[1]
                            except:print('E:你目前处理的ROM似乎是开发者内侧版或被修改成了错误的值.')
                        '''
                        if x[0]=='ro.build.fingerprint':#Android 指纹库
                            text=x[1]
                            self.info=text.split('/')
                            if len(self.info)==6:
                                print('ROM制造商:'+self.info[0]+'\n手机代号:'+self.info[1]+'\n版本:'+self.info[2]+'\nAndroid开发版本:'+self.info[3]+'\n固件版本:'+self.info[4]+'\n发行标志:'+self.info[5])
                                z.close()
                                return
                            else:
                                print('您的设备指纹可能已经被修改,无法获取ROM信息!!!')

        if 'META-INF/com/google/android/updater-script' in self.l:
            z.extract('META-INF/com/google/android/updater-script')
            f=open('META-INF/com/google/android/updater-script')
            l=[]
            for i in f:l.append(i.strip())
            f.close()
            os.remove('META-INF/com/google/android/updater-script')
            for i in l:
                if 'ui_print("Target:' in i:
                    i=i.replace('ui_print("Target:','')
                    i=i.replace('");','')
                    i=i.replace(' ','')
                    self.info=i.split('/')
                    if len(self.info)==6:
                        print('ROM制造商:'+self.info[0]+'\n手机代号:'+self.info[1]+'\n版本:'+self.info[2]+'\nAndroid开发版本:'+self.info[3]+'\n固件版本:'+self.info[4]+'\n发行标志:'+self.info[5])
                        z.close()
                        return
                if (i.find('update-binary') > -1 and i.find('ummy') > -1) or  i.find('#MAGISK') > -1:
                    self.flag=5
                    print('发现该压缩包为功能性卡刷包!(Magisk/oepngapps/ak2/ak3/etc.')
                    z.close()
                    return
            print('W:无法从updater-script获取ROM信息!!')
        z.close()

def lz4install():
    if adbshellpyinformation().p=='Linux':
        os.system('sudo apt install lz4 -y')
        os.system('sudo dnf install lz4 -y')
    else:
        if os.path.exists('lz4.exe')==False:
            urllib.request.urlretrieve('https://github.wuyanzheshui.workers.dev/lz4/lz4/releases/download/v1.9.2/lz4_win32_v1_9_2.zip','lz4.zip')
            z=zipfile.ZipFile('lz4.zip')
            z.extract('lz4.exe')
            z.close()
    return
class lg_kd_kdz():
    def __init__(self,file):
        """
        GitHub Paper:https://github.com/randomstuffpaul/kdztools
        Copyright (C) 2016 Elliott Mitchell <ehem+android@m5p.com>
        Copyright (C) 2013 IOMonster (thecubed on XDA)
	    This program is free software: you can redistribute it and/or modify
	    it under the terms of the GNU General Public License as published by
	    the Free Software Foundation, either version 3 of the License, or
	    (at your option) any later version.
	    This program is distributed in the hope that it will be useful,
	    but WITHOUT ANY WARRANTY; without even the implied warranty of
	    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	    GNU General Public License for more details.
	    You should have received a copy of the GNU General Public License
	    along with this program.  If not, see <http://www.gnu.org/licenses/>.
        file 输入的文件(kdz/kd)
        """
        if os.path.exists(file)==False:
            print('E:无效文件路径!')
            return
        self.file=file
    def islgkdzfile(self):
        kdz=unkdz.KDZFileTools()
        kdz.kdzfile=self.file
        try:
            kdz.openFile(self.file)
            l=kdz.getPartitions()
            if len(l) !=0:return True
            else:return False
        except:return False

    def islgdzfile(self):
        dz=undz.DZFileTools()
        try:
            dz.dz_file=undz.UNDZFile(self.file)
            dz.cmdListPartitions()
            return True
        except:return False
            #dz.

class unpackrom():
    file=''
    unpacktodir=1
    def __init__(self,file,rominfo,unpacktodir=1,check=0):
        '''file:inputfile unpacktodir 0/1 0:Only run onec ;1 only to system dir check:lib 0/1'''
        self.rominfo=rominfo
        if file==False:self.file=rominfo.file
        else:self.file=file
        self.unpacktodir=unpacktodir
        if check==1:
            print('正在安装依赖...')
            import install_requirements
        a=input('ROM解析完成.是否解包?y/n>>>')
        if a=='y':
            pass
            '''
            if rominfo.abflag==True:self.abunpack()
            if rominfo.samsumgodin==True:self.samsumg_tar()
            if rominfo.lgkdz==True:self.lg_kdz()
            if rominfo.ozip==True:self.oppo_ozip()
            '''
        elif a=='n':print('用户取消')
    
    def samsumg_tar(self):
        tar=tarfile.open(self.file)
        tar.extractall(path='rom')
        tar.close()
        lz4install()
        if adbshellpyinformation.p=='Windows':
            os.system('for %%a in (rom\\*.lz4) do lz4 -d %%a')
            os.system('for %%a in (rom\\*.lz4) do del /f/s/q %%a')
        else:
            os.system('find ./rom -name *.lz4  |xargs lz4 -d')
            os.system('find ./rom -name *.lz4  |xargs rm ')
        if os.path.exists('/rom/system.img.ext4') and self.unpacktodir==1:
            self.file='/rom/system.img.ext4'
            self.imgunpack()
    def lg_kdz(self):
        print('当a,b同时为y时,将提取出dz后再列出dz文件分区表,否则当a=y,b=n时,将列出kdz内文件分列表')
        a=input('a:是否仅列出.dz分区列表?(默认n)y/n')
        b=input('b:是否完整解包(自动解包.dz)(默认y)?y/n')
        c=input('c:欲解包的分区序号:(默认全部Enter)')
        d=input('d:是否解包出分片文件?(默认n)y/n')
        if a=='n' and b=='y':
            pass
    def oppo_ozip(self):
        pass
    def unzip(self):
        if info.flag==1:return
        if info.flag==2:
            #专属格式解包
            pass
        if self.rominfo.abflag==True:
            extract_android_ota_payload.main(self.file,'rom')
            if self.unpacktodir==1:
                if os.path.exists('/rom/system.img'):
                    self.file='/rom/system.img'
                    self.imgunpack()
                if os.path.exists('/rom/system_a.img'):
                    self.file='/rom/system_a.img'
                    self.imgunpack()                
                if os.path.exists('/rom/surper.img'):print('暂不支持动态分区!')
        z=zipfile.ZipFile(self.file)
        z.extractall('rom')
        z.close()
        if self.unpacktodir==0:
            print('Done! 输出的到的目录: /rom')
            return
        else:pass
    def abunpack(self):
        extract_android_ota_payload.main(self.file,'rom')
        if self.unpacktodir==1:
            if os.path.exists('/rom/system.img'):
                self.file='/rom/system.img'
                self.imgunpack()
            if os.path.exists('/rom/system_a.img'):
                self.file='/rom/system_a.img'
                self.imgunpack()                
            if os.path.exists('/rom/surper.img'):print('暂不支持动态分区!')        
    def imgunpack(self,flag=1):
        '''flag: 1mount 2unmount Linux'''
        if adbshellpyinformation.p=='Linux':
            if flag==1:
                os.system('mkdir android-system-img')
                os.system('sudo mount %s android-system-img'%self.file)
                print('Done!: 挂载镜像到文件夹 android-system-img')
            if flag==2:
                os.system('sudo umount android-system-img')
                os.system('e2fsck -p -f '+self.file)
                os.system('resize2fs -M '+self.file)
                print('Done!: 保存的镜像 '+self.file)
        if adbshellpyinformation.p=='Windows':
            url='https://hub.fastgit.org/AEnjoy/adbshellpy/raw/master/Imgextractor.exe'
            if os.path.exists('Imgextractor.exe')==False:
                try:urllib.request.urlretrieve(url,'Imgextractor.exe')
                except:
                    print('E:下载失败!')
                    return
            os.system('Imgextractor '+self.file)
            print('Done!')

    def newdatunpack(self,TRANSFER_LIST_FILE='system.transfer.list', NEW_DATA_FILE='system.new.dat', OUTPUT_IMAGE_FILE='system.img'):
        #====================================================
        #          FILE: sdat2img.py
        #       AUTHORS: xpirt - luxi78 - howellzhu
        #          DATE: 2018-10-27 10:33:21 CEST
        #       Chinese: 神郭
        #====================================================
        sdat2img.main(TRANSFER_LIST_FILE,NEW_DATA_FILE,OUTPUT_IMAGE_FILE)
        if self.unpacktodir==1:
            self.file=OUTPUT_IMAGE_FILE
            self.imgunpack()
        

    def brotli(self,INPUT_FILE='system.new.dat.br',OUTPUT_FILE='system.new.dat',flag=1):
        import brotli as b
        if flag==1:
            f=open(INPUT_FILE)
            f=b.decompress(f.read())
            ofile=open(OUTPUT_FILE, 'wb')
            os.write(ofile,f)
            f.close()
            ofile.close()
            sys.exit()
        if flag==2:
            f=open(INPUT_FILE)
            f=b.compress(f.read())
            ofile=open(OUTPUT_FILE, 'wb')
            os.write(ofile,f)
            f.close()
            ofile.close()
            sys.exit()
        print('参数无效!')

def parseArgs():
    parser = argparse.ArgumentParser(description='ROM解包大师')
    parser.add_argument('-f', '--file', help='欲解包的ROM文件', action='store', required=False, dest='file')
    parser.add_argument("-t", "--type", type=str, choices=['kdz', 'dz', 'samsumgodin','abota','flashable','ozip'], help="强制指定输入的文件ROM的类型", required=False)
    return parser.parse_args()
def main(args=None):
    if os.path.exists('rom')==False:os.mkdir('rom')
    if args.file:rom=rominformation(args.file)
    else:rom=rominformation(input('请选择一个处理的ROM>>>'))
    if args.type=='kdz':rom.lgkdz=True
    elif args.type=='dz':rom.lgkd=True
    elif args.type=='samsumgodin':rom.samsumgodinfile=True
    elif args.type=='abota':rom.abflag=True
    elif args.type=='ozip':rom.ozip=True
    elif args.type=='flashable':pass
    unpackrom(args.file,rom)
if __name__ == '__main__':
    args=parseArgs()
    main(args)
    