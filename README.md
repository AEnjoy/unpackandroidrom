# Rom处理工具(Python)

此项目使用Python语言,一键解包安卓ROM的system.img

(开发中 累)

支持格式:

> .new.dat.  .new.dat.br  .img  .tar.md5  .ozip  .kdz  .dz  .bin  .zip  .tar

其中,ozip,new.dat(.br),img,payload.bin,以及部分zip可以一键解包出system.

同时,还可以嗅探某些ROM的底层(魅族 魅蓝note5/6 嗅探底层成功)

支持几乎除了安卓10动态分区外的所有卡刷包,以及三星,LG线刷包,ozip解密等

特点:将众多开源项目涵盖在了一个项目中,方便ROM的解包操作及寻找开源项目

(若main处理不了,你还可以用其它的,不过会略微麻烦就是了)



测试结果:→[前往观赏测试图](pic)

可以正常识别目前我见到的卡刷包

oppo ozip解密解包功能正常(仅部分机型)(含.new.dat.br)

三星官方tar.md5解包system正常

魅族 new.dat解包正常

360 普通打包方式解包正常

Google AB payload.bin解包正常

LG KDZ解包正常

(暂未添加DZ解包)

食用步骤:

Clone该项目:

```
git clone --depth=1 https://hub.fastgit.org/AEnjoy/unpackandroidrom.git
```

安装依赖:

```
python3 install_requirements.py
```

运行:

```
python3 main.py
```

(提交bug -_-||,无情嘲讽)

可选操作:

定期执行-清理缓存

```
python clean_cache.py
```

定期执行-项目同步

```
git pull
```

![img](pic/home.png)

本项目引用的项目(文件)列表及来源:

oppoozip:https://github.com/tahirtaous/ozip2zip
~~extract_android_ota_payload:https://github.com/cyxx/extract_android_ota_payload~~
sdat2img:https://github.com/xpirt/sdat2img
rimg2sdat:https://github.com/jazchen/rimg2sdat
LGKDZ:https://github.com/randomstuffpaul/kdztools
PayloadDumperOnDocker:https://github.com/matze19999/PayloadDumperOnDocker

运行环境需求:

Python2.7/Python3.6+

运行依赖包含在requirements.txt文件中,你可以运行install_requirements.py 一键安装依赖

Changes:

```
2→2.1:2020-8-16 13:19:14
1.修复了一个小bug

1→2:2020-8-15 21:58:28
1.更新lz4,brotli解包代码
2.更新依赖(可能需要重新运行install_requirements.py)
3.LG DZ解包支持(之前只支持查看)
4.MIUI线刷包解包
```

根据上游开源,本项目开源许可协议为GNU/GPL3