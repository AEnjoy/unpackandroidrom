#!/usr/bin/env python
# -*- coding: utf-8 -*-
#====================================================
#          FILE: sdat2img.py
#       AUTHORS: xpirt - luxi78 - howellzhu
#          DATE: 2018-10-27 10:33:21 CEST
#       Chinese: 神郭
#====================================================
'''
相对于原版的改进:
1.中文
2.Python3
3.如若当前路径下存在system.new.dat和system.transfer.list,则不需要输入命令直接运行
例:
./sdat2img.py
./sdat2img.py system.transfer.list system.new.dat
./sdat2img.py system.transfer.list system.new.dat system.img
'''
from __future__ import print_function
import sys, os, errno

def main(TRANSFER_LIST_FILE, NEW_DATA_FILE, OUTPUT_IMAGE_FILE,quiet=1):#quiet:0:enable 1:disable
    __version__ = '1.2'

    if sys.hexversion < 0x02070000:
        print >> sys.stderr, "需要Python 2.7或更新的版本."
        try:
            input = raw_input
        except NameError: pass
        input('按 ENTER 退出...')
        sys.exit(1)
    else:
        if quiet==1:
            print('sdat2img Version: {}\n'.format(__version__))

    def rangeset(src):
        src_set = src.split(',')
        num_set =  [int(item) for item in src_set]
        if len(num_set) != num_set[0]+1:
            print('以下数据分析到RangeSet时出错:\n {}'.format(src), file=sys.stderr)
            sys.exit(1)

        return tuple ([ (num_set[i], num_set[i+1]) for i in range(1, len(num_set), 2) ])

    def parse_transfer_list_file(path):
        trans_list = open(TRANSFER_LIST_FILE, 'r')

        # First line in transfer list is the version number
        version = int(trans_list.readline())

        # Second line in transfer list is the total number of blocks we expect to write
        new_blocks = int(trans_list.readline())

        if version >= 2:
            # Third line is how many stash entries are needed simultaneously
            trans_list.readline()
            # Fourth line is the maximum number of blocks that will be stashed simultaneously
            trans_list.readline()

        # Subsequent lines are all individual transfer commands
        commands = []
        for line in trans_list:
            line = line.split(' ')
            cmd = line[0]
            if cmd in ['erase', 'new', 'zero']:
                commands.append([cmd, rangeset(line[1])])
            else:
                # Skip lines starting with numbers, they are not commands anyway
                if not cmd[0].isdigit():
                    print('命令 "{}" 无效.'.format(cmd), file=sys.stderr)
                    trans_list.close()
                    sys.exit(1)

        trans_list.close()
        return version, new_blocks, commands

    BLOCK_SIZE = 4096
    
    version, new_blocks, commands = parse_transfer_list_file(TRANSFER_LIST_FILE)
    if quiet==1:
        if version == 1:
            print('Android Lollipop 5.0 检测到!\n')
        elif version == 2:
            print('Android Lollipop 5.1 检测到!\n')
        elif version == 3:
            print('Android Marshmallow 6.x 检测到!\n')
        elif version == 4:
            print('Android Nougat 7.x / Oreo 8.x 检测到!\n')
        else:
            print('Unknown Android version!\n')

    # Don't clobber existing files to avoid accidental data loss
    try:
        output_img = open(OUTPUT_IMAGE_FILE, 'wb')
    except IOError as e:
        if e.errno == errno.EEXIST:
            print('错误: 输出的文件 "{}" 已经存在'.format(e.filename), file=sys.stderr)
            print('移动它, 重命名它, 或选择一个不同的文件名.', file=sys.stderr)
            sys.exit(e.errno)
        else:
            raise

    new_data_file = open(NEW_DATA_FILE, 'rb')
    all_block_sets = [i for command in commands for i in command[1]]
    max_file_size = max(pair[1] for pair in all_block_sets)*BLOCK_SIZE

    for command in commands:
        if command[0] == 'new':
            for block in command[1]:
                begin = block[0]
                end = block[1]
                block_count = end - begin
                if quiet==1:
                    print('复制 {} 区段到位置 {}...'.format(block_count, begin))
                # Position output file
                output_img.seek(begin*BLOCK_SIZE)
                
                # Copy one block at a time
                while(block_count > 0):
                    output_img.write(new_data_file.read(BLOCK_SIZE))
                    block_count -= 1
        else:
            if quiet==1:
                print('跳过命令 {}...'.format(command[0]))

    # Make file larger if necessary
    if(output_img.tell() < max_file_size):
        output_img.truncate(max_file_size)

    output_img.close()
    new_data_file.close()
    print('完成! 输出的镜像文件:  {}'.format(os.path.realpath(output_img.name)))

if __name__ == '__main__':
    try:
        TRANSFER_LIST_FILE = str(sys.argv[1])
        NEW_DATA_FILE = str(sys.argv[2])
    except IndexError:
        print('\n用法: sdat2img.py [<transfer_list> <system_new_file>] [system_img]\n')
        print('    <transfer_list>: transfer list 文件')
        print('    <system_new_file>: system new dat 文件')
        print('    [system_img]: 输出 system 镜像\n\n')
        print('Visit xda thread for more information.\n')
        try:
            input = raw_input
        except NameError: pass
        if os.path.exists('system.new.dat') and os.path.exists('system.transfer.list'):
            NEW_DATA_FILE='system.new.dat'
            TRANSFER_LIST_FILE='system.transfer.list'
        else:
            input('按 ENTER 退出...')
            sys.exit()
    try:
        OUTPUT_IMAGE_FILE = str(sys.argv[3])
    except IndexError:
        OUTPUT_IMAGE_FILE = 'system.img'
    if sys.hexversion < 0x03000000:
        import time
        print('Warning:For better Chinese support, please use Python 3 or above.\n')
        print('The program will continue after 3s.\n')
        time.sleep(3)
    main(TRANSFER_LIST_FILE, NEW_DATA_FILE, OUTPUT_IMAGE_FILE)
