#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#          FILE:  simg2img.py
# 
#         USAGE:  ./simg2img.py system.img 
# 
#   DESCRIPTION:  
# 
#        AUTHOR: Karl Zheng 
#       COMPANY: Meizu
#       CREATED: 2011年10月18日 15时25分15秒 CST
#      REVISION:  ---
#        MODIFY: AEnjoy
#===============================================================================

from __future__ import print_function
import os
import sys
import struct

EXT4_FILE_HEADER_MAGIC = 0xED26FF3A
EXT4_CHUNK_HEADER_SIZE = 12

class ext4_file_header(object):
    def __init__(self, buf):
        (self.magic, 
            self.major, 
            self.minor, 
            self.file_header_size, 
            self.chunk_header_size, 
            self.block_size, 
            self.total_blocks, 
            self.total_chunks, 
            self.crc32) = struct.unpack('<I4H4I', buf)

class ext4_chunk_header(object):
    def __init__(self, buf):
        (self.type,
            self.reserved,
            self.chunk_size,
            self.total_size) = struct.unpack('<2H2I', buf)

def main(file,outfile=''):
    with open(file, "rb") as ifd:

        print("file size: %d" % os.stat(file).st_size)

        file_header = ext4_file_header(ifd.read(28))

        if file_header.magic != EXT4_FILE_HEADER_MAGIC:
            print("Not a compressed ext4 file!!")
            sys.exit(3)

        print("file_header chunks:%X" % file_header.total_chunks)

        total_chunks = file_header.total_chunks
        print("total chunk = %d " % total_chunks)
        outfile=file.replace(".img", "output.img")
        with open(outfile, "wb") as ofd:
            sector_base = 82528
            output_len = 0

            while total_chunks > 0:
                chunk_header = ext4_chunk_header(ifd.read(EXT4_CHUNK_HEADER_SIZE))
                sector_size = (chunk_header.chunk_size * file_header.block_size) >> 9
                #print("ct:%X, cs:%X, ts:%X, ss:%X"%(chunk_header.type, chunk_header.chunk_size, chunk_header.total_size, sector_size))

                if chunk_header.type == 0xCAC1:  # raw type 
                    data = ifd.read(chunk_header.total_size - EXT4_CHUNK_HEADER_SIZE)
                    len_data = len(data)
                    if len_data != (sector_size << 9):
                        print("len data:%d, sector_size:%d" % (len_data, sector_size << 9))
                        sys.exit(4)
                    else:
                        print("len data:%d, sector_size:%d" % (len_data, sector_size << 9))
                        ofd.write(data)
                        print("raw_chunk ")
                        print("write raw data in %d size %d \n" % (sector_base, sector_size))
                        print("output len:%x" % (output_len + len_data))
                else:
                    len_data = sector_size << 9
                    if chunk_header.type == 0xCAC2:  # TYPE_FILL
                        print("fill_chunk \n")
                        print("chunk_size:%x" % chunk_header.chunk_size)
                        print("output len:%x" % (output_len + len_data))
                    else:
                        if chunk_header.type == 0xCAC3:  # TYPE_DONT_CARE
                            print("none chunk at chunk:%d" % (file_header.total_chunks - total_chunks))
                            print("data_size:0x%x, chunk_size:%d, block_size:%d" % (len_data, 
                                chunk_header.chunk_size, file_header.block_size))
                        else:
                            print("unknown type!!")
                            print("output len:%x" % (output_len + len_data))
                            
                    ofd.write(struct.pack("B", 0) * len_data) 
                output_len += len_data
                sector_base += sector_size   

                total_chunks -= 1 
                print("remain chunks = %d "% total_chunks)

            print("write done")
        return 0
    
if __name__ == "__main__":
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        main(sys.argv[1])
    else:
        print("required existing input file")
        sys.exit(1)
    
