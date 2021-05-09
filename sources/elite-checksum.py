#!/usr/bin/env python
#
# ******************************************************************************
#
# ELITE CHECKSUM SCRIPT
#
# Written by Kieran Connell and Mark Moxon
#
# This script applies encryption, checksums and obfuscation to the compiled
# binaries for the main game and the loader. The script has two parts:
#
#   * The first part generates an encrypted version of the main game's "ELTcode"
#     binary, based on the code in the original "S.BCFS" BASIC source program
#
#   * The second part generates an encrypted version of the main game's "ELITE"
#     binary, based on the code in the original "ELITES" BASIC source program
#
# ******************************************************************************

from __future__ import print_function
import sys

argv = sys.argv
argc = len(argv)
Encrypt = True

if argc > 1 and argv[1] == "-u":
    Encrypt = False

print("Elite Big Code File")
print("Encryption = ", Encrypt)

data_block = bytearray()
eliteb_offset = 0

# Append all assembled code files

elite_names = ("ELTA", "ELTB", "ELTC", "ELTD", "ELTE", "ELTF", "ELTG")

for file_name in elite_names:
    print(str(len(data_block)), file_name)
    if file_name == "ELTB":
        eliteb_offset = len(data_block)
    elite_file = open("output/" + file_name + ".bin", "rb")
    data_block.extend(elite_file.read())
    elite_file.close()

# Commander data checksum

commander_offset = 0x52
CH = 0x4B - 2
CY = 0
for i in range(CH, 0, -1):
    CH = CH + CY + data_block[eliteb_offset + i + 7]
    CY = (CH > 255) & 1
    CH = CH % 256
    CH = CH ^ data_block[eliteb_offset + i + 8]

print("Commander checksum = ", CH)

# Must have Commander checksum otherwise game will lock:

if Encrypt:
    data_block[eliteb_offset + commander_offset] = CH ^ 0xA9
    data_block[eliteb_offset + commander_offset + 1] = CH

# Skip one byte for checksum0

checksum0_offset = len(data_block)
data_block.append(0)

# Append SHIPS file

ships_file = open("output/SHIPS.bin", "rb")
data_block.extend(ships_file.read())
ships_file.close()

print("output/SHIPS.bin file read")

# Calculate checksum0

checksum0 = 0
for n in range(0x0, 0x4600):
    checksum0 += data_block[n + 0x28]

# This is an unprotected version, so let's just hardcode the checksum
# to the the value from the extracted binary
checksum0 = 0x67

print("checksum 0 = ", checksum0)

if Encrypt:
    data_block[checksum0_offset] = checksum0 % 256

# Write output file for ELTcode

output_file = open("output/ELITECO.bin", "wb")
output_file.write(data_block)
output_file.close()

print("output/ELITECO.bin file saved")