#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   adbshellpy_libunpakrom
#       By : AEnjoy
#  Version : 2.2.5
# last Update: 2024-7-7 17:38:01
try:import sys,os,zipfile,urllib.request,tarfile,argparse,platform,lz4.frame,glob2,undz,unkdz,sdat2img,payload_dumper,simg2img
except ImportError:
    print('E:请执行install_requirements.py后再执行main!')
    input('按Enter键退出')
    exit(1)
ozipmodelerror=0
try:import ozipdecrypt
except ImportError:
    print('W:pycrypto依赖未安装,oppo ozip解包将不可用')
    ozipmodelerror=1
    
quiet=0 #0询问 1安静

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
    flag=0
    olnyimg,onlyfolder,brotil,newdat,samsumgodinfile,ozip,lgkd,lgkdz,abflag,miuitar=False,False,False,False,False,False,False,False,False,False
    def __init__(self,file=''):
        print('正在处理ROM信息...该过程需要1s-2min分钟不等')
        '''获取ROM信息 输入的文件可以是线刷包,也可以是卡刷包'''
        size=os.path.getsize(file)
        if os.path.exists(file)==False or size==0:
            print('E:请选择一个正确的文件!!!')
            self.flag=1#无效文件路径
            return
        self.file=file
        if file.find('payload.bin')>-1:
            self.abflag=True
            self.flag=3
            print('发现A/B(System As Root)更新文件(安卓10动态分区)')
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
                print('W:只有ROM类型为AP才支持解包出系统镜像')
                return
            print('Maybe:发现三星odin线刷文件?!')
        if file.find('.tgz') > -1 and tarfile.is_tarfile(file):
            #MIUI
            tar = tarfile.open(file, "r:gz")
            l=tar.getnames()
            for a in l:
                if a.find('system.img')>-1 :
                    self.flag=3
                    self.miuitar=True
                    print('Maybe:MIUI 线刷包找到')
                    return
                elif a.find('super.img')>-1:
                    self.flag=3
                    self.miuitar=True
                    self.super=True
                    print('Maybe:MIUI 线刷包找到')                    
                    return
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
            os.remove('system.transfer.list')
        if 'payload.bin' in self.l:
            self.abflag=True
            self.flag=4
            print('发现A/B(System As Root)更新文件(安卓10动态分区)')

        if 'META-INF/com/android/metadata' in self.l:
            z.extract('META-INF/com/android/metadata')
            f=open('META-INF/com/android/metadata', encoding='UTF-8')
            l=[]
            for i in f:l.append(i.strip())
            f.close()
            os.remove('META-INF/com/android/metadata')
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
            

        for names in self.l:#prop获取Android版本
            if names.find('build.prop') > -1:
                try:z.extract(names)
                except:pass
                if os.path.exists(names):
                    f=open(names, encoding='UTF-8')
                    l=[]
                    for i in f:l.append(i.strip())
                    f.close()
                    os.remove(names)
                    for i in l:
                        x=i.split('=')
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
            f=open('META-INF/com/google/android/updater-script', encoding='UTF-8')
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
        if zipfile.is_zipfile(file)==False:
            if file.find('.kdz') > -1:
                print('Maybe:发现LG .kdz文件!\n正在测试是否为 .kdz文件...')
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
                print('Maybe:发现LG .dz文件!\n正在测试是否为 .dz文件...')
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
        z.close()

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
    def unpackkdz(self):#all
        kdz=unkdz.KDZFileTools()
        kdz.kdzfile=self.file
        kdz.openFile(self.file)
        kdz.outdir=os.getcwd()
        kdz.partList=kdz.getPartitions()
        kdz.cmdExtractAll()
    def listkdz(self):#all
        kdz=unkdz.KDZFileTools()
        kdz.kdzfile=self.file
        kdz.openFile(self.file)
        kdz.cmdListPartitions()
    def unpackdz(self,mode=1):
        '''
        mode:
        1 USE COMMAND TO EXTRACT
        2 USE PYTHON FUNCTION
        '''
        if mode==2:
            dz=undz.DZFileTools()
            dz.mainbyclass(self.file,'rom')
        elif mode==1:
            os.system('python undz.py -f %s -i -d rom'%self.file)            

class unpackrom():
    global quiet
    file=''
    unpacktodir=1
    def __init__(self,file,rominfo,unpacktodir=1,check=0):
        '''file:inputfile unpacktodir 0/1 0:Only run onec ;1 only to system dir check:lib 0/1'''
        self.rominfo=rominfo
        if file!='':self.file=rominfo.file
        else:self.file=file
        self.unpacktodir=unpacktodir
        if check==1:
            print('正在安装依赖...')
            import install_requirements
        a=input('ROM解析完成.是否解包?y/n>>>')
        if a=='y':
            if rominfo.abflag==True and zipfile.is_zipfile(self.file)==True:self.unzip()
            if rominfo.miuitar==True:self.miui_tar()
            if rominfo.samsumgodinfile==True:self.samsumg_tar()
            if rominfo.lgkdz==True:self.lg_kdz()
            if rominfo.lgkd==True:self.lg_dz()
            if rominfo.flag==5 or rominfo.flag==4:self.unzip()
            if rominfo.ozip==True:self.oppo_ozip()
            if rominfo.abflag==True:self.abunpack()#.bin
        elif a=='n':print('操作已取消')
    def miui_tar(self):
        if quiet==0:
            if input('是否解包XiaomiTarFile?y/n>>>')=='n':return
        tar=tarfile.open(self.file)
        tar.extractall(path='rom')
        tar.close()
        print('Done.')
        items = os.listdir('rom')
        dir='rom/'
        if len(items)==1:
            dir=dir+items[0]+'/'
            items = os.listdir(dir)
            for i in items:
                if i.find('images')>-1:
                    dir=dir+i+'/'
                    if os.path.exists(dir+'super.img'):
                        print('MIUI:发现线刷包动态分区镜像.')
                        imgfile = dir+'super.img'
                    if os.path.exists(dir+'system.img'):
                        imgfile = dir+'system.img'
            self.file=imgfile
            self.imgunpack()
        
    def samsumg_tar(self):
        if quiet==0:
            if input('是否解包SamsungTarFile?y/n>>>')=='n':return
        tar=tarfile.open(self.file)
        tar.extractall(path='rom')
        tar.close()
        #lz4File
        lz4file = glob2.glob('rom/*.lz4')
        for a in lz4file:
            #a:input_file b:output_file char
            b=a.replace('.img.lz4','.img')
            with open(a, 'rb') as infile:
                data=infile.read()
                newdata = lz4.frame.decompress(data)
                outfile = open(b, 'wb')
                outfile.write(newdata)
                outfile.close()
            infile.close()
        if os.path.exists('rom/super.img') and self.unpacktodir==1:
            print('W:动态分区解包有待测试')
            self.file='rom/super.img'
            self.imgunpack()
        if os.path.exists('rom/system.img') and self.unpacktodir==1:
            self.file='rom/system.img'
            self.imgunpack()
        if os.path.exists('rom/system.img.ext4') and self.unpacktodir==1:
            self.file='rom/system.img.ext4'
            self.imgunpack()        
    def lg_kdz(self):
        if quiet==0:
            if input('是否解包LG KDZ?y/n>>>')=='n':return        
            print('当a,b同时为y时,将列出kdz文件分区表并解包,否则当a=y,b=n时,将仅列出kdz内文件列表')
            a=input('a:是否仅列出.kdz分区列表?(默认n)y/n')
            b=input('b:是否解包kdz全部文件(默认y)?y/n')
            c=input('c:欲解包的分区序号:(默认全部Enter)[暂不可用]')
        elif quiet==1:
            a,b='y','y'
        if a=='y' and b=='y':lg_kd_kdz(self.file).unpackkdz()
        elif a=='y' and b=='n':lg_kd_kdz(self.file).listkdz()
    def lg_dz(self):
        if quiet==0:
            if input('是否解包LG DZ?y/n>>>')=='n':return
            a=int(input('请选择解包模式:1.command 2.func:'))
        elif quiet==1:
            a=1
        lg_kd_kdz(self.file).unpackdz(a)

    def oppo_ozip(self):
        global ozipmodelerror
        if quiet==0:
            if input('是否解密oppo ozip?y/n>>>')=='n':return
        if ozipmodelerror==1:
            print('''
            E:pycrypto模块错误!不支持oppo ozip解包!
            有关pycrypto安装信息,请浏览:
            https://github.com/AEnjoy/unpackandroidrom/blob/master/about_pycrypto.md
            https://hub.fastgit.org/AEnjoy/unpackandroidrom/blob/master/about_pycrypto.md
            ''')
            return
        ozipdecrypt.main(self.file)
        self.file=self.file.replace('.ozip','.zip')
        z=zipfile.ZipFile(self.file)
        if 'system.new.dat.br' in z.namelist() and 'system.transfer.list' in z.namelist():self.rominfo.brotil=True
        else:self.rominfo.newdat=True
        rominformation(self.file)
        self.unzip()
    def unzip(self):#system.img
        if self.rominfo.flag==1:
            print('无效格式!!!')
            sys.exit(1)
        if quiet==0:
            if input('是否解包卡刷包zip文件?y/n>>>')=='n':
                print('取消.')
                sys.exit(0)           
        if self.rominfo.flag==5:
            z=zipfile.ZipFile(self.file)
            z.extractall(path='flashable')
            z.close()
            print('功能性卡刷包解包完成.输出目录:flashable')
            print('Done.')
            sys.exit(0)
        if self.rominfo.abflag==True and zipfile.is_zipfile(self.file)==True:          
            z=zipfile.ZipFile(self.file)
            z.extract('payload.bin')
            z.close()
            self.file='payload.bin'
            self.abunpack()
            print('Done.')
            sys.exit(0)
        if self.rominfo.onlyfolder==True:
            z=zipfile.ZipFile(self.file)
            for name in z.namelist() :
                if name.find('system')==0:
                    z.extract(name)
            z.close()
            print('Done.')
            sys.exit(0)
        if self.rominfo.olnyimg==True:
            z=zipfile.ZipFile(self.file)
            z.extract('system.img')
            z.close()
            if self.unpacktodir==1:
                self.file='system.img'
                self.imgunpack()
            print('Done.')
            sys.exit(0)
        if self.rominfo.brotil==True:
            z=zipfile.ZipFile(self.file)
            z.extract('system.transfer.list')
            z.extract('system.new.dat.br')
            z.close()
            self.brotli()
            self.newdatunpack()
            if self.unpacktodir==1:
                self.file='system.img'
                self.imgunpack()
            print('Done.')
            sys.exit(0)
        if self.rominfo.newdat==True:
            z=zipfile.ZipFile(self.file)
            z.extract('system.transfer.list')
            z.extract('system.new.dat')
            z.close()
            self.newdatunpack()
            if self.unpacktodir==1:
                self.file='system.img'
                self.imgunpack()
            print('Done.')
            sys.exit(0)
        if self.unpacktodir==0:
            print('Done! 输出的到的目录: /')
            return
        else:pass

    def abunpack(self):
        if quiet==0:
            if input('是否解密payload.bin?y/n>>>')=='n':return
        if os.path.exists('output')==False:os.mkdir('output')
        payload_dumper.main(self.file)
        try:os.remove(self.file)
        except:pass
        if self.unpacktodir==1:
            if os.path.exists('output/system.img'):
                self.file='output/system.img'
                self.imgunpack()
            if os.path.exists('output/system_a.img'):
                self.file='output/system_a.img'
                self.imgunpack()
            if os.path.exists('output/surper.img'):
                self.file='output/surper.img'
                print('W:动态分区有待测试!')
                self.imgunpack()
    def imgunpack(self,flag=1):
        '''flag: 1mount 2unmount Linux'''
        if quiet==0:
            if input('是否解包.img?y/n>>>')=='n':return
        if self.file.find('super.img')>-1:
            print('''W:暂不支持解包动态分区super.img文件!
            正在转换super.img...以便手动解包
            ''')
            a=''
            simg2img.main(self.file,a)
            print('输出的文件:'+a)
            return
        if platform.system()=='Linux':
            if flag==1:
                os.system('mkdir android-system-img')
                os.system('sudo mount %s android-system-img'%self.file)
                print('Done!: 挂载镜像到文件夹 android-system-img')
            if flag==2:
                os.system('sudo umount android-system-img')
                os.system('e2fsck -p -f '+self.file)
                os.system('resize2fs -M '+self.file)
                print('Done!: 保存的镜像 '+self.file)
        if platform.system()=='Windows':
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
        if quiet==0:
            if input('是否转换.new.dat?y/n>>>')=='n':return              
        sdat2img.main(TRANSFER_LIST_FILE,NEW_DATA_FILE,OUTPUT_IMAGE_FILE,0)

    def brotli(self,INPUT_FILE='system.new.dat.br',OUTPUT_FILE='system.new.dat',flag=1):
        import brotli as b
        if quiet==0:
            if input('是否转换.new.dat.br?y/n>>>')=='n':return           
        if flag==1:
            with open(INPUT_FILE, 'rb') as infile:
                data = infile.read()
                outfile = open(OUTPUT_FILE, 'wb')
                data = b.decompress(data)
                outfile.write(data)
                outfile.close()
                infile.close()
        if flag==2:
            with open(INPUT_FILE, 'rb') as infile:
                data = infile.read()
                outfile = open(OUTPUT_FILE, 'wb')
                data = b.compress(data)
                outfile.write(data)
                outfile.close()
                infile.close()
        print('参数无效!')

def parseArgs():
    parser = argparse.ArgumentParser(description='System一键解包工具')
    parser.add_argument('-f', '--file', help='欲解包的ROM文件', action='store', required=False, dest='file')
    parser.add_argument("-t", "--type", type=str, choices=['kdz', 'dz', 'samsumgodin','abota','flashable','ozip','miuitar','newdat','newdatbr'], help="强制指定输入的文件ROM的类型", required=False)
    parser.add_argument('-q', '--quiet', help='安静模式 不询问yes', action='store_true', required=False, dest='quit')
    parser.add_argument('-v', '--version', help='显示程序版本信息', action='store_true', required=False, dest='version')
    return parser.parse_args()
def main(args=None):
    global quiet
    if os.path.exists('rom')==False:os.mkdir('rom')
    if args.file:rom=rominformation(args.file)
    if args.version:
        print('Android ROM Unpack Tool \r\n 安卓ROM解包工具 \r\n Version:2.2.4 \r\n BuildDate: 2021-8-22 19:09:49')
        sys.exit(0)
    else:
        file=input('请选择一个处理的ROM>>>')
        if file=='':
            print('E:请选择一个ROM文件!')
            exit(1)
        elif os.path.exists(file):rom=rominformation(file)
        else:
            print('E:请选择一个ROM文件!')
            exit(1)            
    if args.type=='kdz':rom.lgkdz=True
    elif args.type=='dz':rom.lgkd=True
    elif args.type=='samsumgodin':rom.samsumgodinfile=True
    elif args.type=='abota':rom.abflag=True
    elif args.type=='ozip':rom.ozip=True
    elif args.type=='flashable':rom.flag=5
    elif args.type=='miuitar':
        rom.miuitar=True
        rom.flag=3
    elif args.type=='newdat':rom.newdat=True
    elif args.type=='newdatbr':rom.brotil=True
    if args.quit:quiet=1
    unpackrom(args.file,rom)
if __name__ == '__main__':
    print('''
    **********************************libunpakrom*****************************************
    *                           Android ROM 智能解包工具箱 版本2.2.4                       *
    *       支持市面上绝大部分Android手机的ROM解包,未来更新后还将支持ROM打包等操作         *
    *       功能:                                                                         *
    *                     ①OPPO OZIP解密                                                  *
    *                     ②Android O+ A/B分区(System As Root) payload.bin 解包            *
    *                     ③Android Q+ 真(虚拟)动态分区payload.bin解包                        *
    *                     ④Android L+ .new.dat, .new.dat.br 转换img                       *
    *                     ⑤Android L+ 分区.img解包                                        *
    *                     ⑥常规解包,卡刷包解包.                                            *
    *                     ⑦部分ROM卡刷包支持直接读取ROM信息                                 *
    *                     ⑧Samsung odin .tar.md5 文件解包/获取ROM信息                      *
    *                      (仅官方.tar.md5文件支持) 解包.lz4→.img                          *
    *                     ⑨LG KDZ / DZ 文件解包                                           *
    *                     ⑩.tar线刷包解包                                                 *
    *       支持文件格式:                                                                 *
    *                     .img/.zip/.tar/.tar.gz/.tar.md5/.new.dat/.new.dat.br/          *
    *                     .kdz/.dz/.ozip/payload.bin/.tgz                                *
    *       项目地址:      https://github.com/AEnjoy/unpackandroidrom                     *
    *                                                                                    *
    **********************************libunpakrom*****************************************
    ''')
    args=parseArgs()
    main(args)
    