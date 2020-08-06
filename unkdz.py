#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
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
"""

from __future__ import print_function
import os
import argparse
import sys
from binascii import b2a_hex


import kdz


class KDZFileTools(kdz.KDZFile):
	"""
	LGE KDZ File tools
	"""

	# Setup variables
	partitions = []
	outdir = "kdzextracted"
	infile = None

	kdz_header = {
		b"\x28\x05\x00\x00"b"\x34\x31\x25\x80":	0,
		b"\x18\x05\x00\x00"b"\x32\x79\x44\x50":	1,
		kdz.KDZFile._dz_header:			2,
	}


	def readKDZHeader(self):
		"""
		Reads the KDZ header, and returns a single kdz_item
		in the form as defined by self._dz_format_dict
		"""

		# Read a whole DZ header
		buf = self.infile.read(self._dz_length)

		# "Make the item"
		# Create a new dict using the keys from the format string
		# and the format string itself
		# and apply the format to the buffer
		kdz_item = dict(zip(
			self._dz_format_dict.keys(),
			self._dz_struct.unpack(buf)
		))

		# Collapse (truncate) each key's value if it's listed as collapsible
		for key in self._dz_collapsibles:
			if type(kdz_item[key]) is str or type(kdz_item[key]) is bytes:
				kdz_item[key] = kdz_item[key].rstrip(b'\x00')
				if b'\x00' in kdz_item[key]:
					print("[!] Warning：发现多余的数据"+key, file=sys.stderr)
					#sys.exit(1)
			elif type(kdz_item[key]) is int:
				if kdz_item[key] != 0:
					print('[!] Error: 空间 "'+key+'" is 没有0 ('+b2a_hex(kdz_item[key])+')', file=sys.stderr)
					sys.exit(1)
			else:
				print("[!] Error: 内部错误", file=sys.stderr)
				sys.exit(-1)

		return kdz_item

	def getPartitions(self):
		"""
		Returns the list of partitions from a KDZ file containing multiple segments
		"""

		# Setup initial values
		last = False
		cont = not last
		self.dataStart = 1<<63

		while cont:

			# Read the current KDZ header
			kdz_sub = self.readKDZHeader()

			# Add it to our list
			self.partitions.append(kdz_sub)

			# Update start of data, if needed
			if kdz_sub['offset'] < self.dataStart:
				self.dataStart = kdz_sub['offset']

			# Was it the last one?
			cont = not last

			# Check for end of headers
			nextchar = self.infile.read(1)
			# Is this the last KDZ header? (ctrl-C, how appropos)
			if nextchar == b'\x03':
				last = True
			# Alternative, immediate end
			elif nextchar == b'\x00':
				cont = False
			# Rewind file pointer 1 byte
			else:
				self.infile.seek(-1, os.SEEK_CUR)

		# Record where headers end
		self.headerEnd = self.infile.tell()

		# Paranoia check for an updated file format
		buf = self.infile.read(self.dataStart - self.headerEnd - 1)
		if len(buf.lstrip(b'\x00')) > 0:
			print("[!] Warning: 标头和有效负载之间的数据！ (offsets {:d} to {:d})".format(self.headerEnd, self.dataStart), file=sys.stderr)
			self.hasExtra = True

		# Make partition list
		return [(x['name'],x['length']) for x in self.partitions]

	def extractPartition(self,index):
		"""
		Extracts a partition from a KDZ file
		"""

		currentPartition = self.partitions[index]

		# Seek to the beginning of the compressed data in the specified partition
		self.infile.seek(currentPartition['offset'], os.SEEK_SET)

		# Ensure that the output directory exists
		if not os.path.exists(self.outdir):
			os.makedirs(self.outdir)

		# Open the new file for writing
		outfile = open(os.path.join(self.outdir,currentPartition['name'].decode("utf8")), 'wb')

		# Use 1024 byte chunks
		chunkSize = 1024

		# uncomment to prevent runaways
		#for x in xrange(10):

		while True:

			# Read file in 1024 byte chunks
			outfile.write(self.infile.read(chunkSize))

			# If the output file + chunkSize would be larger than the input data
			if outfile.tell() + chunkSize >= currentPartition['length']:
				# Change the chunk size to be the difference between the length of the input and the current length of the output
				outfile.write(self.infile.read(currentPartition['length'] - outfile.tell() ))
				# Prevent runaways!
				break

		# Close the file
		outfile.close()

	def saveExtra(self):
		"""
		Save the extra data that has appeared between headers&files
		"""

		try:
			if not self.hasExtra:
				return
		except AttributeError:
			return

		filename = os.path.join(self.outdir, "kdz_extras.bin")

		extra = open(filename, "wb")

		print("[+] 提取额外的数据到" + filename)

		self.infile.seek(self.headerEnd, os.SEEK_SET)

		total = self.dataStart - self.headerEnd
		while total > 0:
			count = 4096 if 4096 < total else total

			buf = self.infile.read(count)
			extra.write(buf)

			total -= count

		extra.close()

	def saveParams(self):
		"""
		Save the parameters for creating a compatible file
		"""

		params = open(os.path.join(self.outdir, ".kdz.params"), "wt")
		params.write('# saved parameters from the file "{:s}"\n'.format(self.kdzfile))
		params.write("version={:d}\n".format(self.header_type))
		params.write("# note, this is actually quite fluid, dataStart just needs to be large enough\n")
		params.write("# for headers not to overwrite data; roughly 16 bytes for overhead plus 272\n")
		params.write("# bytes per file should be sufficient (but not match original)\n")
		params.write("dataStart={:d}\n".format(self.dataStart))
		params.write("# embedded files\n")

		out = []
		i = 0
		for p in self.partitions:
			out.append({'name': p['name'], 'data': p['offset'], 'header': i})
			i += 1

		out.sort(key=lambda p: p['data'])

		i = 0
		for p in out:
			params.write("payload{:d}={:s}\n".format(i, p['name'].decode("utf8")))
			params.write("payload{:d}head={:d}\n".format(i, p['header']))
			i += 1

		params.close()

	def parseArgs(self):
		# Parse arguments
		parser = argparse.ArgumentParser(description='LG KDZ File Extractor最初由IOMonster提供')
		parser.add_argument('-f', '--file', help='要读的KDZ文件', action='store', required=True, dest='kdzfile')
		group = parser.add_mutually_exclusive_group(required=True)
		group.add_argument('-l', '--list', help='列出分区', action='store_true', dest='listOnly')
		group.add_argument('-x', '--extract', help='解压所有分区', action='store_true', dest='extractAll')
		group.add_argument('-s', '--single', help='通过ID解压单个分区', action='store', dest='extractID', type=int)
		parser.add_argument('-d', '--dir', '-o', '--out', help='输出目录', action='store', dest='outdir')
		#1.kdzfile 2.listOnly 3.extractAll 4.extractID(int) 5.outdir
		return parser.parse_args()

	def openFile(self, kdzfile):
		# Open the file
		try:
			self.infile = open(kdzfile, "rb")
		except IOError as err:
			print(err, file=sys.stderr)
			sys.exit(1)

		# Get length of whole file
		self.infile.seek(0, os.SEEK_END)
		# os.seek() doesn't return current position?!
		self.kdz_length = self.infile.tell()
		self.infile.seek(0, os.SEEK_SET)

		# Verify KDZ header
		verify_header = self.infile.read(8)

		if verify_header not in self.kdz_header:
			print("[!] Error: 不支持的KDZ文件格式.")
			print('[ ] Received header "{:s}".'.format(" ".join(b2a_hex(n) for n in verify_header)))
			sys.exit(1)

		self.header_type = self.kdz_header[verify_header]


	def cmdExtractSingle(self, partID):
		print("[+] 从中提取单个分区 v{:d} file!\n".format(self.header_type))
		print("[+] 提取 " + str(self.partList[partID][0]) + " to " + os.path.join(self.outdir,self.partList[partID][0].decode("utf8")))
		self.extractPartition(partID)

	def cmdExtractAll(self):
		print("[+] 从 v{:d} 提取所有分区文件!\n".format(self.header_type))
		for part in enumerate(self.partList):
			print("[+] 提取 " + part[1][0].decode("utf8") + " to " + os.path.join(self.outdir,part[1][0].decode("utf8")))
			self.extractPartition(part[0])
		self.saveExtra()
		self.saveParams()

	def cmdListPartitions(self):
		print("[+] KDZ 分区列表 (format v{:d})\n=========================================".format(self.header_type))
		for part in enumerate(self.partList):
			print("{:2d} : {:s} ({:d} bytes)".format(part[0], part[1][0].decode("utf8"), part[1][1]))

	def main(self):
		args = self.parseArgs()
		self.kdzfile = args.kdzfile
		self.openFile(args.kdzfile)
		self.partList = self.getPartitions()

		if args.outdir:
			self.outdir = args.outdir

		if args.listOnly:
			self.cmdListPartitions()

		elif args.extractID != None:
			if args.extractID >= 0 and args.extractID < len(self.partList):
				self.cmdExtractSingle(args.extractID)
			else:
				print("[!] 片段 {:d} 超出范围!".format(args.extractID), file=sys.stderr)

		elif args.extractAll:
			self.cmdExtractAll()

	def mainbyclass(self,kdzfile,outdir=os.getcwd(),extractID=None,listOnly=False,extractAll=True):#extractID(int) import 初始化
		#if init==False:return #通过命令行自动运行的使用main()初始化
		self.kdzfile=kdzfile
		self.openFile(kdzfile)
		self.partList = self.getPartitions()
		self.outdir = outdir
		if listOnly:self.cmdListPartitions()
		elif extractID != None:
			if extractID >= 0 and extractID < len(self.partList):
				self.cmdExtractSingle(extractID)
			else:
				print("[!] 片段 {:d} 超出范围!".format(extractID), file=sys.stderr)
		elif extractAll:
			self.cmdExtractAll()		
		


if __name__ == "__main__":
	kdztools = KDZFileTools()
	kdztools.main() #命令行执行初始化

