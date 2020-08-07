# Rom处理工具(Python)

此项目使用Python语言解包安卓ROM

(开发中 累)

支持几乎除了安卓10动态分区外的所有卡刷包,以及三星,LG线刷包,ozip解密等

支持格式:

> .new.dat.  .new.dat.br  .img  .tar.md5  .ozip  .kdz  .dz  .bin  .zip  .tar

特点:将众多开源项目涵盖在了一个项目中,方便操作及寻找

本项目引用的项目列表:

oppoozip:https://github.com/tahirtaous/ozip2zip
~~extract_android_ota_payload:https://github.com/cyxx/extract_android_ota_payload~~
sdat2img:https://github.com/xpirt/sdat2img
rimg2sdat:https://github.com/jazchen/rimg2sdat
LGKDZ:https://github.com/randomstuffpaul/kdztools
PayloadDumperOnDocker:https://github.com/matze19999/PayloadDumperOnDocker

运行环境需求:

Python2.7/Python3.6+

运行依赖包含在requirements.txt文件中,你可以运行install_requirements.py 一键安装依赖

根据上游开源,本项目开源许可协议为GNU/GPL3