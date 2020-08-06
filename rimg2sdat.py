#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#===================================
#    File: rimg2sdat.py
# Authors: jazchen
#    Date: 2018.07.05 17:39 CST
#===================================

"""
version == 1: Android Lollipop 5.0
version == 2: Android Lollipop 5.1
version == 3: Android Marshmallow 6.x
version == 4: Android Nougat 7.x / Oreo 8.x
"""

from __future__ import print_function

import os
import sys
import struct
import time


def GetRawImageFileHandle(filepath, image_size):
	image_name = os.path.basename(filepath)
	file_handle = open(filepath, 'rb')

	file_handle.seek(0x438)
	magic = struct.unpack("<H", file_handle.read(2))[0]

	if magic != 0xEF53 :
		print('%s 不是 ext4 文件系统.' % image_name)
		sys.exit(1)

	file_handle.seek(0x418)
	block_size = struct.unpack("<I", file_handle.read(4))[0]
	block_size = 2 ** (10 + block_size)

	if block_size != 4096 :
		print('%s block_size 必须是 4096.' % image_name)
		sys.exit(1)

	file_handle.seek(0x400)
	inodes_count = struct.unpack("<I", file_handle.read(4))[0]

	file_handle.seek(0x420)
	blocks_per_group = struct.unpack("<I", file_handle.read(4))[0]

	file_handle.seek(0x428)
	inodes_per_group = struct.unpack("<I", file_handle.read(4))[0]

	total_bytes = block_size * blocks_per_group * (inodes_count / inodes_per_group)
	if total_bytes != image_size:
		print('%s 分区大小错误.' % image_name)
		sys.exit(1)

	return file_handle


def SplitRangeSet(range_list, limit=0):
	if limit > 0 :
		streams = [(range_list[i], range_list[i+1]) for i in range(0, len(range_list), 2)]
		commands = []
		cmd_range = []

		counter = limit
		for begin, end in streams:
			length = end - begin

			while (length > 0) :
				if length > counter :
					cmd_range.append(begin)
					cmd_range.append(begin + counter)
					begin = begin + counter
					length -= counter
					counter = 0
				else:
					cmd_range.append(begin)
					cmd_range.append(end)
					counter -= length
					length = 0

				if counter == 0 :
					commands.append(tuple(cmd_range))
					cmd_range = []
					counter = limit
		else:
			if len(cmd_range) > 0:
				commands.append(tuple(cmd_range))

		return commands
	else:
		return [tuple(range_list)]


def WriteTransfers(prefix, version, rangeSet, write_blocks, total_blocks, nolimit=False):

	rangeSet['erase'] = []

	if version <= 2 :
		rangeSet['erase'].append(0)
		rangeSet['erase'].append(total_blocks)

	elif version >= 3 :
		range_zero = tuple(rangeSet['zero'])
		del rangeSet['zero'][:]

		for i in range(0, len(range_zero), 2):
			if (range_zero[i+1] - range_zero[i]) > 1024 :
				rangeSet['erase'].append(range_zero[i])
				rangeSet['erase'].append(range_zero[i+1])
			else:
				rangeSet['zero'].append(range_zero[i])
				rangeSet['zero'].append(range_zero[i+1])
		else:
			del range_zero


	if version == 4 and nolimit == False :
		rangeSet['new'] = SplitRangeSet(rangeSet['new'], 1024)
		rangeSet['zero'] = SplitRangeSet(rangeSet['zero'], 1024)
	else:
		rangeSet['new'] = SplitRangeSet(rangeSet['new'])
		rangeSet['zero'] = SplitRangeSet(rangeSet['zero'])


	with open(prefix + '.transfer.list', "w") as f:
		f.write(str(version) +'\n')
		f.write(str(write_blocks) +'\n')

		if version >= 2:
			f.write('0\n0\n')

		if len(rangeSet['erase']) > 0:
			f.write('erase ' + str(len(rangeSet['erase'])) + ',' +  ','.join(map(str,rangeSet['erase'])) +'\n')

		for cmd_range in rangeSet['new']:
			f.write('new ' + str(len(cmd_range)) + ',' + ','.join(map(str, cmd_range)) +'\n')

		for cmd_range in rangeSet['zero']:
			f.write('zero ' + str(len(cmd_range)) + ',' + ','.join(map(str, cmd_range)) +'\n')


def CompressDatFile(in_name, out_name):
	import imp

	read_size = 2 ** 24
	bc = brotli.Compressor(quality=6, lgwin=24)

	# check which one installed
	if imp.find_module('brotli')[0] == None :
		# brotlipy package
		def compress(uncompress):
			return bc.compress(uncompress)
	else:
		# brotli module
		def compress(uncompress):
			return bc.process(uncompress)

	with open(out_name, 'wb') as out_file:
		with open(in_name, 'rb') as in_file:
			while True:
				data = in_file.read(read_size)
				if not data:
					break

				out_file.write(compress(data))

			out_file.write(bc.finish())


def Compute(args):
	sTime = time.time()

	if args.sha1 == True:
		sha1sum = sha1()

	block_size = 4096
	image_file = args.image
	image_size = os.path.getsize(image_file)

	prefix = args.outdir + os.sep + args.prefix

	fh = GetRawImageFileHandle(image_file, image_size)
	fh.seek(0, 0)

	block_count = int(image_size / block_size)
	ref_zero = '\0'.encode('utf-8') * block_size

	rangeSet = {'new': [], 'zero': []}
	zero_range = 0
	write_blocks = 0
	last_command = ''

	dat = open(prefix + '.new.dat', 'wb')

	for bindex in range(block_count):
		data = fh.read(block_size)

		if data == ref_zero:
			command = 'zero'
			zero_range += 1
		else:
			command = 'new'

			# if zero_block range < 128, merge to 'new' command
			if 0 < zero_range and  zero_range < 128 :
				for r in range(zero_range):
					if args.sha1 == True:
						sha1sum.update(ref_zero)
					dat.write(ref_zero)
				write_blocks += zero_range
				last_command = 'new'
				rangeSet['new'].pop()
				rangeSet['zero'].pop()

			if args.sha1 == True:
				sha1sum.update(data)
			dat.write(data)
			zero_range = 0
			write_blocks += 1

		if command != last_command :
			last_command = command

			if bindex == 0:
				rangeSet['new'].append(bindex)
			else:
				rangeSet['new'].append(bindex)
				rangeSet['zero'].append(bindex)
	else:
		rangeSet[command].append(bindex+1)

	dat.close()
	fh.close()

	WriteTransfers(prefix, args.version, rangeSet, write_blocks, block_count, args.nolimit)

	tTime = time.time() - sTime
	print('')
	print('  转换为分卷的Android数据镜像已完成, 使用 %d seconds' % tTime)

	if args.sha1 == True:
		print('\n  Get sha1 checksums: ' + sha1sum.hexdigest())

	if args.compress == True:
		sTime = time.time()
		CompressDatFile(prefix + '.new.dat', prefix + '.new.dat.br')
		tTime = time.time() - sTime
		print('\n  压缩完成, 使用 %d seconds' % tTime)

	print('')


def main(args):
	if not os.path.isfile(args.image):
		print('raw_image_file 不存在: %s' % args.image)
		sys.exit(2)

	if not os.path.isdir(args.outdir):
		print('outdir 不存在: %s' % args.outdir)
		sys.exit(2)

	if args.sha1 == True:
		global sha1
		from hashlib import sha1

	if args.compress == True:
		if args.version == 4:
			global brotli
			try:
				import brotli
			except ImportError:
				print('Please install brotli (brotli or brotlipy), use:')
				print('  pip install brotli\n  Or\n  pip%d.%d install brotli' % (sys.version_info.major, sys.version_info.minor))
				sys.exit(1)
		else:
			print('仅版本4支持压缩选项')
			sys.exit(1)

	Compute(args)


from argparse import ArgumentParser

parser = ArgumentParser(usage='%(prog)s [OPTION] <raw_image_file>')
parser.add_argument('-o', dest='outdir', metavar='outdir', default=".", help='输出目录，默认：当前目录')
parser.add_argument('-p', dest='prefix', metavar='prefix', default="system", help='分卷数据映像的名称（prefix.new.dat），默认: system')
parser.add_argument('-v', dest='version', metavar='version', default=4, type=int, choices=range(1,5), help='transfer 列出版本号, default: 4')
parser.add_argument('-c', dest='compress', action='store_true', default=False, help='使用brotli将new.dat文件压缩为new.dat.br文件。 （警告！仅支持Android 8.1）')
parser.add_argument('-nl', dest='nolimit', action='store_true', default=False, help='当版本为4时，单个命令中没有限制1024个块')
parser.add_argument('-sha1', dest='sha1', action='store_true', default=False, help='获取分卷数据镜像的sha1校验和')
parser.add_argument('image', metavar='raw_image_file', help='输入 system 原镜像文件')


if __name__ == '__main__':
	# as cli
	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit()
	else:
		args = parser.parse_args()

	main(args)
	
else:
	# as module
	def process(image, option=''):
		options = str(option).split()
		options.append(image)

		args = parser.parse_args(options)
		main(args)
